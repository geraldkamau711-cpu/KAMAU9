from datetime import datetime, timezone

import pytest

from modules.crypto.market_data import (
    CryptoMarketDataProvider,
    CryptoMarketSnapshot,
)


def test_market_snapshot_stores_normalised_market_data():
    timestamp = datetime(2026, 10, 1, 9, 30, tzinfo=timezone.utc)

    snapshot = CryptoMarketSnapshot(
        symbol="BTC/USDT",
        timestamp=timestamp,
        price=120000.50,
        volume=42.75,
    )

    assert snapshot.symbol == "BTC/USDT"
    assert snapshot.timestamp == timestamp
    assert snapshot.price == 120000.50
    assert snapshot.volume == 42.75


def test_market_snapshot_is_immutable():
    snapshot = CryptoMarketSnapshot(
        symbol="BTC/USDT",
        timestamp=datetime.now(timezone.utc),
        price=120000.0,
        volume=10.0,
    )

    with pytest.raises(AttributeError):
        snapshot.price = 121000.0


def test_market_snapshot_requires_symbol():
    with pytest.raises(ValueError, match="symbol must be a non-empty string"):
        CryptoMarketSnapshot(
            symbol="",
            timestamp=datetime.now(timezone.utc),
            price=120000.0,
            volume=10.0,
        )


def test_market_snapshot_requires_datetime():
    with pytest.raises(
        TypeError,
        match="timestamp must be a datetime",
    ):
        CryptoMarketSnapshot(
            symbol="BTC/USDT",
            timestamp="2026-10-01T09:30:00Z",
            price=120000.0,
            volume=10.0,
        )


def test_market_snapshot_rejects_negative_price():
    with pytest.raises(ValueError, match="price cannot be negative"):
        CryptoMarketSnapshot(
            symbol="BTC/USDT",
            timestamp=datetime.now(timezone.utc),
            price=-1.0,
            volume=10.0,
        )


def test_market_snapshot_rejects_negative_volume():
    with pytest.raises(ValueError, match="volume cannot be negative"):
        CryptoMarketSnapshot(
            symbol="BTC/USDT",
            timestamp=datetime.now(timezone.utc),
            price=120000.0,
            volume=-1.0,
        )


def test_market_data_provider_defines_snapshot_interface():
    provider = CryptoMarketDataProvider()

    with pytest.raises(NotImplementedError):
        provider.get_snapshot("BTC/USDT")
