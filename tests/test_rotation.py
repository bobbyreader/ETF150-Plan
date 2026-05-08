from etf150.strategy.rotation import suggest_rotation


def test_rotation_suggestion_triggers_on_large_gap() -> None:
    suggestion = suggest_rotation("中证500", 70, "创业板", 30)
    assert suggestion.should_rotate is True
    assert suggestion.from_asset == "中证500"
    assert suggestion.to_asset == "创业板"


def test_rotation_suggestion_skips_small_gap() -> None:
    suggestion = suggest_rotation("中证500", 45, "创业板", 35)
    assert suggestion.should_rotate is False
