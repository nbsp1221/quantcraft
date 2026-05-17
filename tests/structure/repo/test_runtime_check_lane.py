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
        "src/quantleet/backtest/engine.py",
        "src/quantleet/backtest/runtime.py",
        "src/quantleet/backtest/execution_model.py",
        "src/quantleet/backtest/order_activation.py",
        "src/quantleet/backtest/strategy_runtime.py",
        "src/quantleet/research/ta.py",
        "src/quantleet/research/strategy.py",
        "src/quantleet/research/indicators/runtime/",
        "src/quantleet/research/indicators/pure/",
    ]:
        assert path in reliability or path in agents
