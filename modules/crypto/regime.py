from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite

from modules.crypto.market_data import CryptoMarketSnapshot


class CryptoMarketRegime(str, Enum):
    """Deterministic crypto market activity regimes."""

    INSUFFICIENT_DATA = "insufficient_data"
    QUIET = "quiet"
    NORMAL = "normal"
    HIGH_ACTIVITY = "high_activity"
    PRICE_EXPANSION = "price_expansion"


@dataclass(frozen=True)
class CryptoRegimeThresholds:
    """Configurable thresholds for deterministic regime classification."""

    high_volume_ratio: float = 2.0
    price_expansion_ratio: float = 0.03

    def __post_init__(self) -> None:
        if self.high_volume_ratio <= 0:
            raise ValueError(
                "High-volume ratio must be greater than zero."
            )

        if self.price_expansion_ratio <= 0:
            raise ValueError(
                "Price-expansion ratio must be greater than zero."
            )


@dataclass(frozen=True)
class CryptoMarketRegimeObservation:
    """Structured classification of crypto market activity."""

    symbol: str
    regime: CryptoMarketRegime
    price_change_ratio: float | None
    volume_ratio: float | None
    observation_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError(
                "Regime observation symbol must be a non-empty string."
            )

        if not isinstance(self.regime, CryptoMarketRegime):
            raise TypeError(
                "Regime observation regime must be a CryptoMarketRegime."
            )

        if not isinstance(self.observation_count, int):
            raise TypeError(
                "Regime observation count must be an integer."
            )

        if self.observation_count < 0:
            raise ValueError(
                "Regime observation count cannot be negative."
            )

        if self.price_change_ratio is not None:
            if not isinstance(self.price_change_ratio, (int, float)):
                raise TypeError(
                    "Price change ratio must be numeric or None."
                )

            if not isfinite(self.price_change_ratio):
                raise ValueError(
                    "Price change ratio must be finite."
                )

        if self.volume_ratio is not None:
            if not isinstance(self.volume_ratio, (int, float)):
                raise TypeError(
                    "Volume ratio must be numeric or None."
                )

            if not isfinite(self.volume_ratio):
                raise ValueError(
                    "Volume ratio must be finite."
                )


class CryptoMarketRegimeClassifier:
    """Classify crypto market activity from deterministic snapshots."""

    def __init__(
        self,
        thresholds: CryptoRegimeThresholds | None = None,
    ):
        self.thresholds = thresholds or CryptoRegimeThresholds()

    def classify(
        self,
        snapshots: list[CryptoMarketSnapshot],
    ) -> CryptoMarketRegimeObservation:
        self._validate_snapshots(snapshots)

        if len(snapshots) < 2:
            symbol = snapshots[0].symbol if snapshots else "unknown"

            return CryptoMarketRegimeObservation(
                symbol=symbol,
                regime=CryptoMarketRegime.INSUFFICIENT_DATA,
                price_change_ratio=None,
                volume_ratio=None,
                observation_count=len(snapshots),
            )

        previous = snapshots[-2]
        current = snapshots[-1]

        if previous.symbol != current.symbol:
            raise ValueError(
                "Crypto regime snapshots must use the same symbol."
            )

        if previous.price <= 0:
            raise ValueError(
                "Previous snapshot price must be greater than zero."
            )

        if previous.volume <= 0:
            raise ValueError(
                "Previous snapshot volume must be greater than zero."
            )

        price_change_ratio = (
            current.price - previous.price
        ) / previous.price

        volume_ratio = current.volume / previous.volume

        if abs(price_change_ratio) >= self.thresholds.price_expansion_ratio:
            regime = CryptoMarketRegime.PRICE_EXPANSION
        elif volume_ratio >= self.thresholds.high_volume_ratio:
            regime = CryptoMarketRegime.HIGH_ACTIVITY
        elif volume_ratio < 1.0 and abs(price_change_ratio) < (
            self.thresholds.price_expansion_ratio / 2
        ):
            regime = CryptoMarketRegime.QUIET
        else:
            regime = CryptoMarketRegime.NORMAL

        return CryptoMarketRegimeObservation(
            symbol=current.symbol,
            regime=regime,
            price_change_ratio=price_change_ratio,
            volume_ratio=volume_ratio,
            observation_count=len(snapshots),
        )

    @staticmethod
    def _validate_snapshots(
        snapshots: list[CryptoMarketSnapshot],
    ) -> None:
        if not isinstance(snapshots, list):
            raise TypeError(
                "Crypto regime snapshots must be a list."
            )

        for snapshot in snapshots:
            if not isinstance(snapshot, CryptoMarketSnapshot):
                raise TypeError(
                    "Crypto regime snapshots must contain "
                    "CryptoMarketSnapshot objects."
                )
