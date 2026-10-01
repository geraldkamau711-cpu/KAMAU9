from __future__ import annotations

from core.finding import Finding
from modules.crypto.observation import CryptoMarketObservation


class CryptoObservationEvidence:
    """Convert crypto market observations into K9 findings."""

    SOURCE = "crypto_market_intelligence"
    SEVERITY = "info"

    def to_finding(
        self,
        observation: CryptoMarketObservation,
        target: str,
    ) -> Finding:
        if not isinstance(observation, CryptoMarketObservation):
            raise TypeError(
                "Crypto observation must be a CryptoMarketObservation."
            )

        if not isinstance(target, str) or not target.strip():
            raise ValueError(
                "Crypto evidence target must be a non-empty string."
            )

        return Finding(
            title=f"Crypto market observation: {observation.symbol}",
            severity=self.SEVERITY,
            description=(
                f"Observed {observation.symbol} at "
                f"{observation.price} with volume "
                f"{observation.volume}."
            ),
            source=self.SOURCE,
            target=target,
            evidence={
                "symbol": observation.symbol,
                "timestamp": observation.timestamp.isoformat(),
                "price": observation.price,
                "volume": observation.volume,
                "source": observation.source,
                "observation_type": observation.observation_type,
            },
        )
