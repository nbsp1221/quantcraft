from __future__ import annotations

import ast
import inspect
from pathlib import Path

from quantcraft.backtest import BacktestEngine
from quantcraft.research import WalkForwardValidation

ROOT = Path(__file__).resolve().parents[3]


def _imports(module_path: str) -> set[str]:
    tree = ast.parse((ROOT / module_path).read_text())
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imports.add(node.module)
        elif isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
    return imports


def test_walk_forward_validation_is_owned_by_research_and_does_not_invert_dependencies() -> None:
    assert (ROOT / "src/quantcraft/research/validation/walk_forward.py").exists()
    assert "quantcraft.research.validation.walk_forward" in WalkForwardValidation.__module__

    imports = _imports("src/quantcraft/research/validation/walk_forward.py")
    assert "quantcraft.backtest.engine" not in imports
    assert "quantcraft.research.validation.walk_forward" not in _imports(
        "src/quantcraft/backtest/engine.py"
    )
    assert "quantcraft.research.validation.walk_forward" not in _imports(
        "src/quantcraft/trading/__init__.py"
    )
    assert "quantcraft.research.validation.walk_forward" not in _imports(
        "src/quantcraft/execution/__init__.py"
    )


def test_backtest_engine_does_not_gain_walk_forward_or_optimizer_methods() -> None:
    assert not hasattr(BacktestEngine, "walk_forward")
    assert not hasattr(BacktestEngine, "optimize")


def test_walk_forward_validation_public_signature_omits_deferred_controls() -> None:
    init_signature = inspect.signature(WalkForwardValidation)
    run_signature = inspect.signature(WalkForwardValidation.run)

    assert "objective" in init_signature.parameters
    assert "source" not in init_signature.parameters
    assert "folds" not in run_signature.parameters
    assert "workers" not in run_signature.parameters
    assert "gap" not in run_signature.parameters
    assert "embargo" not in run_signature.parameters
