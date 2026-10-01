from core.assessment_persistence import AssessmentPersistence
from core.assessment_snapshot import AssessmentSnapshot


def test_snapshot_can_be_saved_and_loaded(tmp_path):
    snapshot = AssessmentSnapshot(
        assessment_id="assessment-001",
        target="localhost",
        started_at="2026-09-29T12:00:00+00:00",
        finding_count=3,
        severity_counts={"info": 2, "low": 1},
        sources=["host_intelligence", "network_interfaces"],
    )

    persistence = AssessmentPersistence(tmp_path)

    persistence.save(snapshot)

    loaded = persistence.load("assessment-001")

    assert loaded == snapshot


def test_saved_snapshot_is_stored_as_json(tmp_path):
    snapshot = AssessmentSnapshot(
        assessment_id="assessment-002",
        target="localhost",
        started_at="2026-09-29T12:00:00+00:00",
        finding_count=1,
        severity_counts={"info": 1},
        sources=["host_intelligence"],
    )

    persistence = AssessmentPersistence(tmp_path)

    path = persistence.save(snapshot)

    assert path.exists()
    assert path.suffix == ".json"


def test_snapshot_persistence_preserves_module_execution_counts(tmp_path):
    snapshot = AssessmentSnapshot(
        assessment_id="assessment-003",
        target="localhost",
        started_at="2026-09-29T14:00:00+00:00",
        finding_count=3,
        severity_counts={"info": 2, "warning": 1},
        sources=["host_intelligence", "network_interfaces"],
        modules_total=3,
        modules_succeeded=2,
        modules_failed=1,
    )

    persistence = AssessmentPersistence(tmp_path)

    persistence.save(snapshot)

    loaded = persistence.load("assessment-003")

    assert loaded.modules_total == 3
    assert loaded.modules_succeeded == 2
    assert loaded.modules_failed == 1
