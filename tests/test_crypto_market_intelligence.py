import pytest

from core.mode import K9Mode
from modules.crypto.market_intelligence import CryptoMarketIntelligence


def test_crypto_module_declares_crypto_and_analysis_support():
    module = CryptoMarketIntelligence()

    assert module.supports_mode(K9Mode.CRYPTO)
    assert module.supports_mode(K9Mode.ANALYSIS)
    assert not module.supports_mode(K9Mode.LAB)


def test_crypto_module_returns_structured_result():
    module = CryptoMarketIntelligence()

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
        }
    )

    assert result["module"] == "crypto_market_intelligence"
    assert result["status"] == "ok"
    assert result["symbol"] == "BTC/USDT"
    assert result["findings"] == []


def test_crypto_module_accepts_analysis_mode():
    module = CryptoMarketIntelligence()

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.ANALYSIS,
        }
    )

    assert result["status"] == "ok"


def test_crypto_module_rejects_lab_mode():
    module = CryptoMarketIntelligence()

    with pytest.raises(ValueError, match="cannot execute in mode"):
        module.run(
            {
                "symbol": "BTC/USDT",
                "mode": K9Mode.LAB,
            }
        )


def test_crypto_module_requires_symbol():
    module = CryptoMarketIntelligence()

    with pytest.raises(
        ValueError,
        match="Missing required crypto context: symbol",
    ):
        module.run({"mode": K9Mode.CRYPTO})


def test_crypto_module_requires_dictionary_context():
    module = CryptoMarketIntelligence()

    with pytest.raises(TypeError, match="context must be a dictionary"):
        module.run(None)


def test_crypto_module_requires_k9_mode():
    module = CryptoMarketIntelligence()

    with pytest.raises(TypeError, match="mode must be a K9Mode"):
        module.run(
            {
                "symbol": "BTC/USDT",
                "mode": "crypto",
            }
        )
