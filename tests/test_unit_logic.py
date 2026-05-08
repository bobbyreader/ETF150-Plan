from etf150.strategy.units import suggest_units


def test_unit_suggestion_defaults_to_one_unit() -> None:
    suggestion = suggest_units(150000, "normal", "normal")
    assert suggestion.suggested_units == 1
    assert suggestion.unit_amount == 1000.0


def test_unit_suggestion_accelerates_in_golden_zone() -> None:
    suggestion = suggest_units(150000, "golden", "normal")
    assert suggestion.suggested_units == 2


def test_unit_suggestion_caps_at_40_in_extreme_bottom() -> None:
    suggestion = suggest_units(150000, "diamond", "extreme_bottom")
    assert suggestion.suggested_units == 40
