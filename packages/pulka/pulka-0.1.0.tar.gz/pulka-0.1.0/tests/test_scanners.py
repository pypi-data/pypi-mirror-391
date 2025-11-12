from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from pulka.core.engine.contracts import EnginePayloadHandle
from pulka.core.engine.polars_adapter import POLARS_ENGINE, unwrap_physical_plan
from pulka.data.scanners import ScannerRegistry


def test_scanner_registry_wraps_lazyframe(tmp_path: Path) -> None:
    registry = ScannerRegistry()

    def _scan(_path: Path) -> pl.LazyFrame:
        return pl.DataFrame({"value": [1, 2, 3]}).lazy()

    registry.register_scanner(".foo", _scan)

    target = tmp_path / "example.foo"
    target.write_bytes(b"")

    physical_plan = registry.scan(target)

    assert isinstance(physical_plan, EnginePayloadHandle)
    assert physical_plan.as_serializable() == {
        "engine": POLARS_ENGINE,
        "kind": "physical_plan",
    }

    polars_plan = unwrap_physical_plan(physical_plan)
    assert polars_plan.to_lazyframe().collect().to_dict(as_series=False) == {"value": [1, 2, 3]}


def test_scanner_registry_rejects_unknown_payload(tmp_path: Path) -> None:
    registry = ScannerRegistry()

    class _WeirdPlan:
        pass

    def _scan(_path: Path) -> _WeirdPlan:
        return _WeirdPlan()

    registry.register_scanner(".bar", _scan)

    with pytest.raises(TypeError, match="unsupported plan type: _WeirdPlan"):
        registry.scan(tmp_path / "example.bar")
