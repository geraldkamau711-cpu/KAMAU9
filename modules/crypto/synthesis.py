from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from modules.crypto.regime import (
    CryptoMarketRegime,
    CryptoMarketRegimeObservation,
)
from modules.crypto.volatility import (
    CryptoVolatilityObservation,
    CryptoVolatilityRegime,
)


class CryptoIntelligenceState(str, Enum):
    """Deterministic combined crypto market-intelligence states."""

    INSUFFICIENT_DATA = "insufficient_data"
    QUIET_LOW_VOLATILITY = "quiet_low_volatility"
    NORMAL_ACTIVITY_NORMAL_VOLATILITY = (
        "normal_activity_normal_volatility"
    )
    HIGH_ACTIVITY_HIGH_VOLATILITY = "high_activity_high_volatility"
    PRICE_EXPANSION_HIGH_VOLATILITY = (
        "price_expansion_high_volatility"
    )
    HIGH_ACTIVITY_NORMAL_VOLATILITY = (
        "high_activity_normal_volatility"
    )
    PRICE_EXPANSION_NORMAL_VOLATILITY = (
        "price_expansion_normal_volatility"
    )
    OTHER = "other"


@dataclass(frozen=True)
class CryptoIntelligenceObservation:
    """Structured synthesis of independent crypto classifications."""

    symbol: str
    state: CryptoIntelligenceState
    market_regime: CryptoMarketRegime
    volatility_regime: CryptoVolatilityRegime

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError(
                "Intelligence observation symbol must be a "
                "non-empty string."
            )

        if not isinstance(self.state, CryptoIntelligenceState):
            raise TypeError(
                "Intelligence observation state must be a "
                "CryptoIntelligenceState."
            )

        if not isinstance(self.market_regime, CryptoMarketRegime):
            raise TypeError(
                "Intelligence observation market regime must be a "
                "CryptoMarketRegime."
            )

        if not isinstance(
            self.volatility_regime,
            CryptoVolatilityRegime,
        ):
            raise TypeError(
                "Intelligence observation volatility regime must be a "
                "CryptoVolatilityRegime."
            )


class CryptoIntelligenceSynthesizer:
    """Combine independent crypto regime observations deterministically."""

    def synthesize(
        self,
        market_regime: CryptoMarketRegimeObservation,
        volatility: CryptoVolatilityObservation,
    ) -> CryptoIntelligenceObservation:
        self._validate_inputs(market_regime, volatility)

        if market_regime.symbol != volatility.symbol:
            raise ValueError(
                "Crypto intelligence observations must use the same symbol."
            )

        state = self._classify_state(
            market_regime.regime,
            volatility.regime,
        )

        return CryptoIntelligenceObservation(
            symbol=market_regime.symbol,
            state=state,
            market_regime=market_regime.regime,
            volatility_regime=volatility.regime,
        )

    @staticmethod
    def _classify_state(
        market_regime: CryptoMarketRegime,
        volatility_regime: CryptoVolatilityRegime,
    ) -> CryptoIntelligenceState:
        if (
            market_regime is CryptoMarketRegime.INSUFFICIENT_DATA
            or volatility_regime
            is CryptoVolatilityRegime.INSUFFICIENT_DATA
        ):
            return CryptoIntelligenceState.INSUFFICIENT_DATA

        if (
            market_regime is CryptoMarketRegime.QUIET
            and volatility_regime is CryptoVolatilityRegime.LOW
        ):
            return CryptoIntelligenceState.QUIET_LOW_VOLATILITY

        if (
            market_regime is CryptoMarketRegime.NORMAL
            and volatility_regime is CryptoVolatilityRegime.NORMAL
        ):
            return (
                CryptoIntelligenceState
                .NORMAL_ACTIVITY_NORMAL_VOLATILITY
            )

        if (
            market_regime is CryptoMarketRegime.HIGH_ACTIVITY
            and volatility_regime is CryptoVolatilityRegime.HIGH
        ):
            return (
                CryptoIntelligenceState
                .HIGH_ACTIVITY_HIGH_VOLATILITY
            )

        if (
            market_regime is CryptoMarketRegime.PRICE_EXPANSION
            and volatility_regime is CryptoVolatilityRegime.HIGH
        ):
            return (
                CryptoIntelligenceState
                .PRICE_EXPANSION_HIGH_VOLATILITY
            )

        if (
            market_regime is CryptoMarketRegime.HIGH_ACTIVITY
            and volatility_regime is CryptoVolatilityRegime.NORMAL
        ):
            return (
                CryptoIntelligenceState
                .HIGH_ACTIVITY_NORMAL_VOLATILITY
            )

        if (
            market_regime is CryptoMarketRegime.PRICE_EXPANSION
            and volatility_regime is CryptoVolatilityRegime.NORMAL
        ):
            return (
                CryptoIntelligenceState
                .PRICE_EXPANSION_NORMAL_VOLATILITY
            )

        return CryptoIntelligenceState.OTHER

    @staticmethod
    def _validate_inputs(
        market_regime: CryptoMarketRegimeObservation,
        volatility: CryptoVolatilityObservation,
    ) -> None:
        if not isinstance(
            market_regime,
            CryptoMarketRegimeObservation,
        ):
            raise TypeError(
                "Market regime must be a "
                "CryptoMarketRegimeObservation."
            )

        if not isinstance(
            volatility,
            CryptoVolatilityObservation,
        ):
            raise TypeError(
                "Volatility must be a CryptoVolatilityObservation."
            )
