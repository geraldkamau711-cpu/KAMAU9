from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite, sqrt

from modules.crypto.market_data import CryptoMarketSnapshot


class CryptoVolatilityRegime(str, Enum):
    """Deterministic crypto price-volatility regimes."""

    INSUFFICIENT_DATA = "insufficient_data"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


@dataclass(frozen=True)
class CryptoVolatilityThresholds:
    """Configurable thresholds for volatility classification."""

    low: float = 0.005
    high: float = 0.02

    def __post_init__(self) -> None:
        if not isfinite(self.low) or self.low <= 0:
            raise ValueError(
                "Low-volatility threshold must be greater than zero."
            )

        if not isfinite(self.high) or self.high <= self.low:
            raise ValueError(
                "High-volatility threshold must be greater than "
                "the low-volatility threshold."
            )


@dataclass(frozen=True)
class CryptoVolatilityObservation:
    """Structured volatility measurement for K9 intelligence."""

    symbol: str
    regime: CryptoVolatilityRegime
    realised_volatility: float | None
    return_count: int
    observation_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError(
                "Volatility observation symbol must be a non-empty string."
            )

        if not isinstance(self.regime, CryptoVolatilityRegime):
            raise TypeError(
                "Volatility observation regime must be a "
                "CryptoVolatilityRegime."
            )

        if not isinstance(self.return_count, int):
            raise TypeError(
                "Volatility observation return count must be an integer."
            )

        if not isinstance(self.observation_count, int):
            raise TypeError(
                "Volatility observation count must be an integer."
            )

        if self.return_count < 0:
            raise ValueError(
                "Volatility observation return count cannot be negative."
            )

        if self.observation_count < 0:
            raise ValueError(
                "Volatility observation count cannot be negative."
            )

        if self.realised_volatility is not None:
            if not isinstance(self.realised_volatility, (int, float)):
                raise TypeError(
                    "Realised volatility must be numeric or None."
                )

            if not isfinite(self.realised_volatility):
                raise ValueError(
                    "Realised volatility must be finite."
                )

            if self.realised_volatility < 0:
                raise ValueError(
                    "Realised volatility cannot be negative."
                )


class CryptoVolatilityClassifier:
    """Classify crypto price volatility from deterministic snapshots."""

    def __init__(
        self,
        thresholds: CryptoVolatilityThresholds | None = None,
    ):
        self.thresholds = thresholds or CryptoVolatilityThresholds()

    def classify(
        self,
        snapshots: list[CryptoMarketSnapshot],
    ) -> CryptoVolatilityObservation:
        self._validate_snapshots(snapshots)

        symbol = snapshots[-1].symbol if snapshots else "unknown"

        if len(snapshots) < 2:
            return CryptoVolatilityObservation(
                symbol=symbol,
                regime=CryptoVolatilityRegime.INSUFFICIENT_DATA,
                realised_volatility=None,
                return_count=0,
                observation_count=len(snapshots),
            )

        for snapshot in snapshots:
            if snapshot.symbol != symbol:
                raise ValueError(
                    "Crypto volatility snapshots must use the same symbol."
                )

            if snapshot.price <= 0:
                raise ValueError(
                    "Crypto volatility snapshot prices must be "
                    "greater than zero."
                )

        returns = [
            (current.price - previous.price) / previous.price
            for previous, current in zip(
                snapshots,
                snapshots[1:],
            )
        ]

        if len(returns) < 2:
            realised_volatility = abs(returns[0])
        else:
            mean_return = sum(returns) / len(returns)

            variance = sum(
                (value - mean_return) ** 2
                for value in returns
            ) / len(returns)

            realised_volatility = sqrt(variance)

        if realised_volatility < self.thresholds.low:
            regime = CryptoVolatilityRegime.LOW
        elif realised_volatility >= self.thresholds.high:
            regime = CryptoVolatilityRegime.HIGH
        else:
            regime = CryptoVolatilityRegime.NORMAL

        return CryptoVolatilityObservation(
            symbol=symbol,
            regime=regime,
            realised_volatility=realised_volatility,
            return_count=len(returns),
            observation_count=len(snapshots),
        )

    @staticmethod
    def _validate_snapshots(
        snapshots: list[CryptoMarketSnapshot],
    ) -> None:
        if not isinstance(snapshots, list):
            raise TypeError(
                "Crypto volatility snapshots must be a list."
            )

        for snapshot in snapshots:
            if not isinstance(snapshot, CryptoMarketSnapshot):
                raise TypeError(
                    "Crypto volatility snapshots must contain "
                    "CryptoMarketSnapshot objects."
                )
