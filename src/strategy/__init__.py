from __future__ import annotations

from typing import Literal


def generate_signal(
    fast_ma: float,
    slow_ma: float,
    trend_ma: float,
    rsi: float,
    current_price: float,
) -> Literal["BUY", "SELL", "HOLD"]:
    """
    Generates trading signal based on MA crossover strategy.
    
    Rules:
    - BUY: fast_ma > slow_ma AND price > trend_ma AND rsi < 70
    - SELL: fast_ma < slow_ma AND rsi > 30
    - HOLD: otherwise
    """
    # Buy signal
    if fast_ma > slow_ma and current_price > trend_ma and rsi < 70:
        return "BUY"
    
    # Sell signal
    if fast_ma < slow_ma and rsi > 30:
        return "SELL"
    
    return "HOLD"
