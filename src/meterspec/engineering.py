from __future__ import annotations

import math

from .catalog import ct_sizes, products
from .models import ApplicationInput, MeterProduct


def parse_ratio(value: str | None) -> tuple[int, str] | None:
    if not value or ":" not in value:
        return None
    primary, secondary = value.split(":", 1)
    return int(primary.strip()), secondary.strip()


def validate_input(app: ApplicationInput) -> dict:
    findings: list[dict] = []
    if app.maximum_current <= 0:
        findings.append({"level": "HARD REQUIREMENT", "message": "Maximum current must be positive."})
    if app.continuous_current and app.continuous_current > app.maximum_current:
        findings.append({"level": "WARNING", "message": "Continuous current is higher than maximum expected current."})
    if app.connection_type == "CT-operated" and not app.ct_secondary:
        findings.append({"level": "HARD REQUIREMENT", "message": "CT-operated applications require a CT secondary selection."})
    if app.existing_ct and parse_ratio(app.existing_ct_ratio) is None:
        findings.append({"level": "NEEDS CLARIFICATION", "message": "Existing CT was selected but a valid ratio was not provided."})
    if app.frequency not in {50, 60}:
        findings.append({"level": "ENGINEERING REVIEW", "message": "Frequency outside the sample catalog's normal 50/60 Hz assumptions."})
    status = "VALID"
    if any(f["level"] == "HARD REQUIREMENT" for f in findings):
        status = "NEEDS CLARIFICATION"
    elif any(f["level"] == "ENGINEERING REVIEW" for f in findings):
        status = "ENGINEERING REVIEW REQUIRED"
    return {"status": status, "findings": findings}


def size_ct(app: ApplicationInput) -> dict:
    load = app.continuous_current or app.maximum_current * 0.75
    target = max(app.maximum_current, load)
    selected = next((size for size in ct_sizes() if size >= target), ct_sizes()[-1])
    utilization = load / selected
    margin = selected - app.maximum_current
    result = {
        "expected_load": round(load, 1),
        "recommended_ratio": f"{selected}:{app.ct_secondary.replace('A', '')}",
        "utilization": round(utilization * 100, 1),
        "margin_amps": round(margin, 1),
        "status": "SUITABLE" if selected >= app.maximum_current else "REQUIRES ENGINEERING REVIEW",
        "reason": "Selected the smallest configured CT primary rating that is not below the expected maximum current.",
    }
    if app.existing_ct:
        parsed = parse_ratio(app.existing_ct_ratio)
        if parsed:
            primary, secondary = parsed
            result["existing_ratio"] = app.existing_ct_ratio
            result["existing_status"] = "SUITABLE" if primary >= app.maximum_current and secondary == app.ct_secondary.replace("A", "") else "NOT SUITABLE"
            result["existing_reason"] = "Existing CT primary is below expected maximum current." if primary < app.maximum_current else "Existing CT secondary or catalog support should be checked."
    return result


def pt_requirement(app: ApplicationInput, compatible_voltage_limit: float | None = None) -> dict:
    max_direct = compatible_voltage_limit or max(p.voltage_max for p in products())
    required = app.pt_required_by_customer or app.nominal_voltage > max_direct
    return {
        "required": required,
        "status": "PT REQUIRED" if required else "DIRECT VOLTAGE SUPPORTED",
        "reason": "Based on the selected fictional catalog voltage-input limits and the customer PT preference.",
        "catalog_direct_limit": max_direct,
    }


def hard_filter(app: ApplicationInput, product: MeterProduct) -> tuple[bool, list[str]]:
    reasons = []
    if not (product.voltage_min <= app.nominal_voltage <= product.voltage_max):
        reasons.append(f"Voltage {app.nominal_voltage:g} V is outside {product.voltage_min:g}-{product.voltage_max:g} V.")
    if app.wiring not in product.wirings:
        reasons.append(f"Wiring {app.wiring} is not supported.")
    if app.connection_type == "CT-operated" and app.ct_secondary not in product.ct_inputs:
        reasons.append(f"CT secondary {app.ct_secondary} is not supported.")
    if app.protocol not in product.protocols and app.protocol != "No communications":
        reasons.append(f"Protocol {app.protocol} is not supported.")
    missing = [m for m in app.monitoring if m not in product.measurements]
    if missing:
        reasons.append("Missing required measurements: " + ", ".join(missing) + ".")
    if app.environment not in product.mounting:
        reasons.append(f"Mounting/environment {app.environment} is not listed for this product.")
    return not reasons, reasons


