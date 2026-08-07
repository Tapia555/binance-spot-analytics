from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskLevels:
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_per_unit: float


def calculate_long_levels(
    entry_price: float,
    atr_value: float,
    *,
    stop_atr_multiplier: float = 1.5,
    reward_risk_ratio: float = 2.0,
) -> RiskLevels:
    if entry_price <= 0:
        raise ValueError("entry_price must be positive")

    if atr_value <= 0:
        raise ValueError("atr_value must be positive")

    if stop_atr_multiplier <= 0:
        raise ValueError("stop_atr_multiplier must be positive")

    if reward_risk_ratio <= 0:
        raise ValueError("reward_risk_ratio must be positive")

    risk_per_unit = atr_value * stop_atr_multiplier
    stop_loss = entry_price - risk_per_unit
    take_profit = entry_price + risk_per_unit * reward_risk_ratio

    if stop_loss <= 0:
        raise ValueError("calculated stop_loss must be positive")

    return RiskLevels(
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        risk_per_unit=risk_per_unit,
    )
