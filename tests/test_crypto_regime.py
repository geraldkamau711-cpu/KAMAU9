from datetime import datetime, timedelta, timezone

import pytest

from modules.crypto.market_data import CryptoMarketSnapshot
from modules.crypto.regime import (
    CryptoMarketRegime,
    CryptoMarketRegimeObservation,
    CryptoMarketRegimeClassifier,
    CryptoRegimeThresholds,
)


def _snapshot(
    price=100.0,
    volume=100.0,
    symbol="BTC/USDT",
    minutes=0,
):
    return CryptoMarketSnapshot(
        symbol=symbol,
        timestamp=datetime(
            2026,
            10,
            1,
            9,
            0,
            tzinfo=timezone.utc,
        )
        + timedelta(minutes=minutes),
        price=price,
        volume=volume,
    )


def test_default_thresholds_are_available():
    thresholds = CryptoRegimeThresholds()

    assert thresholds.high_volume_ratio == 2.0
    assert thresholds.price_expansion_ratio == 0.03


def test_thresholds_reject_non_positive_volume_ratio():
    with pytest.raises(
        ValueError,
        match="High-volume ratio must be greater than zero",
    ):
        CryptoRegimeThresholds(high_volume_ratio=0)


def test_thresholds_reject_non_positive_price_ratio():
    with pytest.raises(
        ValueError,
        match="Price-expansion ratio must be greater than zero",
    ):
        CryptoRegimeThresholds(price_expansion_ratio=0)


def test_empty_snapshots_return_insufficient_data():
    classifier = CryptoMarketRegimeClassifier()

    result = classifier.classify([])

    assert isinstance(result, CryptoMarketRegimeObservation)
    assert result.symbol == "unknown"
    assert result.regime is CryptoMarketRegime.INSUFFICIENT_DATA
    assert result.price_change_ratio is None
    assert result.volume_ratio is None
    assert result.observation_count == 0


def test_single_snapshot_returns_insufficient_data():
    classifier = CryptoMarketRegimeClassifier()

    result = classifier.classify([_snapshot()])

    assert result.regime is CryptoMarketRegime.INSUFFICIENT_DATA
    assert result.symbol == "BTC/USDT"
    assert result.observation_count == 1


def test_normal_activity_is_classified_as_normal():
    classifier = CryptoMarketRegimeClassifier()

    result = classifier.classify(
        [
            _snapshot(price=100.0, volume=100.0),
            _snapshot(price=101.0, volume=110.0, minutes=1),
        ]
    )

    assert result.regime is CryptoMarketRegime.NORMAL
    assert result.price_change_ratio == pytest.approx(0.01)
    assert result.volume_ratio == pytest.approx(1.10)


def test_low_activity_is_classified_as_quiet():
    classifier = CryptoMarketRegimeClassifier()

    result = classifier.classify(
        [
            _snapshot(price=100.0, volume=100.0),
            _snapshot(price=100.5, volume=50.0, minutes=1),
        ]
    )

    assert result.regime is CryptoMarketRegime.QUIET
    assert result.price_change_ratio == pytest.approx(0.005)
    assert result.volume_ratio == pytest.approx(0.50)


def test_high_volume_is_classified_as_high_activity():
    classifier = CryptoMarketRegimeClassifier()

    result = classifier.classify(
        [
            _snapshot(price=100.0, volume=100.0),
            _snapshot(price=101.0, volume=250.0, minutes=1),
        ]
    )

    assert result.regime is CryptoMarketRegime.HIGH_ACTIVITY
    assert result.volume_ratio == pytest.approx(2.50)


def test_large_price_move_is_classified_as_price_expansion():
    classifier = CryptoMarketRegimeClassifier()

    result = classifier.classify(
        [
            _snapshot(price=100.0, volume=100.0),
            _snapshot(price=104.0, volume=110.0, minutes=1),
        ]
    )

    assert result.regime is CryptoMarketRegime.PRICE_EXPANSION
    assert result.price_change_ratio == pytest.approx(0.04)


def test_price_expansion_takes_priority_over_high_volume():
    classifier = CryptoMarketRegimeClassifier()

    result = classifier.classify(
        [
            _snapshot(price=100.0, volume=100.0),
            _snapshot(price=105.0, volume=300.0, minutes=1),
        ]
    )

    assert result.regime is CryptoMarketRegime.PRICE_EXPANSION


def test_custom_thresholds_change_classification():
    thresholds = CryptoRegimeThresholds(
        high_volume_ratio=1.5,
        price_expansion_ratio=0.05,
    )
    classifier = CryptoMarketRegimeClassifier(thresholds)

    result = classifier.classify(
        [
            _snapshot(price=100.0, volume=100.0),
            _snapshot(price=102.0, volume=160.0, minutes=1),
        ]
    )

    assert result.regime is CryptoMarketRegime.HIGH_ACTIVITY


def test_snapshots_must_be_a_list():
    classifier = CryptoMarketRegimeClassifier()

    with pytest.raises(
        TypeError,
        match="snapshots must be a list",
    ):
        classifier.classify(None)


def test_snapshots_must_contain_market_snapshots():
    classifier = CryptoMarketRegimeClassifier()

    with pytest.raises(
        TypeError,
        match="must contain CryptoMarketSnapshot objects",
    ):
        classifier.classify([{"price": 100}])


def test_snapshots_must_use_same_symbol():
    classifier = CryptoMarketRegimeClassifier()

    with pytest.raises(
        ValueError,
        match="same symbol",
    ):
        classifier.classify(
            [
                _snapshot(symbol="BTC/USDT"),
                _snapshot(symbol="ETH/USDT", minutes=1),
            ]
        )


def test_previous_price_must_be_positive():
    classifier = CryptoMarketRegimeClassifier()

    previous = _snapshot(price=0)
    current = _snapshot(price=100, minutes=1)

    with pytest.raises(
        ValueError,
        match="Previous snapshot price must be greater than zero",
    ):
        classifier.classify([previous, current])


def test_previous_volume_must_be_positive():
    classifier = CryptoMarketRegimeClassifier()

    previous = _snapshot(volume=0)
    current = _snapshot(volume=100, minutes=1)

    with pytest.raises(
        ValueError,
        match="Previous snapshot volume must be greater than zero",
    ):
        classifier.classify([previous, current])


def test_regime_observation_rejects_empty_symbol():
    with pytest.raises(
        ValueError,
        match="symbol must be a non-empty string",
    ):
        CryptoMarketRegimeObservation(
            symbol="",
            regime=CryptoMarketRegime.NORMAL,
            price_change_ratio=0.01,
            volume_ratio=1.1,
            observation_count=2,
        )


def test_regime_observation_requires_enum_regime():
    with pytest.raises(
        TypeError,
        match="regime must be a CryptoMarketRegime",
    ):
        CryptoMarketRegimeObservation(
            symbol="BTC/USDT",
            regime="normal",
            price_change_ratio=0.01,
            volume_ratio=1.1,
            observation_count=2,
        )


def test_regime_observation_rejects_negative_count():
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        CryptoMarketRegimeObservation(
            symbol="BTC/USDT",
            regime=CryptoMarketRegime.NORMAL,
            price_change_ratio=0.01,
            volume_ratio=1.1,
            observation_count=-1,
        )
