from datetime import datetime, timedelta, timezone

import pytest

from core.finding import Finding
from core.mode import K9Mode
from modules.crypto.evidence import CryptoObservationEvidence
from modules.crypto.market_data import (
    CryptoMarketDataProvider,
    CryptoMarketSnapshot,
)
from modules.crypto.market_intelligence import CryptoMarketIntelligence
from modules.crypto.observation import CryptoMarketObservation
from modules.crypto.regime import (
    CryptoMarketRegime,
    CryptoMarketRegimeClassifier,
    CryptoMarketRegimeObservation,
)
from modules.crypto.volatility import (
    CryptoVolatilityClassifier,
    CryptoVolatilityObservation,
    CryptoVolatilityRegime,
)


class FakeMarketDataProvider(CryptoMarketDataProvider):
    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.requested_symbol = None

    def get_snapshot(self, symbol):
        self.requested_symbol = symbol
        return self.snapshot


def _snapshot(
    price=120000.50,
    volume=42.75,
    minutes=0,
):
    return CryptoMarketSnapshot(
        symbol="BTC/USDT",
        timestamp=datetime(
            2026,
            10,
            1,
            9,
            30,
            tzinfo=timezone.utc,
        )
        + timedelta(minutes=minutes),
        price=price,
        volume=volume,
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


def test_crypto_module_returns_finding():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
        }
    )

    assert len(result["findings"]) == 1
    assert isinstance(result["findings"][0], Finding)


def test_crypto_module_finding_contains_observation_evidence():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
            "target": "crypto-assessment-001",
        }
    )

    finding = result["findings"][0]

    assert finding.title == "Crypto market observation: BTC/USDT"
    assert finding.severity == "info"
    assert finding.source == "crypto_market_intelligence"
    assert finding.target == "crypto-assessment-001"
    assert finding.evidence["symbol"] == "BTC/USDT"
    assert finding.evidence["price"] == 120000.50
    assert finding.evidence["volume"] == 42.75
    assert finding.evidence["source"] == "FakeMarketDataProvider"


def test_crypto_module_uses_symbol_when_target_is_missing():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
        }
    )

    assert result["findings"][0].target == "BTC/USDT"


def test_crypto_module_accepts_custom_evidence_adapter():
    class RecordingAdapter(CryptoObservationEvidence):
        def __init__(self):
            self.received_observation = None
            self.received_target = None

        def to_finding(self, observation, target):
            self.received_observation = observation
            self.received_target = target
            return Finding(
                title="Custom crypto finding",
                severity="info",
                description="Custom",
                source="custom",
                target=target,
            )

    adapter = RecordingAdapter()
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(
        provider,
        evidence_adapter=adapter,
    )

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
            "target": "custom-target",
        }
    )

    assert result["findings"][0].title == "Custom crypto finding"
    assert adapter.received_observation.symbol == "BTC/USDT"
    assert adapter.received_target == "custom-target"


def test_crypto_module_rejects_invalid_evidence_adapter_result():
    class InvalidAdapter:
        def to_finding(self, observation, target):
            return {"target": target}

    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(
        provider,
        evidence_adapter=InvalidAdapter(),
    )

    with pytest.raises(
        TypeError,
        match="must return a Finding",
    ):
        module.run(
            {
                "symbol": "BTC/USDT",
                "mode": K9Mode.CRYPTO,
            }
        )


def test_crypto_module_uses_default_regime_classifier():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    assert isinstance(
        module.regime_classifier,
        CryptoMarketRegimeClassifier,
    )


def test_crypto_module_accepts_custom_regime_classifier():
    class RecordingClassifier:
        def __init__(self):
            self.received_snapshots = None

        def classify(self, snapshots):
            self.received_snapshots = snapshots

            return CryptoMarketRegimeObservation(
                symbol="BTC/USDT",
                regime=CryptoMarketRegime.NORMAL,
                price_change_ratio=0.01,
                volume_ratio=1.1,
                observation_count=len(snapshots),
            )

    classifier = RecordingClassifier()
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(
        provider,
        regime_classifier=classifier,
    )

    snapshots = [
        _snapshot(price=100.0, volume=100.0),
        _snapshot(
            price=101.0,
            volume=110.0,
            minutes=1,
        ),
    ]

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
            "snapshots": snapshots,
        }
    )

    assert classifier.received_snapshots == snapshots
    assert result["regime"].regime is CryptoMarketRegime.NORMAL


