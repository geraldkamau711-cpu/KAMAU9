from core.assessment_snapshot import AssessmentSnapshot


def test_snapshot_stores_assessment_identity():
    snapshot = AssessmentSnapshot(
        assessment_id="assessment-123",
        target="localhost",
        started_at="2026-09-29T10:00:00+00:00",
        finding_count=3,
        severity_counts={
            "info": 2,
            "warning": 1,
        },
        sources=[
            "host_intelligence",
            "network_interfaces",
        ],
    )

    assert snapshot.assessment_id == "assessment-123"
    assert snapshot.target == "localhost"
    assert snapshot.started_at == "2026-09-29T10:00:00+00:00"


def test_snapshot_stores_assessment_statistics():
    snapshot = AssessmentSnapshot(
        assessment_id="assessment-123",
        target="localhost",
        started_at="2026-09-29T10:00:00+00:00",
        finding_count=3,
        severity_counts={
            "info": 2,
            "warning": 1,
        },
        sources=[
            "host_intelligence",
            "network_interfaces",
        ],
    )

    assert snapshot.finding_count == 3
    assert snapshot.severity_counts == {
        "info": 2,
        "warning": 1,
    }
    assert snapshot.sources == [
        "host_intelligence",
        "network_interfaces",
    ]


def test_snapshot_serialises_to_dict():
    snapshot = AssessmentSnapshot(
        assessment_id="assessment-123",
        target="localhost",
        started_at="2026-09-29T10:00:00+00:00",
        finding_count=1,
        severity_counts={"info": 1},
        sources=["host_intelligence"],
    )

    result = snapshot.to_dict()

    assert result == {
        "assessment_id": "assessment-123",
        "target": "localhost",
        "started_at": "2026-09-29T10:00:00+00:00",
        "finding_count": 1,
        "severity_counts": {"info": 1},
        "sources": ["host_intelligence"],
    }