def score_product(app: ApplicationInput, product: MeterProduct) -> int:
    score = 60
    score += 10 if product.logging and "Data logging" in app.monitoring else 0
    score += 10 if product.power_quality and "Power Quality indicators" in app.monitoring else 0
    score += 8 if app.protocol in product.protocols else 0
    score += 6 if app.environment in product.mounting else 0
    score += max(0, 6 - math.ceil((product.voltage_max - app.nominal_voltage) / 200))
    return min(score, 100)


def communication_architecture(app: ApplicationInput) -> dict:
    if app.protocol == "Modbus TCP":
        path = ["Meter", "Ethernet switch", "Customer LAN", "Energy management system"]
        notes = "Assign a static IP or reserved DHCP address and document unit/device identifiers."
    elif app.protocol in {"Modbus RTU", "RS-485"}:
        path = ["Meter", "RS-485 trunk", "Gateway or data logger", "Ethernet", "BMS/EMS"]
        notes = "Confirm baud rate, parity, stop bits, termination, biasing, and unique device ID."
    elif app.protocol == "BACnet/IP":
        path = ["Meter", "Ethernet switch", "BACnet/IP network", "BMS"]
        notes = "Coordinate device instance, network number, and point naming with the BMS team."
    elif app.protocol == "Pulse":
        path = ["Meter pulse output", "Pulse input module", "Data logger"]
        notes = "Confirm pulse weight and input debounce settings."
    else:
        path = ["Local meter display", "Manual read or future integration"]
        notes = "No communication equipment is required by the current requirement."
    return {"protocol": app.protocol, "path": path, "notes": notes}


def select_solution(app: ApplicationInput) -> dict:
    validation = validate_input(app)
    ct = size_ct(app)
    compatible = []
    excluded = []
    for product in products():
        ok, reasons = hard_filter(app, product)
        if ok:
            compatible.append({"product": product, "score": score_product(app, product), "why": f"Supports {app.wiring}, {app.nominal_voltage:g} V, {app.ct_secondary} CT input, {app.protocol}, and requested measurements."})
        else:
            excluded.append({"product": product.name, "reasons": reasons})
    compatible.sort(key=lambda item: item["score"], reverse=True)
    recommended = compatible[0] if compatible else None
    alternative = compatible[1] if len(compatible) > 1 else None
    voltage_limit = recommended["product"].voltage_max if recommended else None
    return {
        "status": validation["status"] if compatible else "ENGINEERING REVIEW REQUIRED",
        "application": app.model_dump(),
        "validation": validation,
        "ct": ct,
        "pt": pt_requirement(app, voltage_limit),
        "recommended": _pack(recommended),
        "alternative": _pack(alternative),
        "compatible": [_pack(item) for item in compatible],
        "excluded": excluded,
        "architecture": communication_architecture(app),
        "open_questions": open_questions(app, compatible),
        "notes": ["Selections use hard electrical/protocol filtering before scoring.", "Actual procurement must be checked against manufacturer documentation."],
    }


def _pack(item: dict | None) -> dict | None:
    if not item:
        return None
    product: MeterProduct = item["product"]
    return {"name": product.name, "score": item["score"], "why": item["why"], "spec": product.model_dump()}


def open_questions(app: ApplicationInput, compatible: list[dict]) -> list[str]:
    questions = []
    if app.pt_required_by_customer:
        questions.append("Confirm PT ratio and secondary voltage with the electrical design package.")
    if app.existing_ct and size_ct(app).get("existing_status") == "NOT SUITABLE":
        questions.append("Existing CT appears undersized or incompatible; confirm available CT cabinet space.")
    if not compatible:
        questions.append("No fictional catalog product met every hard requirement; engineering review required.")
    return questions
