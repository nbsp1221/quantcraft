import importlib
import importlib.util

import pytest

import quantcraft


def test_data_public_import_surface_exposes_time_bar_and_bar_series() -> None:
    data_module = importlib.import_module("quantcraft.data")

    assert getattr(data_module, "TimeBar", None) is not None
    assert getattr(data_module, "BarSeries", None) is not None
    assert getattr(data_module, "CCXTDataSource", None) is not None
    assert getattr(data_module, "CSVDataSource", None) is not None
    assert getattr(data_module, "DataFrameDataSource", None) is not None


def test_root_package_exports_no_legacy_public_symbols() -> None:
    for name in ("Exchange", "MarketType", "TimeBar", "BacktestEngine"):
        with pytest.raises(AttributeError, match="has no attribute"):
            getattr(quantcraft, name)


def test_research_public_import_surface_exposes_validation_pipeline() -> None:
    research_module = importlib.import_module("quantcraft.research")

    for name in (
        "ValidationPipeline",
        "ValidationStep",
        "ValidationContext",
        "ValidationReport",
        "ValidationStepResult",
        "ValidationDiagnostic",
        "ValidationProvenance",
        "ValidationArtifact",
        "ValidationStatus",
        "SplitWindow",
        "RollingSplitPolicy",
        "WalkForwardValidation",
        "WalkForwardValidationResult",
        "WalkForwardFoldResult",
        "ta",
        "qc",
    ):
        assert getattr(research_module, name, None) is not None

    for old_name in (
        "Strategy",
        "ParameterStudy",
        "GridSearchResult",
        "GridSearchRow",
        "WalkForwardStudy",
        "WalkForwardResult",
        "WalkForwardFold",
        "WalkForwardDiagnostic",
        "WalkForwardOosSummary",
        "WalkForwardExecutionScale",
        "MetricSelectionPolicy",
        "run_backtest",
        "BacktestEngine",
    ):
        assert not hasattr(research_module, old_name)

    for old_module in (
        "quantcraft.research.parameter_exploration",
        "quantcraft.research.walk_forward",
        "quantcraft.research.strategy",
        "quantcraft.research.series",
    ):
        assert importlib.util.find_spec(old_module) is None


def test_strategy_public_import_surface_exposes_strategy_config_contract() -> None:
    strategy_module = importlib.import_module("quantcraft.strategy")
    research_module = importlib.import_module("quantcraft.research")

    assert getattr(strategy_module, "Strategy", None) is not None
    assert getattr(strategy_module, "StrategyConfig", None) is not None
    assert getattr(strategy_module, "StrategyConfigError", None) is not None
    assert getattr(strategy_module, "StrategyConfigDeclarationError", None) is not None
    assert getattr(strategy_module, "StrategyConfigValidationError", None) is not None
    assert getattr(strategy_module, "StrategyConfigMutationError", None) is not None
    assert not hasattr(research_module, "Strategy")


def test_capability_public_surfaces_import_cleanly() -> None:
    research_module = importlib.import_module("quantcraft.research")
    strategy_module = importlib.import_module("quantcraft.strategy")
    backtest_module = importlib.import_module("quantcraft.backtest")
    execution_module = importlib.import_module("quantcraft.execution")
    integrations_module = importlib.import_module("quantcraft.integrations")
    ccxt_module = importlib.import_module("quantcraft.integrations.venues.ccxt")

    assert getattr(backtest_module, "BacktestEngine", None) is not None
    assert getattr(backtest_module, "BacktestStrategyConstructionError", None) is not None
    assert getattr(backtest_module, "CostConfig", None) is not None
    assert getattr(backtest_module, "BacktestReport", None) is not None
    assert getattr(backtest_module, "RunManifest", None) is not None
    assert getattr(backtest_module, "ExecutionAssumptions", None) is not None
    assert getattr(backtest_module, "ReturnMetrics", None) is not None
    assert getattr(backtest_module, "RiskMetrics", None) is not None
    assert getattr(backtest_module, "TradeMetrics", None) is not None
    assert getattr(backtest_module, "CostMetrics", None) is not None
    assert getattr(backtest_module, "ExposureMetrics", None) is not None
    assert getattr(backtest_module, "EquityPoint", None) is not None
    assert getattr(backtest_module, "ReportingFill", None) is not None
    assert getattr(backtest_module, "ClosedTrade", None) is not None
    assert getattr(backtest_module, "BacktestResult", None) is not None
    assert getattr(backtest_module, "BacktestSummary", None) is not None
    assert getattr(backtest_module, "ExposureSummary", None) is not None
    assert getattr(strategy_module, "Strategy", None) is not None
    assert getattr(strategy_module, "StrategyConfig", None) is not None
    assert getattr(research_module, "ValidationPipeline", None) is not None
    assert getattr(research_module, "WalkForwardValidation", None) is not None
    assert getattr(ccxt_module, "Exchange", None) is not None
    assert getattr(ccxt_module, "MarketType", None) is not None
    for name in (
        "CCXTBackend",
        "TimeBar",
        "_DEFAULT_PAGINATION_LIMIT",
        "_fetch_ohlcv_range",
        "_make_ccxt_exchange",
        "_validate_symbol_contract",
        "ccxt",
    ):
        assert not hasattr(ccxt_module, name)
    assert getattr(execution_module, "__all__", None) == []
    assert getattr(integrations_module, "__all__", None) == []


def test_removed_legacy_paths_no_longer_import() -> None:
    for module_name in (
        "quantcraft.exchange",
        "quantcraft.data.adapters.exchange_backend",
        "quantcraft.data.domain",
        "quantcraft.data.domain.bars",
        "quantcraft.data.domain.sources",
        "quantcraft.research.domain",
        "quantcraft.research.domain.series",
        "quantcraft.research.application",
        "quantcraft.research.application.backtest",
        "quantcraft.research.application.engine",
        "quantcraft.research.application.order_activation",
        "quantcraft.research.application.strategy",
        "quantcraft.research.application._runtime",
        "quantcraft.research.adapters",
        "quantcraft.research.adapters.execution_model",
        "quantcraft.data.application",
        "quantcraft.trading.application",
        "quantcraft.trading.adapters",
    ):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(module_name)
