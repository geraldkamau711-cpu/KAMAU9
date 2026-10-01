from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CryptoMarketObservation:
    """Structured crypto market observation for K9 evidence pipelines."""

    symbol: str
    timestamp: datetime
    price: float
    volume: float
    source: str
    observation_type: str = "market_snapshot"

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError(
                "Observation symbol must be a non-empty string."
            )

        if not isinstance(self.timestamp, datetime):
            raise TypeError(
                "Observation timestamp must be a datetime."
            )

        if not isinstance(self.price, (int, float)):
            raise TypeError(
                "Observation price must be numeric."
            )

        if not isinstance(self.volume, (int, float)):
            raise TypeError(
                "Observation volume must be numeric."
            )

        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError(
                "Observation source must be a non-empty string."
            )

        if (
            not isinstance(self.observation_type, str)
            or not self.observation_type.strip()
        ):
            raise ValueError(
                "Observation type must be a non-empty string."
            )

        if self.price < 0:
            raise ValueError(
                "Observation price cannot be negative."
            )

        if self.volume < 0:
            raise ValueError(
                "Observation volume cannot be negative."
            )
