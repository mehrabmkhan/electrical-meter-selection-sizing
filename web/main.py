from __future__ import annotations

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

from meterspec.catalog import load_catalog, products
from meterspec.engineering import select_solution, size_ct, validate_input
from meterspec.models import ApplicationInput
from meterspec.report import render_report
from meterspec.scenarios import SCENARIOS


templates = Jinja2Templates(directory="web/templates")
app = FastAPI(title="MeterSpec", version="1.0.0")


def input_from_form(**data) -> ApplicationInput:
    monitoring = data.pop("monitoring", [])
    if isinstance(monitoring, str):
        monitoring = [monitoring]
    data["monitoring"] = monitoring or ["Voltage", "Current", "kW", "PF", "Frequency", "kWh"]
    data["existing_ct"] = bool(data.get("existing_ct"))
    data["pt_required_by_customer"] = bool(data.get("pt_required_by_customer"))
    return ApplicationInput(**data)


@app.get("/", response_class=HTMLResponse)
def home(request: Request, scenario: str = "commercial_facility") -> HTMLResponse:
    app_input = SCENARIOS.get(scenario, SCENARIOS["commercial_facility"])
    solution = select_solution(app_input)
    return templates.TemplateResponse(request, "wizard.html", {"input": app_input, "solution": solution, "scenarios": SCENARIOS, "catalog": products()})


@app.post("/selection", response_class=HTMLResponse)
def selection(
    request: Request,
    application_name: str = Form(...),
    facility_type: str = Form(...),
    system: str = Form(...),
    wiring: str = Form(...),
    nominal_voltage: float = Form(...),
    frequency: float = Form(...),
    maximum_current: float = Form(...),
    continuous_current: float | None = Form(None),
    metering_points: int = Form(...),
    connection_type: str = Form(...),
    ct_type: str = Form(...),
    ct_secondary: str = Form(...),
    existing_ct_ratio: str | None = Form(None),
    protocol: str = Form(...),
    environment: str = Form(...),
    monitoring: list[str] = Form(default=[]),
    existing_ct: str | None = Form(None),
    pt_required_by_customer: str | None = Form(None),
) -> HTMLResponse:
    app_input = input_from_form(**locals())
    solution = select_solution(app_input)
    return templates.TemplateResponse(request, "results.html", {"input": app_input, "solution": solution, "catalog": products()})


@app.get("/catalog", response_class=HTMLResponse)
def catalog_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "catalog.html", {"catalog": products(), "notice": load_catalog()["notice"]})


@app.get("/compare", response_class=HTMLResponse)
def compare(request: Request, scenario: str = "commercial_facility") -> HTMLResponse:
    solution = select_solution(SCENARIOS.get(scenario, SCENARIOS["commercial_facility"]))
    return templates.TemplateResponse(request, "compare.html", {"solution": solution})


@app.get("/rules", response_class=HTMLResponse)
def rules(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "rules.html")


@app.get("/reports/{scenario}.html")
def report(scenario: str = "commercial_facility") -> Response:
    solution = select_solution(SCENARIOS.get(scenario, SCENARIOS["commercial_facility"]))
    return Response(render_report(solution), media_type="text/html", headers={"Content-Disposition": f"attachment; filename=meterspec_{scenario}.html"})


@app.get("/api/catalog")
def api_catalog() -> dict:
    return load_catalog()


@app.post("/api/validation")
def api_validation(app_input: ApplicationInput) -> dict:
    return validate_input(app_input)


@app.post("/api/ct-sizing")
def api_ct(app_input: ApplicationInput) -> dict:
    return size_ct(app_input)


@app.post("/api/selection")
def api_selection(app_input: ApplicationInput) -> dict:
    return select_solution(app_input)


@app.get("/api/scenarios/{scenario}/selection")
def api_scenario_selection(scenario: str) -> dict:
    return select_solution(SCENARIOS.get(scenario, SCENARIOS["commercial_facility"]))


@app.get("/api/reports/{scenario}")
def api_report(scenario: str = "commercial_facility") -> dict:
    return {"path": f"/reports/{scenario}.html"}
