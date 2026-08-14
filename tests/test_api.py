from fastapi.testclient import TestClient

from meterspec.models import ApplicationInput
from web.main import app


def test_catalog_api():
    client = TestClient(app)
    response = client.get("/api/catalog")
    assert response.status_code == 200
    assert len(response.json()["meters"]) >= 4


def test_selection_api_returns_reportable_solution():
    client = TestClient(app)
    response = client.post("/api/selection", json=ApplicationInput().model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data["recommended"]["name"]
    assert data["architecture"]["path"]


def test_industrial_retrofit_api_flags_existing_ct():
    client = TestClient(app)
    response = client.get("/api/scenarios/industrial_retrofit/selection")
    assert response.status_code == 200
    assert response.json()["ct"]["existing_status"] == "NOT SUITABLE"


def test_report_downloads_html():
    client = TestClient(app)
    response = client.get("/reports/commercial_facility.html")
    assert response.status_code == 200
    assert "MeterSpec Electrical Meter Selection" in response.text
