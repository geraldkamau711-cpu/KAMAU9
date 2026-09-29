from core.finding import Finding


def test_finding_creation():
    finding = Finding(
        title="Test finding",
        severity="low",
        description="Test description",
        source="test",
        target="lab-target",
    )

    assert finding.title == "Test finding"
    assert finding.severity == "low"
    assert finding.target == "lab-target"


def test_finding_serialisation():
    finding = Finding(
        title="Test finding",
        severity="low",
        description="Test description",
        source="test",
        target="lab-target",
        evidence={"port": 80},
    )

    data = finding.to_dict()

    assert data["evidence"]["port"] == 80
