from __future__ import annotations

from .models import ApplicationInput


SCENARIOS = {
    "commercial_facility": ApplicationInput(),
    "industrial_retrofit": ApplicationInput(
        application_name="Industrial Retrofit",
        facility_type="Industrial",
        wiring="3P3W",
        nominal_voltage=480,
        maximum_current=800,
        continuous_current=620,
        existing_ct=True,
        existing_ct_ratio="600:5",
        protocol="Modbus RTU",
        monitoring=["Voltage", "Current", "kW", "kVA", "kvar", "PF", "Frequency", "kWh", "Demand"],
        environment="Retrofit",
    ),
    "small_commercial_panel": ApplicationInput(
        application_name="Small Commercial Panel",
        facility_type="Small commercial",
        wiring="3P4W",
        nominal_voltage=208,
        maximum_current=200,
        continuous_current=150,
        protocol="Ethernet",
        monitoring=["Voltage", "Current", "kW", "PF", "Frequency", "kWh"],
        environment="Panel",
    ),
}
