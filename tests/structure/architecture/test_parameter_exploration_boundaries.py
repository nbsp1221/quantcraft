from __future__ import annotations

import ast
from pathlib import Path

from tests.support import ROOT

VALIDATION_IMPORT = "quantcraft.research.validation"


def _imports_validation(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.startswith(VALIDATION_IMPORT) for alias in node.names):
                return True
        elif isinstance(node, ast.ImportFrom) and (node.module or "").startswith(VALIDATION_IMPORT):
            return True
    return False


def test_validation_subpackage_lives_under_research_boundary() -> None:
    assert (ROOT / "src" / "quantcraft" / "research" / "validation").is_dir()


def test_backtest_trading_and_execution_do_not_import_validation_layer() -> None:
    for package_name in ("backtest", "trading", "execution"):
        package_root = ROOT / "src" / "quantcraft" / package_name
        offenders = [path for path in package_root.rglob("*.py") if _imports_validation(path)]
        assert offenders == []


def test_backtest_surface_does_not_gain_validation_exports() -> None:
    import quantcraft.backtest as backtest

    for name in ("ValidationPipeline", "WalkForwardValidation", "RollingSplitPolicy"):
        assert not hasattr(backtest, name)


def test_no_heavy_optimizer_dependency_is_added_for_beta() -> None:
    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    for dependency_name in ("optuna", "ray", "scikit-optimize", "skopt"):
        assert dependency_name not in pyproject_text
