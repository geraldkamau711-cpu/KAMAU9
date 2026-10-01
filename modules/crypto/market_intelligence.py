from __future__ import annotations

from core.mode import K9Mode
from core.module import K9Module
from modules.crypto.market_data import (
    CryptoMarketDataProvider,
    CryptoMarketSnapshot,
)


class CryptoMarketIntelligence(K9Module):
    """CRYPTO module for structured market intelligence."""

    name = "crypto_market_intelligence"
    supported_modes = frozenset({K9Mode.CRYPTO, K9Mode.ANALYSIS})

    REQUIRED_CONTEXT = frozenset({"symbol"})

    def __init__(self, provider: CryptoMarketDataProvider):
        self.provider = provider

    def run(self, context):
        self._validate_context(context)

        symbol = context["symbol"]
        snapshot = self.provider.get_snapshot(symbol)

        if not isinstance(snapshot, CryptoMarketSnapshot):
            raise TypeError(
                "Crypto market data provider must return "
                "a CryptoMarketSnapshot."
            )

        return {
            "module": self.name,
            "status": "ok",
            "symbol": snapshot.symbol,
            "timestamp": snapshot.timestamp,
            "price": snapshot.price,
            "volume": snapshot.volume,
            "findings": [],
        }

    def _validate_context(self, context):
        if not isinstance(context, dict):
            raise TypeError("Crypto module context must be a dictionary.")

        missing = self.REQUIRED_CONTEXT - context.keys()

        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(
                f"Missing required crypto context: {names}"
            )

        mode = context.get("mode")

        if not isinstance(mode, K9Mode):
            raise TypeError("Crypto module context mode must be a K9Mode.")

        if mode not in self.supported_modes:
            raise ValueError(
                f"Crypto module cannot execute in mode: {mode.value}"
            )
