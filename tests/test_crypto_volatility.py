from datetime import datetime, timedelta, timezone

import pytest

from modules.crypto.market_data import CryptoMarketSnapshot
from modules.crypto.volatility import (
    CryptoVolatilityClassifier,
    CryptoVolatilityObservation,
    CryptoVolatilityRegime,
    CryptoVolatilityThresholds,
)


def _snapshot(price, minute=0, volume=10.0):
    return CryptoMarketSnapshot(
        symbol="BTC/USDT",
        timestamp=datetime(
            2026,
            10,
            1,
            9,
            45,
            tzinfo=timezone.utc,
        ) + timedelta(minutes=minute),
        price=price,
        volume=volume,
    )


def test_default_thresholds_are_valid():
    thresholds = CryptoVolatilityThresholds()

    assert thresholds.low == 0.005
    assert thresholds.high == 0.02


def test_thresholds_require_positive_low_value():
    with pytest.raises(
        ValueError,
        match="Low-volatility threshold",
    ):
        CryptoVolatilityThresholds(low=0)


def test_thresholds_require_high_above_low():
    with pytest.raises(
        ValueError,
        match="High-volatility threshold",
    ):
        CryptoVolatilityThresholds(low=0.02, high=0.01)


def test_classifier_returns_insufficient_data_for_empty_snapshots():
    result = CryptoVolatilityClassifier().classify([])

    assert isinstance(result, CryptoVolatilityObservation)
    assert result.symbol == "unknown"
    assert result.regime is CryptoVolatilityRegime.INSUFFICIENT_DATA
    assert result.realised_volatility is None
    assert result.return_count == 0
    assert result.observation_count == 0


def test_classifier_returns_insufficient_data_for_one_snapshot():
    result = CryptoVolatilityClassifier().classify(
        [_snapshot(100.0)]
    )

    assert result.symbol == "BTC/USDT"
    assert result.regime is CryptoVolatilityRegime.INSUFFICIENT_DATA
    assert result.realised_volatility is None
    assert result.return_count == 0
    assert result.observation_count == 1


def test_classifier_accepts_two_snapshots():
    result = CryptoVolatilityClassifier().classify(
        [
            _snapshot(100.0),
            _snapshot(100.4, minute=1),
        ]
    )

    assert result.regime is CryptoVolatilityRegime.LOW
    assert result.return_count == 1
    assert result.observation_count == 2
    assert result.realised_volatility == pytest.approx(0.004)


def test_classifier_detects_low_volatility():
    result = CryptoVolatilityClassifier().classify(
        [
            _snapshot(100.0),
            _snapshot(100.4, minute=1),
            _snapshot(100.1, minute=2),
        ]
    )

    assert result.regime is CryptoVolatilityRegime.LOW
    assert result.realised_volatility is not None
    assert result.realised_volatility < 0.005


def test_classifier_detects_normal_volatility():
    result = CryptoVolatilityClassifier().classify(
        [
            _snapshot(100.0),
            _snapshot(101.0, minute=1),
            _snapshot(99.5, minute=2),
            _snapshot(100.5, minute=3),
        ]
    )

    assert result.regime is CryptoVolatilityRegime.NORMAL
    assert result.realised_volatility is not None
    assert 0.005 <= result.realised_volatility < 0.02


def test_classifier_detects_high_volatility():
    result = CryptoVolatilityClassifier().classify(
        [
            _snapshot(100.0),
            _snapshot(103.0, minute=1),
            _snapshot(97.0, minute=2),
        ]
    )

    assert result.regime is CryptoVolatilityRegime.HIGH
    assert result.realised_volatility is not None
    assert result.realised_volatility >= 0.02


def test_classifier_accepts_custom_thresholds():
    classifier = CryptoVolatilityClassifier(
        CryptoVolatilityThresholds(
            low=0.01,
            high=0.05,
        )
    )

    result = classifier.classify(
        [
            _snapshot(100.0),
            _snapshot(102.0, minute=1),
        ]
    )

    assert result.regime is CryptoVolatilityRegime.NORMAL


def test_classifier_rejects_non_list_snapshots():
    with pytest.raises(
        TypeError,
        match="snapshots must be a list",
    ):
        CryptoVolatilityClassifier().classify(())  # type: ignore[arg-type]


def test_classifier_rejects_invalid_snapshot_type():
    with pytest.raises(
        TypeError,
        match="must contain CryptoMarketSnapshot",
    ):
        CryptoVolatilityClassifier().classify([object()])


def test_classifier_rejects_mixed_symbols():
    snapshots = [
        _snapshot(100.0),
        CryptoMarketSnapshot(
            symbol="ETH/USDT",
            timestamp=datetime(
                2026,
                10,
                1,
                9,
                46,
                tzinfo=timezone.utc,
            ),
            price=101.0,
            volume=10.0,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="same symbol",
    ):
        CryptoVolatilityClassifier().classify(snapshots)


def test_classifier_rejects_non_positive_prices():
    with pytest.raises(
        ValueError,
        match="prices must be greater than zero",
    ):
        CryptoVolatilityClassifier().classify(
            [
                _snapshot(100.0),
                _snapshot(0.0, minute=1),
            ]
        )


def test_observation_rejects_invalid_regime():
    with pytest.raises(TypeError):
        CryptoVolatilityObservation(
            symbol="BTC/USDT",
            regime="high",  # type: ignore[arg-type]
            realised_volatility=0.03,
            return_count=1,
            observation_count=2,
        )


def test_observation_rejects_negative_volatility():
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        CryptoVolatilityObservation(
            symbol="BTC/USDT",
            regime=CryptoVolatilityRegime.HIGH,
            realised_volatility=-0.01,
            return_count=1,
            observation_count=2,
        )


def test_observation_rejects_negative_counts():
    with pytest.raises(
        ValueError,
        match="return count cannot be negative",
    ):
        CryptoVolatilityObservation(
            symbol="BTC/USDT",
            regime=CryptoVolatilityRegime.LOW,
            realised_volatility=0.001,
            return_count=-1,
            observation_count=2,
        )