def test_crypto_module_returns_regime_observation():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    snapshots = [
        _snapshot(price=100.0, volume=100.0),
        _snapshot(
            price=101.0,
            volume=110.0,
            minutes=1,
        ),
    ]

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
            "snapshots": snapshots,
        }
    )

    regime = result["regime"]

    assert isinstance(regime, CryptoMarketRegimeObservation)
    assert regime.symbol == "BTC/USDT"
    assert regime.regime is CryptoMarketRegime.NORMAL
    assert regime.observation_count == 2


def test_crypto_module_returns_regime_finding():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    snapshots = [
        _snapshot(price=100.0, volume=100.0),
        _snapshot(
            price=105.0,
            volume=300.0,
            minutes=1,
        ),
    ]

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
            "target": "crypto-regime-001",
            "snapshots": snapshots,
        }
    )

    assert len(result["findings"]) == 4

    finding = result["findings"][1]

    assert isinstance(finding, Finding)
    assert finding.title == (
        "Crypto market regime: BTC/USDT / price_expansion"
    )
    assert finding.severity == "info"
    assert finding.source == "crypto_market_regime"
    assert finding.target == "crypto-regime-001"
    assert finding.evidence["symbol"] == "BTC/USDT"
    assert finding.evidence["regime"] == "price_expansion"
    assert finding.evidence["observation_count"] == 2


def test_crypto_module_uses_target_for_regime_finding():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
            "target": "custom-regime-target",
            "snapshots": [
                _snapshot(price=100.0, volume=100.0),
                _snapshot(
                    price=101.0,
                    volume=110.0,
                    minutes=1,
                ),
            ],
        }
    )

    assert result["findings"][1].target == "custom-regime-target"
    assert result["findings"][2].target == "custom-regime-target"


def test_crypto_module_accepts_insufficient_regime_data():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
            "snapshots": [
                _snapshot(),
            ],
        }
    )

    assert result["regime"].regime is (
        CryptoMarketRegime.INSUFFICIENT_DATA
    )
    assert len(result["findings"]) == 4
    assert result["findings"][1].evidence["regime"] == (
        "insufficient_data"
    )



def test_crypto_module_uses_default_volatility_classifier():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    assert isinstance(
        module.volatility_classifier,
        CryptoVolatilityClassifier,
    )


def test_crypto_module_accepts_custom_volatility_classifier():
    class RecordingClassifier:
        def __init__(self):
            self.received_snapshots = None

        def classify(self, snapshots):
            self.received_snapshots = snapshots

            return CryptoVolatilityObservation(
                symbol="BTC/USDT",
                regime=CryptoVolatilityRegime.NORMAL,
                realised_volatility=0.01,
                return_count=len(snapshots) - 1,
                observation_count=len(snapshots),
            )

    classifier = RecordingClassifier()
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(
        provider,
        volatility_classifier=classifier,
    )

    snapshots = [
        _snapshot(price=100.0, volume=100.0),
        _snapshot(
            price=101.0,
            volume=110.0,
            minutes=1,
        ),
        _snapshot(
            price=100.5,
            volume=105.0,
            minutes=2,
        ),
    ]

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
            "snapshots": snapshots,
        }
    )

    assert classifier.received_snapshots == snapshots
    assert result["volatility"].regime is CryptoVolatilityRegime.NORMAL


