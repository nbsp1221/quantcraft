from __future__ import annotations

from scripts import coverage_check


def test_default_pytest_args_match_default_lane() -> None:
    assert coverage_check.default_pytest_args() == ["-q"]
