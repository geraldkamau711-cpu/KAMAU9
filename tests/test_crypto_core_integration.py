from datetime import datetime, timedelta, timezone

from core.config import K9Config
from core.main import K9Core
from core.mode import K9Mode
from core.finding import Finding
from modules.crypto.market_data import (
    CryptoMarketDataProvider,
    CryptoMarketSnapshot,
)
from modules.crypto.market_intelligence import CryptoMarketIntelligence
from modules.crypto.regime import CryptoMarketRegime


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
            45,
            tzinfo=timezone.utc,
        ),
        price=120000.50,
        volume=42.75,
    )


def _snapshot_history():
    first = _snapshot()

    return [
        first,
        CryptoMarketSnapshot(
            symbol=first.symbol,
            timestamp=first.timestamp + timedelta(minutes=1),
            price=121000.50,
            volume=85.50,
        ),
    ]


def _core():
    config = K9Config(mode=K9Mode.CRYPTO)
    core = K9Core(config=config)

    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    core.register_module(module)

    return core, provider


def test_crypto_core_runs_market_intelligence():
    core, provider = _core()

    context = core.start_assessment("crypto-assessment-001")

    result = core.run_module(
        "crypto_market_intelligence",
        {
            "symbol": "BTC/USDT",
        },
    )

    assert context.target == "crypto-assessment-001"
    assert provider.requested_symbol == "BTC/USDT"
    assert result["status"] == "ok"
    assert result["symbol"] == "BTC/USDT"


def test_crypto_core_passes_configured_mode_to_module():
    core, _ = _core()

    core.start_assessment("crypto-assessment-002")

    result = core.run_module(
        "crypto_market_intelligence",
        {
            "symbol": "BTC/USDT",
        },
    )

    assert result["status"] == "ok"
    assert core.config.mode is K9Mode.CRYPTO


def test_crypto_core_stores_crypto_finding_in_evidence():
    core, _ = _core()

    core.start_assessment("crypto-assessment-003")

    result = core.run_module(
        "crypto_market_intelligence",
        {
            "symbol": "BTC/USDT",
        },
    )

    findings = core.evidence.all()

    assert len(result["findings"]) == 1
    assert len(findings) == 1
    assert isinstance(findings[0], Finding)


def test_crypto_core_preserves_assessment_target_in_finding():
    core, _ = _core()

    core.start_assessment("crypto-assessment-004")

    core.run_module(
        "crypto_market_intelligence",
        {
            "symbol": "BTC/USDT",
        },
    )

    finding = core.evidence.all()[0]

    assert finding.target == "crypto-assessment-004"
    assert finding.source == "crypto_market_intelligence"
    assert finding.evidence["symbol"] == "BTC/USDT"
    assert finding.evidence["price"] == 120000.50
    assert finding.evidence["volume"] == 42.75


def test_crypto_core_passes_snapshot_history_to_regime_classifier():
    core, _ = _core()

    core.start_assessment("crypto-assessment-005")

    result = core.run_module(
        "crypto_market_intelligence",
        {
            "symbol": "BTC/USDT",
            "snapshots": _snapshot_history(),
        },
    )

    assert "regime" in result
    assert result["regime"].symbol == "BTC/USDT"
    assert result["regime"].regime is CryptoMarketRegime.HIGH_ACTIVITY


def test_crypto_core_stores_market_and_regime_findings():
    core, _ = _core()

    core.start_assessment("crypto-assessment-006")

    result = core.run_module(
        "crypto_market_intelligence",
        {
            "symbol": "BTC/USDT",
            "snapshots": _snapshot_history(),
        },
    )

    findings = core.evidence.all()

    assert len(result["findings"]) == 2
    assert len(findings) == 2
    assert all(isinstance(finding, Finding) for finding in findings)

    assert findings[0].source == "crypto_market_intelligence"
    assert findings[1].source == "crypto_market_regime"


def test_crypto_core_preserves_target_in_regime_finding():
    core, _ = _core()

    core.start_assessment("crypto-assessment-007")

    core.run_module(
        "crypto_market_intelligence",
        {
            "symbol": "BTC/USDT",
            "snapshots": _snapshot_history(),
        },
    )

    findings = core.evidence.all()
    regime_finding = findings[1]

    assert regime_finding.target == "crypto-assessment-007"
    assert regime_finding.evidence["symbol"] == "BTC/USDT"
    assert regime_finding.evidence["regime"] == "high_activity"
    assert regime_finding.evidence["observation_count"] == 2


def test_crypto_core_cannot_run_module_without_assessment():
    core, _ = _core()

    try:
        core.run_module(
            "crypto_market_intelligence",
            {
                "symbol": "BTC/USDT",
            },
        )
    except RuntimeError as exc:
        assert str(exc) == "No active assessment."
    else:
        raise AssertionError(
            "Expected RuntimeError when no assessment is active."
        )
