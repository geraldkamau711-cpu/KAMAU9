from datetime import datetime, timezone

import pytest

from core.mode import K9Mode
from modules.crypto.market_data import (
    CryptoMarketDataProvider,
    CryptoMarketSnapshot,
)
from modules.crypto.market_intelligence import CryptoMarketIntelligence
from modules.crypto.observation import CryptoMarketObservation


class FakeMarketDataProvider(CryptoMarketDataProvider):
    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.requested_symbol = None

    def get_snapshot(self, symbol):
        self.requested_symbol = symbol
        return self.snapshot


def _snapshot():
    return CryptoMarketSnapshot(
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
    )


def test_crypto_module_declares_crypto_and_analysis_support():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    assert module.supports_mode(K9Mode.CRYPTO)
    assert module.supports_mode(K9Mode.ANALYSIS)
    assert not module.supports_mode(K9Mode.LAB)


def test_crypto_module_consumes_market_data_provider():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
        }
    )

    assert provider.requested_symbol == "BTC/USDT"


def test_crypto_module_returns_market_snapshot_data():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
        }
    )

    assert result["module"] == "crypto_market_intelligence"
    assert result["status"] == "ok"
    assert result["symbol"] == "BTC/USDT"
    assert result["timestamp"] == _snapshot().timestamp
    assert result["price"] == 120000.50
    assert result["volume"] == 42.75
    assert result["findings"] == []


def test_crypto_module_returns_structured_observation():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
        }
    )

    observation = result["observation"]

    assert isinstance(observation, CryptoMarketObservation)
    assert observation.symbol == "BTC/USDT"
    assert observation.timestamp == _snapshot().timestamp
    assert observation.price == 120000.50
    assert observation.volume == 42.75
    assert observation.source == "FakeMarketDataProvider"
    assert observation.observation_type == "market_snapshot"


def test_crypto_module_observation_matches_snapshot():
    snapshot = _snapshot()
    provider = FakeMarketDataProvider(snapshot)
    module = CryptoMarketIntelligence(provider)

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
        }
    )

    observation = result["observation"]

    assert observation.symbol == snapshot.symbol
    assert observation.timestamp == snapshot.timestamp
    assert observation.price == snapshot.price
    assert observation.volume == snapshot.volume


def test_crypto_module_accepts_analysis_mode():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.ANALYSIS,
        }
    )

    assert result["status"] == "ok"
    assert isinstance(result["observation"], CryptoMarketObservation)


def test_crypto_module_rejects_lab_mode():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    with pytest.raises(ValueError, match="cannot execute in mode"):
        module.run(
            {
                "symbol": "BTC/USDT",
                "mode": K9Mode.LAB,
            }
        )


def test_crypto_module_requires_symbol():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    with pytest.raises(
        ValueError,
        match="Missing required crypto context: symbol",
    ):
        module.run({"mode": K9Mode.CRYPTO})


def test_crypto_module_requires_dictionary_context():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    with pytest.raises(TypeError, match="context must be a dictionary"):
        module.run(None)


def test_crypto_module_requires_k9_mode():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    with pytest.raises(TypeError, match="mode must be a K9Mode"):
        module.run(
            {
                "symbol": "BTC/USDT",
                "mode": "crypto",
            }
        )


def test_crypto_module_rejects_invalid_provider_result():
    class InvalidProvider(CryptoMarketDataProvider):
        def get_snapshot(self, symbol):
            return {"symbol": symbol}

    module = CryptoMarketIntelligence(InvalidProvider())

    with pytest.raises(
        TypeError,
        match="must return a CryptoMarketSnapshot",
    ):
        module.run(
            {
                "symbol": "BTC/USDT",
                "mode": K9Mode.CRYPTO,
            }
        )
