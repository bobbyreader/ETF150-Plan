from etf150.strategy.position import suggest_position


def test_position_suggestion_halves_exposure_in_high_percentile() -> None:
    suggestion = suggest_position(70)
    assert suggestion.target_equity_pct == 15.0


def test_position_suggestion_rebalances_near_center() -> None:
    suggestion = suggest_position(50)
    assert 40.0 <= suggestion.target_equity_pct <= 45.0


def test_position_suggestion_amplifies_low_percentile() -> None:
    suggestion = suggest_position(20)
    assert suggestion.target_equity_pct > 80.0
