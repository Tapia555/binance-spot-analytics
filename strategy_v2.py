import numpy as np
import pandas as pd
from collections import deque
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class StrategyConfig:
    fast_period: int = 12
    slow_period: int = 26
    rsi_period: int = 14
    rsi_buy_threshold: float = 30
    rsi_sell_threshold: float = 70
    min_volume_ratio: float = 1.5
    atr_period: int = 14
    stop_loss_pct: float = 2.0
    take_profit_pct: float = 4.0

class EnhancedMACDStrategy:
    def __init__(self, config: Optional[StrategyConfig] = None):
        self.config = config or StrategyConfig()
        self.fast_ema = deque(maxlen=self.config.fast_period + 10)
        self.slow_ema = deque(maxlen=self.config.slow_period + 10)
        self.rsi_values = deque(maxlen=self.config.rsi_period + 10)
        self.volume_values = deque(maxlen=20)
        self.prev_fast = None
        self.prev_slow = None
        self.prices = deque(maxlen=100)
        
    def _ema(self, value: float, prev: Optional[float], period: int) -> float:
        multiplier = 2 / (period + 1)
        if prev is None:
            return value
        return (value - prev) * multiplier + prev
    
    def _rsi(self, prices: deque) -> float:
        if len(prices) < self.config.rsi_period + 1:
            return 50.0
        diffs = np.diff(list(prices)[-self.config.rsi_period-1:])
        gains = np.where(diffs > 0, diffs, 0)
        losses = np.where(diffs < 0, -diffs, 0)
        avg_gain = np.mean(gains) if len(gains) > 0 else 0
        avg_loss = np.mean(losses) if len(losses) > 0 else 0
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def _volume_spike(self) -> bool:
        if len(self.volume_values) < 10:
            return False
        recent = list(self.volume_values)[-5:]
        prev = list(self.volume_values)[:-5]
        if len(prev) == 0:
            return False
        avg_prev = np.mean(prev)
        avg_recent = np.mean(recent)
        return avg_recent > (avg_prev * self.config.min_volume_ratio)
    
    def update(self, price: float, volume: float) -> Tuple[Signal, Dict]:
        self.prices.append(price)
        self.volume_values.append(volume)
        
        if len(self.prices) < self.config.slow_period + 10:
            return Signal.HOLD, {"reason": "insufficient_data"}
        
        if self.prev_fast is None:
            self.prev_fast = price
            self.prev_slow = price
            return Signal.HOLD, {"reason": "initializing"}
        
        self.fast_ema.append(self._ema(price, self.prev_fast, self.config.fast_period))
        self.slow_ema.append(self._ema(price, self.prev_slow, self.config.slow_period))
        
        self.prev_fast = self.fast_ema[-1]
        self.prev_slow = self.slow_ema[-1]
        
        rsi = self._rsi(self.prices)
        self.rsi_values.append(rsi)
        
        fast = self.fast_ema[-1]
        slow = self.slow_ema[-1]
        
        crossed_up = (self.prev_fast <= self.prev_slow) and (fast > slow)
        crossed_down = (self.prev_fast >= self.prev_slow) and (fast < slow)
        
        volume_confirmed = self._volume_spike()
        rsi_oversold = rsi < self.config.rsi_buy_threshold
        rsi_overbought = rsi > self.config.rsi_sell_threshold
        
        signal = Signal.HOLD
        reason = "filtered_or_no_crossover"
        
        if crossed_up and (rsi_oversold or volume_confirmed):
            signal = Signal.BUY
            reason = "macd_crossover_up_confirmed"
        elif crossed_down and (rsi_overbought or volume_confirmed):
            signal = Signal.SELL
            reason = "macd_crossover_down_confirmed"
        
        return signal, {
            "fast": fast,
            "slow": slow,
            "rsi": rsi,
            "volume_spike": volume_confirmed,
            "reason": reason
        }
