from core.assessment_persistence import AssessmentPersistence
from core.assessment_snapshot import AssessmentSnapshot
from core.main import K9Core


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


def test_snapshot_persistence_loads_legacy_snapshot_without_module_counts(
    tmp_path,
):
    legacy_snapshot = {
        "assessment_id": "assessment-legacy",
        "target": "localhost",
        "started_at": "2026-09-29T15:00:00+00:00",
        "finding_count": 2,
        "severity_counts": {"info": 2},
        "sources": ["host_intelligence"],
    }

    path = tmp_path / "assessment-legacy.json"
    path.write_text(
        __import__("json").dumps(legacy_snapshot),
        encoding="utf-8",
    )

    persistence = AssessmentPersistence(tmp_path)

    loaded = persistence.load("assessment-legacy")

    assert loaded.assessment_id == "assessment-legacy"
    assert loaded.finding_count == 2
    assert loaded.modules_total == 0
    assert loaded.modules_succeeded == 0
    assert loaded.modules_failed == 0


def test_k9_core_can_use_explicit_assessment_persistence(tmp_path):
    persistence = AssessmentPersistence(tmp_path)
    k9 = K9Core(persistence=persistence)

    assert k9.persistence is persistence


def test_k9_core_persistence_is_optional():
    k9 = K9Core()

    assert k9.persistence is None


def test_k9_core_can_save_current_assessment_snapshot(tmp_path):
    persistence = AssessmentPersistence(tmp_path)
    k9 = K9Core(persistence=persistence)

    k9.start_assessment("localhost")

    snapshot = k9.save_assessment_snapshot()

    assert snapshot.assessment_id == k9.context.assessment_id
    assert (tmp_path / f"{snapshot.assessment_id}.json").exists()


def test_k9_core_can_load_persisted_assessment_snapshot(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    snapshot = AssessmentSnapshot(
        assessment_id="assessment-load-001",
        target="localhost",
        started_at="2026-09-29T16:00:00+00:00",
        finding_count=4,
        severity_counts={"info": 3, "warning": 1},
        sources=["host_intelligence"],
        modules_total=2,
        modules_succeeded=2,
        modules_failed=0,
    )

    persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    loaded = k9.load_assessment_snapshot("assessment-load-001")

    assert loaded == snapshot
    assert k9.context is None


def test_k9_core_save_snapshot_requires_persistence():
    k9 = K9Core()

    k9.start_assessment("localhost")

    try:
        k9.save_assessment_snapshot()
    except RuntimeError as exc:
        assert str(exc) == "Assessment persistence is not configured."
    else:
        raise AssertionError("Expected RuntimeError")


def test_k9_core_load_snapshot_requires_persistence():
    k9 = K9Core()

    try:
        k9.load_assessment_snapshot("assessment-missing")
    except RuntimeError as exc:
        assert str(exc) == "Assessment persistence is not configured."
    else:
        raise AssertionError("Expected RuntimeError")


def test_list_assessments_returns_empty_list_when_directory_is_empty(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    assert persistence.list_assessments() == []


def test_list_assessments_returns_saved_assessment_ids(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    for assessment_id in ("assessment-002", "assessment-001"):
        snapshot = AssessmentSnapshot(
            assessment_id=assessment_id,
            target="localhost",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=1,
            severity_counts={"info": 1},
            sources=["host_intelligence"],
        )
        persistence.save(snapshot)

    assert persistence.list_assessments() == [
        "assessment-001",
        "assessment-002",
    ]


def test_list_assessments_ignores_non_json_files(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    snapshot = AssessmentSnapshot(
        assessment_id="assessment-json",
        target="localhost",
        started_at="2026-09-29T12:00:00+00:00",
        finding_count=1,
        severity_counts={"info": 1},
        sources=["host_intelligence"],
    )
    persistence.save(snapshot)

    (tmp_path / "notes.txt").write_text(
        "not an assessment",
        encoding="utf-8",
    )

    assert persistence.list_assessments() == ["assessment-json"]
