from __future__ import annotations

from core.finding import Finding
from core.mode import K9Mode
from core.module import K9Module
from modules.crypto.evidence import CryptoObservationEvidence
from modules.crypto.market_data import (
    CryptoMarketDataProvider,
    CryptoMarketSnapshot,
)
from modules.crypto.observation import CryptoMarketObservation
from modules.crypto.regime import (
    CryptoMarketRegimeClassifier,
    CryptoMarketRegimeObservation,
)
from modules.crypto.synthesis import (
    CryptoIntelligenceObservation,
    CryptoIntelligenceSynthesizer,
)
from modules.crypto.volatility import (
    CryptoVolatilityClassifier,
    CryptoVolatilityObservation,
)


class CryptoMarketIntelligence(K9Module):
    """CRYPTO module for structured market intelligence."""

    name = "crypto_market_intelligence"
    supported_modes = frozenset({K9Mode.CRYPTO, K9Mode.ANALYSIS})

    REQUIRED_CONTEXT = frozenset({"symbol"})

    def __init__(
        self,
        provider: CryptoMarketDataProvider,
        evidence_adapter: CryptoObservationEvidence | None = None,
        regime_classifier: CryptoMarketRegimeClassifier | None = None,
        volatility_classifier: CryptoVolatilityClassifier | None = None,
        intelligence_synthesizer: CryptoIntelligenceSynthesizer | None = None,
    ):
        self.provider = provider
        self.evidence_adapter = evidence_adapter or CryptoObservationEvidence()
        self.regime_classifier = (
            regime_classifier or CryptoMarketRegimeClassifier()
        )
        self.volatility_classifier = (
            volatility_classifier or CryptoVolatilityClassifier()
        )
        self.intelligence_synthesizer = (
            intelligence_synthesizer
            or CryptoIntelligenceSynthesizer()
        )

    def run(self, context):
        self._validate_context(context)

        symbol = context["symbol"]
        snapshot = self.provider.get_snapshot(symbol)

        if not isinstance(snapshot, CryptoMarketSnapshot):
            raise TypeError(
                "Crypto market data provider must return "
                "a CryptoMarketSnapshot."
            )

        observation = CryptoMarketObservation(
            symbol=snapshot.symbol,
            timestamp=snapshot.timestamp,
            price=snapshot.price,
            volume=snapshot.volume,
            source=type(self.provider).__name__,
        )

        target = context.get("target", observation.symbol)

        finding = self.evidence_adapter.to_finding(
            observation,
            target=target,
        )

        if not isinstance(finding, Finding):
            raise TypeError(
                "Crypto evidence adapter must return a Finding."
            )

        result = {
            "module": self.name,
            "status": "ok",
            "symbol": observation.symbol,
            "timestamp": observation.timestamp,
            "price": observation.price,
            "volume": observation.volume,
            "observation": observation,
            "findings": [finding],
        }

        snapshots = context.get("snapshots")

        if snapshots is not None:
            regime = self.regime_classifier.classify(snapshots)

            if not isinstance(
                regime,
                CryptoMarketRegimeObservation,
            ):
                raise TypeError(
                    "Crypto regime classifier must return a "
                    "CryptoMarketRegimeObservation."
                )

            regime_finding = self._regime_to_finding(
                regime,
                target=target,
            )

            result["regime"] = regime
            result["findings"].append(regime_finding)

            volatility = self.volatility_classifier.classify(
                snapshots
            )

            if not isinstance(
                volatility,
                CryptoVolatilityObservation,
            ):
                raise TypeError(
                    "Crypto volatility classifier must return a "
                    "CryptoVolatilityObservation."
                )

            volatility_finding = self._volatility_to_finding(
                volatility,
                target=target,
            )

            result["volatility"] = volatility
            result["findings"].append(volatility_finding)

            intelligence = self.intelligence_synthesizer.synthesize(
                regime,
                volatility,
            )

            if not isinstance(
                intelligence,
                CryptoIntelligenceObservation,
            ):
                raise TypeError(
                    "Crypto intelligence synthesizer must return a "
                    "CryptoIntelligenceObservation."
                )

            intelligence_finding = self._intelligence_to_finding(
                intelligence,
                target=target,
            )

            result["intelligence"] = intelligence
            result["findings"].append(intelligence_finding)

        return result

    @staticmethod
    def _regime_to_finding(
        regime: CryptoMarketRegimeObservation,
        target: str,
    ) -> Finding:
        return Finding(
            title=(
                f"Crypto market regime: "
                f"{regime.symbol} / {regime.regime.value}"
            ),
            severity="info",
            description=(
                f"Classified {regime.symbol} market activity as "
                f"{regime.regime.value}."
            ),
            source="crypto_market_regime",
            target=target,
            evidence={
                "symbol": regime.symbol,
                "regime": regime.regime.value,
                "price_change_ratio": regime.price_change_ratio,
                "volume_ratio": regime.volume_ratio,
                "observation_count": regime.observation_count,
            },
        )

    @staticmethod
    def _volatility_to_finding(
        volatility: CryptoVolatilityObservation,
        target: str,
    ) -> Finding:
        return Finding(
            title=(
                f"Crypto volatility: "
                f"{volatility.symbol} / {volatility.regime.value}"
            ),
            severity="info",
            description=(
                f"Classified {volatility.symbol} price volatility as "
                f"{volatility.regime.value}."
            ),
            source="crypto_volatility",
            target=target,
            evidence={
                "symbol": volatility.symbol,
                "regime": volatility.regime.value,
                "realised_volatility": volatility.realised_volatility,
                "return_count": volatility.return_count,
                "observation_count": volatility.observation_count,
            },
        )

    @staticmethod
    def _intelligence_to_finding(
        intelligence: CryptoIntelligenceObservation,
        target: str,
    ) -> Finding:
        return Finding(
            title=(
                f"Crypto intelligence: "
                f"{intelligence.symbol} / {intelligence.state.value}"
            ),
            severity="info",
            description=(
                f"Combined {intelligence.symbol} market activity and "
                f"volatility classifications as "
                f"{intelligence.state.value}."
            ),
            source="crypto_intelligence_synthesis",
            target=target,
            evidence={
                "symbol": intelligence.symbol,
                "state": intelligence.state.value,
                "market_regime": intelligence.market_regime.value,
                "volatility_regime": (
                    intelligence.volatility_regime.value
                ),
            },
        )

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
