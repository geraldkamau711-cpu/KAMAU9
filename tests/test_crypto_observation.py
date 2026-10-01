from datetime import datetime, timezone

import pytest

from modules.crypto.observation import CryptoMarketObservation


def _observation():
    return CryptoMarketObservation(
        symbol="BTC/USDT",
        timestamp=datetime(
            2026,
            10,
            1,
            9,
            30,
            tzinfo=timezone.utc,
        ),
        price=120000.50,
        volume=42.75,
        source="fake_provider",
    )


def test_observation_stores_market_data():
    observation = _observation()

    assert observation.symbol == "BTC/USDT"
    assert observation.price == 120000.50
    assert observation.volume == 42.75
    assert observation.source == "fake_provider"
    assert observation.observation_type == "market_snapshot"


def test_observation_is_immutable():
    observation = _observation()

    with pytest.raises(AttributeError):
        observation.price = 100000


def test_observation_requires_non_empty_symbol():
    with pytest.raises(ValueError, match="symbol"):
        CryptoMarketObservation(
            symbol="",
            timestamp=_observation().timestamp,
            price=1,
            volume=1,
            source="test",
        )


def test_observation_requires_datetime():
    with pytest.raises(TypeError, match="timestamp"):
        CryptoMarketObservation(
            symbol="BTC/USDT",
            timestamp="2026-10-01T09:30:00Z",
            price=1,
            volume=1,
            source="test",
        )


def test_observation_rejects_negative_price():
    with pytest.raises(ValueError, match="price cannot be negative"):
        CryptoMarketObservation(
            symbol="BTC/USDT",
            timestamp=_observation().timestamp,
            price=-1,
            volume=1,
            source="test",
        )


def test_observation_rejects_negative_volume():
    with pytest.raises(ValueError, match="volume cannot be negative"):
        CryptoMarketObservation(
            symbol="BTC/USDT",
            timestamp=_observation().timestamp,
            price=1,
            volume=-1,
            source="test",
        )


def test_observation_requires_source():
    with pytest.raises(ValueError, match="source"):
        CryptoMarketObservation(
            symbol="BTC/USDT",
            timestamp=_observation().timestamp,
            price=1,
            volume=1,
            source="",
        )


def test_observation_requires_observation_type():
    with pytest.raises(ValueError, match="type"):
        CryptoMarketObservation(
            symbol="BTC/USDT",
            timestamp=_observation().timestamp,
            price=1,
            volume=1,
            source="test",
            observation_type="",
        )