def test_crypto_module_returns_volatility_observation():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    snapshots = [
        _snapshot(price=100.0, volume=100.0),
        _snapshot(
            price=101.0,
            volume=110.0,
            minutes=1,
        ),
        _snapshot(
            price=100.5,
            volume=105.0,
            minutes=2,
        ),
    ]

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
            "snapshots": snapshots,
        }
    )

    volatility = result["volatility"]

    assert isinstance(volatility, CryptoVolatilityObservation)
    assert volatility.symbol == "BTC/USDT"
    assert volatility.return_count == 2
    assert volatility.observation_count == 3


def test_crypto_module_returns_volatility_finding():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    snapshots = [
        _snapshot(price=100.0, volume=100.0),
        _snapshot(
            price=105.0,
            volume=300.0,
            minutes=1,
        ),
    ]

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
            "target": "crypto-volatility-001",
            "snapshots": snapshots,
        }
    )

    assert len(result["findings"]) == 4

    finding = result["findings"][2]

    assert isinstance(finding, Finding)
    assert finding.title == "Crypto volatility: BTC/USDT / high"
    assert finding.severity == "info"
    assert finding.source == "crypto_volatility"
    assert finding.target == "crypto-volatility-001"
    assert finding.evidence["symbol"] == "BTC/USDT"
    assert finding.evidence["regime"] == "high"
    assert finding.evidence["return_count"] == 1
    assert finding.evidence["observation_count"] == 2


def test_crypto_module_uses_target_for_volatility_finding():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
            "target": "custom-volatility-target",
            "snapshots": [
                _snapshot(price=100.0, volume=100.0),
                _snapshot(
                    price=101.0,
                    volume=110.0,
                    minutes=1,
                ),
                _snapshot(
                    price=100.5,
                    volume=105.0,
                    minutes=2,
                ),
            ],
        }
    )

    assert result["findings"][2].target == "custom-volatility-target"


def test_crypto_module_accepts_insufficient_volatility_data():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
            "snapshots": [
                _snapshot(),
            ],
        }
    )

    assert result["volatility"].regime is (
        CryptoVolatilityRegime.INSUFFICIENT_DATA
    )
    assert len(result["findings"]) == 4
    assert result["findings"][2].evidence["regime"] == (
        "insufficient_data"
    )


def test_crypto_module_skips_volatility_when_snapshots_are_missing():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
        }
    )

    assert "volatility" not in result
    assert len(result["findings"]) == 1


def test_crypto_module_rejects_invalid_volatility_classifier_result():
    class InvalidClassifier:
        def classify(self, snapshots):
            return {"volatility": "normal"}

    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(
        provider,
        volatility_classifier=InvalidClassifier(),
    )

    with pytest.raises(
        TypeError,
        match="must return a CryptoVolatilityObservation",
    ):
        module.run(
            {
                "symbol": "BTC/USDT",
                "mode": K9Mode.CRYPTO,
                "snapshots": [
                    _snapshot(price=100.0, volume=100.0),
                    _snapshot(
                        price=101.0,
                        volume=110.0,
                        minutes=1,
                    ),
                ],
            }
        )


def test_crypto_module_skips_regime_when_snapshots_are_missing():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
        }
    )

    assert "regime" not in result
    assert len(result["findings"]) == 1


def test_crypto_module_rejects_invalid_regime_classifier_result():
    class InvalidClassifier:
        def classify(self, snapshots):
            return {"regime": "normal"}

    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(
        provider,
        regime_classifier=InvalidClassifier(),
    )

    with pytest.raises(
        TypeError,
        match="must return a CryptoMarketRegimeObservation",
    ):
        module.run(
            {
                "symbol": "BTC/USDT",
                "mode": K9Mode.CRYPTO,
                "snapshots": [
                    _snapshot(price=100.0, volume=100.0),
                    _snapshot(
                        price=101.0,
                        volume=110.0,
                        minutes=1,
                    ),
                ],
            }
        )


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
    assert isinstance(result["findings"][0], Finding)


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


def test_crypto_module_uses_default_intelligence_synthesizer():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    from modules.crypto.synthesis import CryptoIntelligenceSynthesizer

    assert isinstance(
        module.intelligence_synthesizer,
        CryptoIntelligenceSynthesizer,
    )


