from core.evidence import EvidenceStore
from core.finding import Finding


def make_finding():
    return Finding(
        title="Test finding",
        severity="low",
        description="Test",
        source="test",
        target="lab-target",
    )


def test_evidence_store_adds_finding():
    store = EvidenceStore()

    store.add(make_finding())

    assert store.count() == 1
    assert store.all()[0].title == "Test finding"


def test_evidence_store_returns_copy():
    store = EvidenceStore()
    store.add(make_finding())

    findings = store.all()
    findings.clear()

    assert store.count() == 1


def test_evidence_store_clear():
    store = EvidenceStore()
    store.add(make_finding())

    store.clear()

    assert store.count() == 0
