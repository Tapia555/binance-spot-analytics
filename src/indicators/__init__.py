from __future__ import annotations

from typing import List


def calculate_ma(prices: List[float], period: int) -> float:
    """Calculates Simple Moving Average."""
    if len(prices) < period:
        return prices[-1] if prices else 0.0
    return sum(prices[-period:]) / period


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Calculates RSI (Relative Strength Index)."""
    if len(prices) < period + 1:
        return 50.0
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))
    
    # Берём последние period значений
    recent_gains = gains[-period:] if len(gains) >= period else gains
    recent_losses = losses[-period:] if len(losses) >= period else losses
    
    avg_gain = sum(recent_gains) / len(recent_gains) if recent_gains else 0
    avg_loss = sum(recent_losses) / len(recent_losses) if recent_losses else 0
    
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_volatility(prices: List[float], period: int = 20) -> float:
    """Calculates historical volatility."""
    if len(prices) < period + 1:
        return 0.0
    
    returns = []
    for i in range(1, len(prices)):
        ret = (prices[i] - prices[i - 1]) / prices[i - 1]
        returns.append(ret)
    
    recent_returns = returns[-period:]
    mean_return = sum(recent_returns) / len(recent_returns)
    variance = sum((r - mean_return) ** 2 for r in recent_returns) / len(recent_returns)
    
    return variance ** 0.5
