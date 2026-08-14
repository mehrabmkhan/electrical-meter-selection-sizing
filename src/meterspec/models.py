from __future__ import annotations

from pydantic import BaseModel, Field


class ApplicationInput(BaseModel):
    application_name: str = "Commercial Facility"
    facility_type: str = "Commercial"
    system: str = "Three-phase"
    wiring: str = "3P4W"
    nominal_voltage: float = 600
    frequency: float = 60
    maximum_current: float = Field(default=1200, gt=0)
    continuous_current: float | None = 900
    metering_points: int = Field(default=1, ge=1)
    connection_type: str = "CT-operated"
    ct_type: str = "split-core"
    ct_secondary: str = "5A"
    existing_ct: bool = False
    existing_ct_ratio: str | None = None
    pt_required_by_customer: bool = False
    protocol: str = "Modbus TCP"
    monitoring: list[str] = Field(default_factory=lambda: ["Voltage", "Current", "kW", "PF", "Frequency", "kWh", "Demand", "Data logging"])
    environment: str = "Switchboard"


class MeterProduct(BaseModel):
    name: str
    voltage_min: float
    voltage_max: float
    wirings: list[str]
    ct_inputs: list[str]
    protocols: list[str]
    measurements: list[str]
    demand: bool
    logging: bool
    power_quality: bool
    mounting: list[str]
    use_case: str
