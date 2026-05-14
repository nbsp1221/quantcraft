from __future__ import annotations

from quantleet.research import WalkForwardStudy
from tests.unit.research.support_parameter_study import NoTradeStrategy, make_bars, make_engine


def test_no_closed_trades_emits_info_diagnostic_without_failing_run() -> None:
    result = WalkForwardStudy(
        engine=make_engine(),
        bars=make_bars(closes=tuple(float(100 + index) for index in range(8))),
        strategy=NoTradeStrategy,
    ).run(
        parameters={"x": [1]},
        objective=("returns.total_return", "max"),
        train_size=4,
        test_size=2,
    )

    diagnostics = {diagnostic.code: diagnostic for diagnostic in result.diagnostics}
    assert result.failed_fold_count == 0
    assert diagnostics["no_closed_trades"].severity == "info"
    assert diagnostics["no_closed_trades"].fold_indexes == (0, 1)


def test_no_selected_config_and_zero_successful_oos_are_warning_diagnostics() -> None:
    result = WalkForwardStudy(
        engine=make_engine(),
        bars=make_bars(closes=tuple(float(100 + index) for index in range(8))),
        strategy=NoTradeStrategy,
    ).run(
        parameters={"x": [1]},
        objective=("returns.total_return", "max"),
        constraint=lambda config: False,
        train_size=4,
        test_size=2,
    )

    diagnostics = {diagnostic.code: diagnostic for diagnostic in result.diagnostics}
    assert result.failed_fold_count == 2
    assert diagnostics["fold_execution_failed"].severity == "warning"
    assert diagnostics["no_selected_config"].severity == "warning"
    assert diagnostics["zero_successful_oos_folds"].severity == "warning"
