import pytest

from risk.levels import calculate_long_levels


def test_calculate_long_levels():
    levels = calculate_long_levels(
        entry_price=100.0,
        atr_value=2.0,
        stop_atr_multiplier=1.5,
        reward_risk_ratio=2.0,
    )

    assert levels.entry_price == 100.0
    assert levels.risk_per_unit == pytest.approx(3.0)
    assert levels.stop_loss == pytest.approx(97.0)
    assert levels.take_profit == pytest.approx(106.0)


def test_reject_invalid_values():
    with pytest.raises(ValueError):
        calculate_long_levels(0.0, 2.0)

    with pytest.raises(ValueError):
        calculate_long_levels(100.0, 0.0)

    with pytest.raises(ValueError):
        calculate_long_levels(100.0, 2.0, stop_atr_multiplier=0.0)
