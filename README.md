# MeterSpec

Electrical Meter Selection & Sizing Tool.

MeterSpec is a focused application-engineering tool for turning customer metering requirements into a defensible meter and CT recommendation. It uses deterministic validation, CT sizing, PT assessment, product compatibility filtering, communication architecture generation, comparison, and a downloadable technical report.

The product catalog is fictional and included only for demonstration. This project is not affiliated with any meter manufacturer.

## Live Demo

Live demo: deployment pending.

## Screenshots

Current screenshots are captured from the running application and stored in `screenshots/`.

- [Customer requirements wizard](screenshots/wizard.png)
- [Fictional product catalog](screenshots/catalog.png)
- [Meter comparison](screenshots/compare.png)

## Problem

Metering applications often fail because the basic fit checks are scattered across emails, spec sheets, and tribal knowledge. MeterSpec puts the repeatable checks in one tool so the application engineer can explain why a meter is selected, why another is excluded, and where engineering review is still required.

## Engineering Workflow

Customer requirements -> electrical validation -> CT sizing -> PT logic -> hard product filtering -> deterministic ranking -> communication architecture -> technical report.

## Features

- Step-by-step customer requirements wizard
- Engineering validation with hard requirements, warnings, and review flags
- Deterministic CT sizing using configured standard ratios
- Existing CT suitability checks
- PT requirement logic based on fictional catalog input limits
- Hard filtering for voltage, wiring, CT input, protocol, mounting, and measurements
- Recommended and alternative meter ranking
- Excluded-product reasoning
- Communication architecture generation
- Product comparison view
- Downloadable HTML technical report
- FastAPI JSON APIs and Swagger docs

## Example Scenarios

- Commercial Facility: 600 V, 3P4W, 1200 A, Modbus TCP, logging.
- Industrial Retrofit: 480 V, 3P3W, 800 A with existing 600:5 CT, Modbus RTU. This correctly flags the existing CT as undersized.
- Small Commercial Panel: 208/120 V, 3P4W, 200 A, Ethernet, basic metering.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
uvicorn web.main:app --host 0.0.0.0 --port 8000
```

## Docker

```powershell
docker compose up --build
```

## Testing

```powershell
pytest -q
python -m compileall src web
```

## API

- `GET /api/catalog`
- `POST /api/validation`
- `POST /api/ct-sizing`
- `POST /api/selection`
- `GET /api/scenarios/{scenario}/selection`
- `GET /api/reports/{scenario}`

## Documentation

- [Architecture](docs/architecture.md)
- [Engineering Rules](docs/engineering-rules.md)
- [Architecture Diagram](diagrams/architecture.mmd)

## Limitations

- The product catalog is fictional and intentionally small.
- The tool does not make electrical-code determinations.
- Results must be validated against actual manufacturer documentation before procurement or installation.
- Reports are downloadable HTML for simple free hosting.