def test_crypto_module_returns_intelligence_observation():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    from modules.crypto.synthesis import (
        CryptoIntelligenceObservation,
        CryptoIntelligenceState,
    )

    snapshots = [
        _snapshot(price=100.0, volume=100.0),
        _snapshot(
            price=105.0,
            volume=300.0,
            minutes=1,
        ),
    ]

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
            "snapshots": snapshots,
        }
    )

    intelligence = result["intelligence"]

    assert isinstance(intelligence, CryptoIntelligenceObservation)
    assert intelligence.symbol == "BTC/USDT"
    assert intelligence.state is (
        CryptoIntelligenceState.PRICE_EXPANSION_HIGH_VOLATILITY
    )


def test_crypto_module_returns_intelligence_finding():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    snapshots = [
        _snapshot(price=100.0, volume=100.0),
        _snapshot(
            price=105.0,
            volume=300.0,
            minutes=1,
        ),
    ]

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
            "target": "crypto-intelligence-001",
            "snapshots": snapshots,
        }
    )

    assert len(result["findings"]) == 4

    finding = result["findings"][3]

    assert isinstance(finding, Finding)
    assert finding.title == (
        "Crypto intelligence: "
        "BTC/USDT / price_expansion_high_volatility"
    )
    assert finding.severity == "info"
    assert finding.source == "crypto_intelligence_synthesis"
    assert finding.target == "crypto-intelligence-001"
    assert finding.evidence["symbol"] == "BTC/USDT"
    assert finding.evidence["state"] == (
        "price_expansion_high_volatility"
    )
    assert finding.evidence["market_regime"] == "price_expansion"
    assert finding.evidence["volatility_regime"] == "high"


def test_crypto_module_uses_custom_intelligence_synthesizer():
    from modules.crypto.synthesis import (
        CryptoIntelligenceObservation,
        CryptoIntelligenceState,
    )

    class RecordingSynthesizer:
        def __init__(self):
            self.received_regime = None
            self.received_volatility = None

        def synthesize(self, market_regime, volatility):
            self.received_regime = market_regime
            self.received_volatility = volatility

            return CryptoIntelligenceObservation(
                symbol="BTC/USDT",
                state=CryptoIntelligenceState.OTHER,
                market_regime=market_regime.regime,
                volatility_regime=volatility.regime,
            )

    synthesizer = RecordingSynthesizer()
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(
        provider,
        intelligence_synthesizer=synthesizer,
    )

    snapshots = [
        _snapshot(price=100.0, volume=100.0),
        _snapshot(
            price=101.0,
            volume=110.0,
            minutes=1,
        ),
    ]

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
            "snapshots": snapshots,
        }
    )

    assert synthesizer.received_regime is result["regime"]
    assert synthesizer.received_volatility is result["volatility"]
    assert result["intelligence"].state is CryptoIntelligenceState.OTHER


def test_crypto_module_rejects_invalid_intelligence_synthesizer_result():
    class InvalidSynthesizer:
        def synthesize(self, market_regime, volatility):
            return {"state": "other"}

    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(
        provider,
        intelligence_synthesizer=InvalidSynthesizer(),
    )

    with pytest.raises(
        TypeError,
        match="must return a CryptoIntelligenceObservation",
    ):
        module.run(
            {
                "symbol": "BTC/USDT",
                "mode": K9Mode.CRYPTO,
                "snapshots": [
                    _snapshot(price=100.0, volume=100.0),
                    _snapshot(
                        price=101.0,
                        volume=110.0,
                        minutes=1,
                    ),
                ],
            }
        )


def test_crypto_module_skips_intelligence_when_snapshots_are_missing():
    provider = FakeMarketDataProvider(_snapshot())
    module = CryptoMarketIntelligence(provider)

    result = module.run(
        {
            "symbol": "BTC/USDT",
            "mode": K9Mode.CRYPTO,
        }
    )

    assert "intelligence" not in result
    assert len(result["findings"]) == 1
