from meterspec.engineering import hard_filter, pt_requirement, select_solution, size_ct
from meterspec.models import ApplicationInput, MeterProduct
from meterspec.scenarios import SCENARIOS


def test_ct_sizing_selects_smallest_suitable_standard_ratio():
    result = size_ct(ApplicationInput(maximum_current=801, continuous_current=700))
    assert result["recommended_ratio"] == "1000:5"
    assert result["status"] == "SUITABLE"


def test_existing_ct_undersized_is_not_suitable():
    result = size_ct(SCENARIOS["industrial_retrofit"])
    assert result["existing_status"] == "NOT SUITABLE"


def test_pt_logic_uses_catalog_voltage_limit():
    result = pt_requirement(ApplicationInput(nominal_voltage=800), compatible_voltage_limit=690)
    assert result["required"] is True


def test_hard_filter_blocks_unsupported_protocol():
    product = MeterProduct(name="Demo", voltage_min=90, voltage_max=600, wirings=["3P4W"], ct_inputs=["5A"], protocols=["Pulse"], measurements=["Voltage", "Current"], demand=False, logging=False, power_quality=False, mounting=["Panel"], use_case="Demo")
    ok, reasons = hard_filter(ApplicationInput(protocol="Modbus TCP", monitoring=["Voltage"]), product)
    assert ok is False
    assert any("Protocol" in reason for reason in reasons)


def test_selection_recommends_network_meter_for_commercial_facility():
    solution = select_solution(SCENARIOS["commercial_facility"])
    assert solution["recommended"]["name"] in {"MeterSpec M300", "MeterSpec PQ500"}
    assert solution["excluded"]


def test_power_quality_requirement_filters_to_pq_meter():
    app = ApplicationInput(monitoring=["Voltage", "Current", "kW", "kWh", "Power Quality indicators"], protocol="Modbus TCP")
    solution = select_solution(app)
    assert solution["recommended"]["name"] == "MeterSpec PQ500"
