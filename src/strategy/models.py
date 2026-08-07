from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SignalSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class Signal:
    side: SignalSide
    reason: str
    price: float | None = None
    confidence: float = 0.0
