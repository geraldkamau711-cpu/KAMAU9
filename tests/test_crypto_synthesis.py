from datetime import datetime, timezone

import pytest

from modules.crypto.regime import (
    CryptoMarketRegime,
    CryptoMarketRegimeObservation,
)
from modules.crypto.synthesis import (
    CryptoIntelligenceObservation,
    CryptoIntelligenceState,
    CryptoIntelligenceSynthesizer,
)
from modules.crypto.volatility import (
    CryptoVolatilityObservation,
    CryptoVolatilityRegime,
)


def _market_regime(
    regime=CryptoMarketRegime.NORMAL,
    symbol="BTC/USDT",
):
    return CryptoMarketRegimeObservation(
        symbol=symbol,
        regime=regime,
        price_change_ratio=0.01,
        volume_ratio=1.1,
        observation_count=3,
    )


def _volatility(
    regime=CryptoVolatilityRegime.NORMAL,
    symbol="BTC/USDT",
):
    return CryptoVolatilityObservation(
        symbol=symbol,
        regime=regime,
        realised_volatility=0.01,
        return_count=2,
        observation_count=3,
    )


def test_normal_activity_and_normal_volatility():
    result = CryptoIntelligenceSynthesizer().synthesize(
        _market_regime(CryptoMarketRegime.NORMAL),
        _volatility(CryptoVolatilityRegime.NORMAL),
    )

    assert isinstance(result, CryptoIntelligenceObservation)
    assert result.symbol == "BTC/USDT"
    assert result.state is (
        CryptoIntelligenceState.NORMAL_ACTIVITY_NORMAL_VOLATILITY
    )


def test_quiet_activity_and_low_volatility():
    result = CryptoIntelligenceSynthesizer().synthesize(
        _market_regime(CryptoMarketRegime.QUIET),
        _volatility(CryptoVolatilityRegime.LOW),
    )

    assert result.state is (
        CryptoIntelligenceState.QUIET_LOW_VOLATILITY
    )


def test_high_activity_and_high_volatility():
    result = CryptoIntelligenceSynthesizer().synthesize(
        _market_regime(CryptoMarketRegime.HIGH_ACTIVITY),
        _volatility(CryptoVolatilityRegime.HIGH),
    )

    assert result.state is (
        CryptoIntelligenceState.HIGH_ACTIVITY_HIGH_VOLATILITY
    )


def test_price_expansion_and_high_volatility():
    result = CryptoIntelligenceSynthesizer().synthesize(
        _market_regime(CryptoMarketRegime.PRICE_EXPANSION),
        _volatility(CryptoVolatilityRegime.HIGH),
    )

    assert result.state is (
        CryptoIntelligenceState.PRICE_EXPANSION_HIGH_VOLATILITY
    )


def test_high_activity_and_normal_volatility():
    result = CryptoIntelligenceSynthesizer().synthesize(
        _market_regime(CryptoMarketRegime.HIGH_ACTIVITY),
        _volatility(CryptoVolatilityRegime.NORMAL),
    )

    assert result.state is (
        CryptoIntelligenceState.HIGH_ACTIVITY_NORMAL_VOLATILITY
    )


def test_price_expansion_and_normal_volatility():
    result = CryptoIntelligenceSynthesizer().synthesize(
        _market_regime(CryptoMarketRegime.PRICE_EXPANSION),
        _volatility(CryptoVolatilityRegime.NORMAL),
    )

    assert result.state is (
        CryptoIntelligenceState.PRICE_EXPANSION_NORMAL_VOLATILITY
    )


def test_insufficient_market_data_produces_insufficient_state():
    result = CryptoIntelligenceSynthesizer().synthesize(
        _market_regime(CryptoMarketRegime.INSUFFICIENT_DATA),
        _volatility(CryptoVolatilityRegime.NORMAL),
    )

    assert result.state is CryptoIntelligenceState.INSUFFICIENT_DATA


def test_insufficient_volatility_data_produces_insufficient_state():
    result = CryptoIntelligenceSynthesizer().synthesize(
        _market_regime(CryptoMarketRegime.NORMAL),
        _volatility(CryptoVolatilityRegime.INSUFFICIENT_DATA),
    )

    assert result.state is CryptoIntelligenceState.INSUFFICIENT_DATA


def test_unmapped_combination_returns_other():
    result = CryptoIntelligenceSynthesizer().synthesize(
        _market_regime(CryptoMarketRegime.QUIET),
        _volatility(CryptoVolatilityRegime.HIGH),
    )

    assert result.state is CryptoIntelligenceState.OTHER


def test_mismatched_symbols_are_rejected():
    with pytest.raises(
        ValueError,
        match="same symbol",
    ):
        CryptoIntelligenceSynthesizer().synthesize(
            _market_regime(symbol="BTC/USDT"),
            _volatility(symbol="ETH/USDT"),
        )


def test_invalid_market_regime_input_is_rejected():
    with pytest.raises(
        TypeError,
        match="Market regime must be",
    ):
        CryptoIntelligenceSynthesizer().synthesize(
            object(),
            _volatility(),
        )


def test_invalid_volatility_input_is_rejected():
    with pytest.raises(
        TypeError,
        match="Volatility must be",
    ):
        CryptoIntelligenceSynthesizer().synthesize(
            _market_regime(),
            object(),
        )


def test_observation_rejects_empty_symbol():
    with pytest.raises(
        ValueError,
        match="symbol must be a non-empty string",
    ):
        CryptoIntelligenceObservation(
            symbol="",
            state=CryptoIntelligenceState.OTHER,
            market_regime=CryptoMarketRegime.NORMAL,
            volatility_regime=CryptoVolatilityRegime.NORMAL,
        )


def test_observation_requires_state_enum():
    with pytest.raises(TypeError):
        CryptoIntelligenceObservation(
            symbol="BTC/USDT",
            state="other",  # type: ignore[arg-type]
            market_regime=CryptoMarketRegime.NORMAL,
            volatility_regime=CryptoVolatilityRegime.NORMAL,
        )


def test_observation_requires_market_regime_enum():
    with pytest.raises(TypeError):
        CryptoIntelligenceObservation(
            symbol="BTC/USDT",
            state=CryptoIntelligenceState.OTHER,
            market_regime="normal",  # type: ignore[arg-type]
            volatility_regime=CryptoVolatilityRegime.NORMAL,
        )


def test_observation_requires_volatility_regime_enum():
    with pytest.raises(TypeError):
        CryptoIntelligenceObservation(
            symbol="BTC/USDT",
            state=CryptoIntelligenceState.OTHER,
            market_regime=CryptoMarketRegime.NORMAL,
            volatility_regime="normal",  # type: ignore[arg-type]
        )
