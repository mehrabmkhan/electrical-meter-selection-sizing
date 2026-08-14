from __future__ import annotations

from pathlib import Path

import yaml

from .models import MeterProduct


def load_catalog(path: str | Path = "data/catalog.yaml") -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def products() -> list[MeterProduct]:
    return [MeterProduct(**item) for item in load_catalog()["meters"]]


def ct_sizes() -> list[int]:
    return list(load_catalog()["standard_ct_primaries"])
