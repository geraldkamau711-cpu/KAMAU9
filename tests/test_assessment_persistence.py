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


def test_k9_core_can_list_persisted_assessments(tmp_path):
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

    k9 = K9Core(persistence=persistence)

    assert k9.list_assessments() == [
        "assessment-001",
        "assessment-002",
    ]


def test_k9_core_list_assessments_requires_persistence():
    k9 = K9Core()

    try:
        k9.list_assessments()
    except RuntimeError as exc:
        assert str(exc) == "Assessment persistence is not configured."
    else:
        raise AssertionError("Expected RuntimeError")


def test_k9_core_can_load_all_persisted_assessment_snapshots(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    for assessment_id, finding_count in (
        ("assessment-002", 2),
        ("assessment-001", 1),
    ):
        snapshot = AssessmentSnapshot(
            assessment_id=assessment_id,
            target="localhost",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=finding_count,
            severity_counts={"info": finding_count},
            sources=["host_intelligence"],
        )
        persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    snapshots = k9.list_assessment_snapshots()

    assert [snapshot.assessment_id for snapshot in snapshots] == [
        "assessment-001",
        "assessment-002",
    ]
    assert [snapshot.finding_count for snapshot in snapshots] == [1, 2]


def test_k9_core_returns_empty_snapshot_history_when_nothing_is_persisted(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)
    k9 = K9Core(persistence=persistence)

    assert k9.list_assessment_snapshots() == []


def test_k9_core_snapshot_history_requires_persistence():
    k9 = K9Core()

    try:
        k9.list_assessment_snapshots()
    except RuntimeError as exc:
        assert str(exc) == "Assessment persistence is not configured."
    else:
        raise AssertionError("Expected RuntimeError")


def test_k9_core_can_load_latest_persisted_assessment_snapshot(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    for assessment_id, started_at in (
        ("assessment-001", "2026-09-29T12:00:00+00:00"),
        ("assessment-003", "2026-09-29T14:00:00+00:00"),
        ("assessment-002", "2026-09-29T13:00:00+00:00"),
    ):
        snapshot = AssessmentSnapshot(
            assessment_id=assessment_id,
            target="localhost",
            started_at=started_at,
            finding_count=1,
            severity_counts={"info": 1},
            sources=["host_intelligence"],
        )
        persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    latest = k9.get_latest_assessment_snapshot()

    assert latest is not None
    assert latest.assessment_id == "assessment-003"
    assert latest.started_at == "2026-09-29T14:00:00+00:00"


def test_k9_core_returns_none_when_no_assessment_snapshots_exist(tmp_path):
    persistence = AssessmentPersistence(tmp_path)
    k9 = K9Core(persistence=persistence)

    assert k9.get_latest_assessment_snapshot() is None


def test_k9_core_latest_snapshot_requires_persistence():
    k9 = K9Core()

    try:
        k9.get_latest_assessment_snapshot()
    except RuntimeError as exc:
        assert str(exc) == "Assessment persistence is not configured."
    else:
        raise AssertionError("Expected RuntimeError")


def test_k9_core_can_list_persisted_assessment_snapshots_for_target(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    for assessment_id, target in (
        ("assessment-003", "192.168.1.20"),
        ("assessment-001", "localhost"),
        ("assessment-002", "192.168.1.20"),
    ):
        snapshot = AssessmentSnapshot(
            assessment_id=assessment_id,
            target=target,
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=1,
            severity_counts={"info": 1},
            sources=["host_intelligence"],
        )
        persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    snapshots = k9.list_assessment_snapshots_for_target(
        "192.168.1.20"
    )

    assert [snapshot.assessment_id for snapshot in snapshots] == [
        "assessment-002",
        "assessment-003",
    ]



def test_k9_core_lists_target_snapshots_in_started_at_order(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    snapshots = (
        AssessmentSnapshot(
            assessment_id="assessment-003",
            target="192.168.1.20",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=1,
            severity_counts={"info": 1},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="192.168.1.20",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=3,
            severity_counts={"info": 3},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-002",
            target="192.168.1.20",
            started_at="2026-09-29T13:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host_intelligence"],
        ),
    )

    for snapshot in snapshots:
        persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    result = k9.list_assessment_snapshots_for_target(
        "192.168.1.20",
    )

    assert [snapshot.assessment_id for snapshot in result] == [
        "assessment-003",
        "assessment-002",
        "assessment-001",
    ]


def test_k9_core_returns_empty_history_for_unknown_target(tmp_path):
    persistence = AssessmentPersistence(tmp_path)
    snapshot = AssessmentSnapshot(
        assessment_id="assessment-001",
        target="localhost",
        started_at="2026-09-29T12:00:00+00:00",
        finding_count=1,
        severity_counts={"info": 1},
        sources=["host_intelligence"],
    )
    persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    assert k9.list_assessment_snapshots_for_target(
        "192.168.1.20"
    ) == []


def test_k9_core_target_snapshot_history_requires_persistence():
    k9 = K9Core()

    try:
        k9.list_assessment_snapshots_for_target("localhost")
    except RuntimeError as exc:
        assert str(exc) == "Assessment persistence is not configured."
    else:
        raise AssertionError("Expected RuntimeError")


def test_k9_core_can_load_latest_persisted_snapshot_for_target(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    for assessment_id, target, started_at in (
        (
            "assessment-001",
            "192.168.1.20",
            "2026-09-29T12:00:00+00:00",
        ),
        (
            "assessment-003",
            "192.168.1.20",
            "2026-09-29T14:00:00+00:00",
        ),
        (
            "assessment-002",
            "localhost",
            "2026-09-29T15:00:00+00:00",
        ),
    ):
        snapshot = AssessmentSnapshot(
            assessment_id=assessment_id,
            target=target,
            started_at=started_at,
            finding_count=1,
            severity_counts={"info": 1},
            sources=["host_intelligence"],
        )
        persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    latest = k9.get_latest_assessment_snapshot_for_target(
        "192.168.1.20"
    )

    assert latest is not None
    assert latest.assessment_id == "assessment-003"
    assert latest.target == "192.168.1.20"
    assert latest.started_at == "2026-09-29T14:00:00+00:00"


def test_k9_core_returns_none_when_target_has_no_snapshot_history(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)
    snapshot = AssessmentSnapshot(
        assessment_id="assessment-001",
        target="localhost",
        started_at="2026-09-29T12:00:00+00:00",
        finding_count=1,
        severity_counts={"info": 1},
        sources=["host_intelligence"],
    )
    persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    assert (
        k9.get_latest_assessment_snapshot_for_target(
            "192.168.1.20"
        )
        is None
    )


def test_k9_core_latest_target_snapshot_requires_persistence():
    k9 = K9Core()

    try:
        k9.get_latest_assessment_snapshot_for_target("localhost")
    except RuntimeError as exc:
        assert str(exc) == "Assessment persistence is not configured."
    else:
        raise AssertionError("Expected RuntimeError")


def test_k9_core_can_compare_persisted_assessment_snapshots(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    previous = AssessmentSnapshot(
        assessment_id="assessment-001",
        target="localhost",
        started_at="2026-09-29T12:00:00+00:00",
        finding_count=2,
        severity_counts={"info": 2},
        sources=["host_intelligence"],
        modules_total=2,
        modules_succeeded=2,
        modules_failed=0,
    )

    current = AssessmentSnapshot(
        assessment_id="assessment-002",
        target="localhost",
        started_at="2026-09-29T13:00:00+00:00",
        finding_count=4,
        severity_counts={"info": 3, "low": 1},
        sources=["host_intelligence", "network_interfaces"],
        modules_total=3,
        modules_succeeded=2,
        modules_failed=1,
    )

    persistence.save(previous)
    persistence.save(current)

    k9 = K9Core(persistence=persistence)

    result = k9.compare_assessment_snapshots(
        "assessment-001",
        "assessment-002",
    )

    assert result["previous_assessment_id"] == "assessment-001"
    assert result["current_assessment_id"] == "assessment-002"
    assert result["finding_count_change"] == 2
    assert result["new_sources"] == ["network_interfaces"]
    assert result["removed_sources"] == []
    assert result["module_execution_counts"] == {
        "previous": {
            "total": 2,
            "succeeded": 2,
            "failed": 0,
        },
        "current": {
            "total": 3,
            "succeeded": 2,
            "failed": 1,
        },
    }


def test_k9_core_compare_assessment_snapshots_requires_persistence():
    k9 = K9Core()

    try:
        k9.compare_assessment_snapshots(
            "assessment-001",
            "assessment-002",
        )
    except RuntimeError as exc:
        assert str(exc) == "Assessment persistence is not configured."
    else:
        raise AssertionError("Expected RuntimeError")


def test_k9_core_can_compare_latest_two_snapshots_for_target(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    snapshots = (
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="192.168.1.20",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-002",
            target="192.168.1.20",
            started_at="2026-09-29T13:00:00+00:00",
            finding_count=4,
            severity_counts={"info": 3, "low": 1},
            sources=["host_intelligence", "network_interfaces"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-003",
            target="localhost",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=8,
            severity_counts={"high": 1},
            sources=["host_intelligence"],
        ),
    )

    for snapshot in snapshots:
        persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    result = k9.compare_latest_assessment_snapshots_for_target(
        "192.168.1.20",
    )

    assert result is not None
    assert result["previous_assessment_id"] == "assessment-001"
    assert result["current_assessment_id"] == "assessment-002"
    assert result["finding_count_change"] == 2
    assert result["new_sources"] == ["network_interfaces"]
    assert result["removed_sources"] == []


def test_k9_core_target_history_comparison_uses_chronological_order(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    snapshots = (
        AssessmentSnapshot(
            assessment_id="assessment-003",
            target="192.168.1.20",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=1,
            severity_counts={"info": 1},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="192.168.1.20",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=5,
            severity_counts={"info": 5},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-002",
            target="192.168.1.20",
            started_at="2026-09-29T13:00:00+00:00",
            finding_count=3,
            severity_counts={"info": 3},
            sources=["host_intelligence"],
        ),
    )

    for snapshot in snapshots:
        persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    result = k9.compare_assessment_history_for_target(
        "192.168.1.20",
    )

    assert [
        (
            comparison["previous_assessment_id"],
            comparison["current_assessment_id"],
        )
        for comparison in result
    ] == [
        ("assessment-003", "assessment-002"),
        ("assessment-002", "assessment-001"),
    ]

    assert [comparison["finding_count_change"] for comparison in result] == [
        2,
        2,
    ]


def test_k9_core_returns_none_when_target_has_fewer_than_two_snapshots(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    persistence.save(
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="192.168.1.20",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host_intelligence"],
        )
    )

    k9 = K9Core(persistence=persistence)

    assert (
        k9.compare_latest_assessment_snapshots_for_target(
            "192.168.1.20",
        )
        is None
    )


def test_k9_core_latest_target_comparison_requires_persistence():
    k9 = K9Core()

    try:
        k9.compare_latest_assessment_snapshots_for_target(
            "localhost",
        )
    except RuntimeError as exc:
        assert str(exc) == "Assessment persistence is not configured."
    else:
        raise AssertionError("Expected RuntimeError")


def test_k9_core_can_compare_latest_snapshots_for_all_targets(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    snapshots = (
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="192.168.1.20",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-002",
            target="192.168.1.20",
            started_at="2026-09-29T13:00:00+00:00",
            finding_count=4,
            severity_counts={"info": 3, "low": 1},
            sources=["host_intelligence", "network_interfaces"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-003",
            target="localhost",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=1,
            severity_counts={"info": 1},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-004",
            target="localhost",
            started_at="2026-09-29T15:00:00+00:00",
            finding_count=3,
            severity_counts={"info": 2, "low": 1},
            sources=["host_intelligence", "network_interfaces"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-005",
            target="10.0.0.5",
            started_at="2026-09-29T16:00:00+00:00",
            finding_count=5,
            severity_counts={"medium": 5},
            sources=["network_interfaces"],
        ),
    )

    for snapshot in snapshots:
        persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    result = k9.compare_latest_assessment_snapshots_for_all_targets()

    assert list(result) == ["192.168.1.20", "localhost"]
    assert result["192.168.1.20"]["previous_assessment_id"] == (
        "assessment-001"
    )
    assert result["192.168.1.20"]["current_assessment_id"] == (
        "assessment-002"
    )
    assert result["192.168.1.20"]["finding_count_change"] == 2

    assert result["localhost"]["previous_assessment_id"] == (
        "assessment-003"
    )
    assert result["localhost"]["current_assessment_id"] == (
        "assessment-004"
    )
    assert result["localhost"]["finding_count_change"] == 2

    assert "10.0.0.5" not in result


def test_k9_core_returns_empty_comparison_map_when_no_target_has_history(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    persistence.save(
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="192.168.1.20",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host_intelligence"],
        )
    )

    k9 = K9Core(persistence=persistence)

    assert k9.compare_latest_assessment_snapshots_for_all_targets() == {}


def test_k9_core_all_target_comparison_requires_persistence():
    k9 = K9Core()

    try:
        k9.compare_latest_assessment_snapshots_for_all_targets()
    except RuntimeError as exc:
        assert str(exc) == "Assessment persistence is not configured."
    else:
        raise AssertionError("Expected RuntimeError")


def test_k9_core_can_compare_full_assessment_history_for_target(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    snapshots = (
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="192.168.1.20",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-002",
            target="192.168.1.20",
            started_at="2026-09-29T13:00:00+00:00",
            finding_count=4,
            severity_counts={"info": 3, "low": 1},
            sources=["host_intelligence", "network_interfaces"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-003",
            target="192.168.1.20",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=1,
            severity_counts={"info": 1},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-004",
            target="localhost",
            started_at="2026-09-29T15:00:00+00:00",
            finding_count=8,
            severity_counts={"high": 1},
            sources=["host_intelligence"],
        ),
    )

    for snapshot in snapshots:
        persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    result = k9.compare_assessment_history_for_target(
        "192.168.1.20",
    )

    assert len(result) == 2

    assert result[0]["previous_assessment_id"] == "assessment-001"
    assert result[0]["current_assessment_id"] == "assessment-002"
    assert result[0]["finding_count_change"] == 2

    assert result[1]["previous_assessment_id"] == "assessment-002"
    assert result[1]["current_assessment_id"] == "assessment-003"
    assert result[1]["finding_count_change"] == -3


def test_k9_core_returns_empty_history_when_target_has_fewer_than_two_snapshots(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    persistence.save(
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="192.168.1.20",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host_intelligence"],
        )
    )

    k9 = K9Core(persistence=persistence)

    assert (
        k9.compare_assessment_history_for_target(
            "192.168.1.20",
        )
        == []
    )


def test_k9_core_assessment_history_requires_persistence():
    k9 = K9Core()

    try:
        k9.compare_assessment_history_for_target(
            "localhost",
        )
    except RuntimeError as exc:
        assert str(exc) == "Assessment persistence is not configured."
    else:
        raise AssertionError("Expected RuntimeError")


def test_k9_core_can_list_persisted_assessment_targets(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    snapshots = (
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="localhost",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=1,
            severity_counts={"info": 1},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-002",
            target="192.168.1.20",
            started_at="2026-09-29T13:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-003",
            target="localhost",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=3,
            severity_counts={"info": 3},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-004",
            target="10.0.0.5",
            started_at="2026-09-29T15:00:00+00:00",
            finding_count=4,
            severity_counts={"info": 4},
            sources=["network_interfaces"],
        ),
    )

    for snapshot in snapshots:
        persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    assert k9.list_assessment_targets() == [
        "10.0.0.5",
        "192.168.1.20",
        "localhost",
    ]


def test_k9_core_assessment_target_listing_requires_persistence():
    k9 = K9Core()

    try:
        k9.list_assessment_targets()
    except RuntimeError as exc:
        assert str(exc) == "Assessment persistence is not configured."
    else:
        raise AssertionError("Expected RuntimeError")


def test_k9_core_can_group_persisted_assessment_snapshots_by_target(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    snapshots = (
        AssessmentSnapshot(
            assessment_id="assessment-003",
            target="localhost",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=3,
            severity_counts={"info": 3},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="localhost",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=1,
            severity_counts={"info": 1},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-004",
            target="10.0.0.5",
            started_at="2026-09-29T15:00:00+00:00",
            finding_count=4,
            severity_counts={"info": 4},
            sources=["network_interfaces"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-002",
            target="192.168.1.20",
            started_at="2026-09-29T13:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-005",
            target="localhost",
            started_at="2026-09-29T16:00:00+00:00",
            finding_count=5,
            severity_counts={"info": 5},
            sources=["host_intelligence"],
        ),
    )

    for snapshot in snapshots:
        persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    grouped = k9.list_assessment_snapshots_by_target()

    assert list(grouped) == [
        "10.0.0.5",
        "192.168.1.20",
        "localhost",
    ]

    assert [
        snapshot.assessment_id
        for snapshot in grouped["localhost"]
    ] == [
        "assessment-001",
        "assessment-003",
        "assessment-005",
    ]


def test_k9_core_returns_empty_target_snapshot_groups_when_none_are_persisted(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    k9 = K9Core(persistence=persistence)

    assert k9.list_assessment_snapshots_by_target() == {}


def test_k9_core_target_snapshot_grouping_requires_persistence():
    k9 = K9Core()

    try:
        k9.list_assessment_snapshots_by_target()
    except RuntimeError as exc:
        assert str(exc) == "Assessment persistence is not configured."
    else:
        raise AssertionError("Expected RuntimeError")


def test_k9_core_gets_latest_assessment_snapshot_for_target_from_grouped_snapshots(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    snapshots = (
        AssessmentSnapshot(
            assessment_id="assessment-003",
            target="localhost",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=3,
            severity_counts={"info": 3},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="localhost",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=1,
            severity_counts={"info": 1},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-002",
            target="192.168.1.20",
            started_at="2026-09-29T13:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host_intelligence"],
        ),
    )

    for snapshot in snapshots:
        persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    latest = k9.get_latest_assessment_snapshot_for_target(
        "localhost",
    )

    assert latest is not None
    assert latest.assessment_id == "assessment-003"


def test_k9_core_returns_none_for_latest_snapshot_of_unknown_target(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    persistence.save(
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="localhost",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=1,
            severity_counts={"info": 1},
            sources=["host_intelligence"],
        )
    )

    k9 = K9Core(persistence=persistence)

    assert (
        k9.get_latest_assessment_snapshot_for_target(
            "10.0.0.5",
        )
        is None
    )


def test_k9_core_latest_snapshot_for_target_requires_persistence():
    k9 = K9Core()

    try:
        k9.get_latest_assessment_snapshot_for_target(
            "localhost",
        )
    except RuntimeError as exc:
        assert str(exc) == "Assessment persistence is not configured."
    else:
        raise AssertionError("Expected RuntimeError")


def test_k9_core_can_get_latest_assessment_snapshot_for_each_target(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    snapshots = (
        AssessmentSnapshot(
            assessment_id="assessment-003",
            target="localhost",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=3,
            severity_counts={"info": 3},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="localhost",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=1,
            severity_counts={"info": 1},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-004",
            target="10.0.0.5",
            started_at="2026-09-29T15:00:00+00:00",
            finding_count=4,
            severity_counts={"info": 4},
            sources=["network_interfaces"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-002",
            target="192.168.1.20",
            started_at="2026-09-29T13:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-005",
            target="localhost",
            started_at="2026-09-29T16:00:00+00:00",
            finding_count=5,
            severity_counts={"info": 5},
            sources=["host_intelligence"],
        ),
    )

    for snapshot in snapshots:
        persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    latest = k9.get_latest_assessment_snapshots_by_target()

    assert list(latest) == [
        "10.0.0.5",
        "192.168.1.20",
        "localhost",
    ]

    assert latest["10.0.0.5"].assessment_id == "assessment-004"
    assert latest["192.168.1.20"].assessment_id == "assessment-002"
    assert latest["localhost"].assessment_id == "assessment-005"


def test_k9_core_returns_empty_latest_snapshot_mapping_when_none_are_persisted(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    k9 = K9Core(persistence=persistence)

    assert k9.get_latest_assessment_snapshots_by_target() == {}


def test_k9_core_latest_snapshot_mapping_requires_persistence():
    k9 = K9Core()

    try:
        k9.get_latest_assessment_snapshots_by_target()
    except RuntimeError as exc:
        assert str(exc) == "Assessment persistence is not configured."
    else:
        raise AssertionError("Expected RuntimeError")


def test_k9_core_compares_latest_assessment_snapshots_for_all_targets(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)

    snapshots = (
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="localhost",
            started_at="2026-09-29T12:00:00+00:00",
            finding_count=1,
            severity_counts={"info": 1},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-002",
            target="localhost",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=3,
            severity_counts={"info": 3},
            sources=["host_intelligence"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-003",
            target="10.0.0.5",
            started_at="2026-09-29T13:00:00+00:00",
            finding_count=2,
            severity_counts={"low": 2},
            sources=["network_interfaces"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-004",
            target="10.0.0.5",
            started_at="2026-09-29T15:00:00+00:00",
            finding_count=4,
            severity_counts={"low": 4},
            sources=["network_interfaces"],
        ),
    )

    for snapshot in snapshots:
        persistence.save(snapshot)

    k9 = K9Core(persistence=persistence)

    comparisons = k9.compare_latest_assessment_snapshots_for_all_targets()

    assert sorted(comparisons) == ["10.0.0.5", "localhost"]

    assert comparisons["10.0.0.5"]["previous_assessment_id"] == (
        "assessment-003"
    )
    assert comparisons["10.0.0.5"]["current_assessment_id"] == (
        "assessment-004"
    )

    assert comparisons["localhost"]["previous_assessment_id"] == (
        "assessment-001"
    )
    assert comparisons["localhost"]["current_assessment_id"] == (
        "assessment-002"
    )
