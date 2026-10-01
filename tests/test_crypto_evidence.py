from datetime import datetime, timezone

import pytest

from core.finding import Finding
from modules.crypto.evidence import CryptoObservationEvidence
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
        source="FakeMarketDataProvider",
    )


def test_crypto_evidence_converts_observation_to_finding():
    adapter = CryptoObservationEvidence()

    finding = adapter.to_finding(
        _observation(),
        target="BTC/USDT",
    )

    assert isinstance(finding, Finding)


def test_crypto_evidence_sets_finding_metadata():
    adapter = CryptoObservationEvidence()

    finding = adapter.to_finding(
        _observation(),
        target="BTC/USDT",
    )

    assert finding.title == "Crypto market observation: BTC/USDT"
    assert finding.severity == "info"
    assert finding.source == "crypto_market_intelligence"
    assert finding.target == "BTC/USDT"


def test_crypto_evidence_preserves_observation_data():
    adapter = CryptoObservationEvidence()

    finding = adapter.to_finding(
        _observation(),
        target="BTC/USDT",
    )

    assert finding.evidence == {
        "symbol": "BTC/USDT",
        "timestamp": "2026-10-01T09:30:00+00:00",
        "price": 120000.50,
        "volume": 42.75,
        "source": "FakeMarketDataProvider",
        "observation_type": "market_snapshot",
    }


def test_crypto_evidence_requires_observation():
    adapter = CryptoObservationEvidence()

    with pytest.raises(
        TypeError,
        match="must be a CryptoMarketObservation",
    ):
        adapter.to_finding(
            None,
            target="BTC/USDT",
        )


def test_crypto_evidence_requires_target():
    adapter = CryptoObservationEvidence()

    with pytest.raises(
        ValueError,
        match="target must be a non-empty string",
    ):
        adapter.to_finding(
            _observation(),
            target="",
        )


def test_crypto_evidence_accepts_different_target():
    adapter = CryptoObservationEvidence()

    finding = adapter.to_finding(
        _observation(),
        target="crypto-assessment-001",
    )

    assert finding.target == "crypto-assessment-001"
