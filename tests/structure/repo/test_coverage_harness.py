from __future__ import annotations

import tomllib

from tests.support import ROOT


def _pyproject() -> dict[str, object]:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_pyproject_defines_coverage_poe_task() -> None:
    tasks = _pyproject()["tool"]["poe"]["tasks"]

    assert "coverage" in tasks


def test_poe_verify_includes_coverage_gate() -> None:
    verify = _pyproject()["tool"]["poe"]["tasks"]["verify"]

    assert "coverage" in verify["sequence"]


def test_repository_defines_approved_coverage_thresholds() -> None:
    script_path = ROOT / "scripts" / "coverage_check.py"

    assert script_path.exists()

    script = script_path.read_text(encoding="utf-8")
    assert "90.0" in script
    assert "100.0" in script
    assert "src/quantcraft/trading/domain/" in script


def test_coverage_harness_targets_source_only() -> None:
    script = (ROOT / "scripts" / "coverage_check.py").read_text(encoding="utf-8")

    assert "src/quantcraft/*" in script
