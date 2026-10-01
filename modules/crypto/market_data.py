from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CryptoMarketSnapshot:
    """Normalised point-in-time crypto market observation."""

    symbol: str
    timestamp: datetime
    price: float
    volume: float

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError("Market snapshot symbol must be a non-empty string.")

        if not isinstance(self.timestamp, datetime):
            raise TypeError("Market snapshot timestamp must be a datetime.")

        if not isinstance(self.price, (int, float)):
            raise TypeError("Market snapshot price must be numeric.")

        if not isinstance(self.volume, (int, float)):
            raise TypeError("Market snapshot volume must be numeric.")

        if self.price < 0:
            raise ValueError("Market snapshot price cannot be negative.")

        if self.volume < 0:
            raise ValueError("Market snapshot volume cannot be negative.")


class CryptoMarketDataProvider:
    """Interface for providers that supply normalised crypto market data."""

    def get_snapshot(self, symbol: str) -> CryptoMarketSnapshot:
        raise NotImplementedError
