from __future__ import annotations

import ast
import inspect
from pathlib import Path

from quantleet.backtest import BacktestEngine
from quantleet.research import WalkForwardStudy

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


def test_walk_forward_is_owned_by_research_and_does_not_invert_dependencies() -> None:
    assert (ROOT / "src/quantleet/research/walk_forward.py").exists()
    assert "quantleet.research.walk_forward" in WalkForwardStudy.__module__

    imports = _imports("src/quantleet/research/walk_forward.py")
    assert "quantleet.backtest.engine" not in imports
    assert "quantleet.research.walk_forward" not in _imports("src/quantleet/backtest/engine.py")
    assert "quantleet.research.walk_forward" not in _imports("src/quantleet/trading/__init__.py")
    assert "quantleet.research.walk_forward" not in _imports("src/quantleet/execution/__init__.py")


def test_backtest_engine_does_not_gain_walk_forward_or_optimizer_methods() -> None:
    assert not hasattr(BacktestEngine, "walk_forward")
    assert not hasattr(BacktestEngine, "optimize")


def test_walk_forward_public_signature_omits_deferred_stage_four_controls() -> None:
    signature = inspect.signature(WalkForwardStudy.run)

    assert "source" not in signature.parameters
    assert "folds" not in signature.parameters
    assert "workers" not in signature.parameters
    assert "gap" not in signature.parameters
    assert "embargo" not in signature.parameters
