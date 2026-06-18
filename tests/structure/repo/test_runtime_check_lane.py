from __future__ import annotations

import tomllib

from tests.support import ROOT


def _pyproject() -> dict[str, object]:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_pyproject_defines_runtime_check_task() -> None:
    tasks = _pyproject()["tool"]["poe"]["tasks"]

    assert "check-runtime" in tasks
    check_runtime = tasks["check-runtime"]
    assert check_runtime["sequence"] == ["check", "perf-check"]
    assert (
        check_runtime["help"] == "Run the stronger explicit check lane for runtime-sensitive "
        "backtest or research changes"
    )


def test_runtime_check_lane_is_documented_with_trigger_paths() -> None:
    reliability = (ROOT / "docs" / "RELIABILITY.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    for content in [reliability, agents]:
        assert "uv run poe check-runtime" in content
        assert "runtime-sensitive backtest or research" in content

    for path in [
        "src/quantcraft/backtest/engine.py",
        "src/quantcraft/backtest/runtime.py",
        "src/quantcraft/backtest/execution_model.py",
        "src/quantcraft/backtest/order_activation.py",
        "src/quantcraft/backtest/strategy_runtime.py",
        "src/quantcraft/research/ta.py",
        "src/quantcraft/research/strategy.py",
        "src/quantcraft/research/indicators/runtime/",
        "src/quantcraft/research/indicators/pure/",
    ]:
        assert path in reliability or path in agents
