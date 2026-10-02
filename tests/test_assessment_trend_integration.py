from core.assessment_trend import AssessmentTrend
from core.assessment_snapshot import AssessmentSnapshot
from core.main import K9Core


def test_k9_core_summarises_assessment_trend_for_target(tmp_path):
    core = K9Core()
    core.persistence = core.persistence or __import__(
        "core.assessment_persistence",
        fromlist=["AssessmentPersistence"],
    ).AssessmentPersistence(tmp_path)

    snapshots = [
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="localhost",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-002",
            target="localhost",
            started_at="2026-09-29T15:00:00+00:00",
            finding_count=4,
            severity_counts={"info": 4},
            sources=["host"],
        ),
        AssessmentSnapshot(
            assessment_id="assessment-003",
            target="localhost",
            started_at="2026-09-29T16:00:00+00:00",
            finding_count=3,
            severity_counts={"info": 3},
            sources=["host"],
        ),
    ]

    for snapshot in snapshots:
        core.persistence.save(snapshot)

    result = core.summarise_assessment_trend_for_target(
        "localhost",
    )

    assert result == {
        "comparison_count": 2,
        "total_finding_count_change": 1,
        "increases": 1,
        "decreases": 1,
        "unchanged": 0,
        "latest_change": -1,
        "latest_direction": "decreased",
        "severity_changes": {
            "info": 1,
        },
    }


def test_k9_core_returns_no_history_for_target_without_comparisons(
    tmp_path,
):
    core = K9Core()
    core.persistence = core.persistence or __import__(
        "core.assessment_persistence",
        fromlist=["AssessmentPersistence"],
    ).AssessmentPersistence(tmp_path)

    core.persistence.save(
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="localhost",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host"],
        )
    )

    result = core.summarise_assessment_trend_for_target(
        "localhost",
    )

    assert result == {
        "comparison_count": 0,
        "total_finding_count_change": 0,
        "increases": 0,
        "decreases": 0,
        "unchanged": 0,
        "latest_change": None,
        "latest_direction": "no_history",
    }


def test_assessment_trend_component_matches_core_history_input():
    comparisons = [
        {
            "previous_assessment_id": "assessment-001",
            "current_assessment_id": "assessment-002",
            "finding_count_change": 2,
        },
        {
            "previous_assessment_id": "assessment-002",
            "current_assessment_id": "assessment-003",
            "finding_count_change": -1,
        },
    ]

    assert AssessmentTrend().summarise(comparisons)["latest_direction"] == (
        "decreased"
    )

def test_k9_core_summarises_assessment_trends_for_all_targets(tmp_path):
    core = K9Core()
    core.persistence = core.persistence or __import__(
        "core.assessment_persistence",
        fromlist=["AssessmentPersistence"],
    ).AssessmentPersistence(tmp_path)

    snapshots = [
        AssessmentSnapshot(
            assessment_id="host-001",
            target="host-a",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host"],
        ),
        AssessmentSnapshot(
            assessment_id="host-002",
            target="host-a",
            started_at="2026-09-29T15:00:00+00:00",
            finding_count=4,
            severity_counts={"info": 4},
            sources=["host"],
        ),
        AssessmentSnapshot(
            assessment_id="host-b-001",
            target="host-b",
            started_at="2026-09-29T14:30:00+00:00",
            finding_count=5,
            severity_counts={"warning": 5},
            sources=["network"],
        ),
        AssessmentSnapshot(
            assessment_id="host-b-002",
            target="host-b",
            started_at="2026-09-29T15:30:00+00:00",
            finding_count=3,
            severity_counts={"warning": 3},
            sources=["network"],
        ),
    ]

    for snapshot in snapshots:
        core.persistence.save(snapshot)

    result = core.summarise_assessment_trends_for_all_targets()

    assert result == {
        "host-a": {
            "comparison_count": 1,
            "total_finding_count_change": 2,
            "increases": 1,
            "decreases": 0,
            "unchanged": 0,
            "latest_change": 2,
            "latest_direction": "increased",
            "severity_changes": {
                "info": 2,
            },
        },
        "host-b": {
            "comparison_count": 1,
            "total_finding_count_change": -2,
            "increases": 0,
            "decreases": 1,
            "unchanged": 0,
            "latest_change": -2,
            "latest_direction": "decreased",
            "severity_changes": {
                "warning": -2,
            },
        },
    }


def test_k9_core_rejects_all_target_trend_summary_without_persistence():
    core = K9Core()

    try:
        core.summarise_assessment_trends_for_all_targets()
    except RuntimeError as exc:
        assert str(exc) == (
            "Assessment persistence is not configured."
        )
    else:
        raise AssertionError("Expected RuntimeError")


def test_k9_core_analyse_assessment_trend_for_target(tmp_path):
    core = K9Core()
    core.persistence = core.persistence or __import__(
        "core.assessment_persistence",
        fromlist=["AssessmentPersistence"],
    ).AssessmentPersistence(tmp_path)

    core.persistence.save(
        AssessmentSnapshot(
            assessment_id="assessment-001",
            target="localhost",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host"],
        )
    )

    core.persistence.save(
        AssessmentSnapshot(
            assessment_id="assessment-002",
            target="localhost",
            started_at="2026-09-29T15:00:00+00:00",
            finding_count=5,
            severity_counts={"info": 5},
            sources=["host"],
        )
    )

    result = core.analyse_assessment_trend_for_target(
        "localhost",
    )

    assert result == {
        "state": "increased",
        "finding_count_change": 3,
        "latest_direction": "increased",
        "severity_changes": {
            "info": 3,
        },
    }


def test_k9_core_analyse_assessment_trends_for_all_targets(tmp_path):
    core = K9Core()
    core.persistence = core.persistence or __import__(
        "core.assessment_persistence",
        fromlist=["AssessmentPersistence"],
    ).AssessmentPersistence(tmp_path)

    core.persistence.save(
        AssessmentSnapshot(
            assessment_id="assessment-a-001",
            target="host-a",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=2,
            severity_counts={"info": 2},
            sources=["host"],
        )
    )

    core.persistence.save(
        AssessmentSnapshot(
            assessment_id="assessment-a-002",
            target="host-a",
            started_at="2026-09-29T15:00:00+00:00",
            finding_count=5,
            severity_counts={"info": 5},
            sources=["host"],
        )
    )

    core.persistence.save(
        AssessmentSnapshot(
            assessment_id="assessment-b-001",
            target="host-b",
            started_at="2026-09-29T14:00:00+00:00",
            finding_count=5,
            severity_counts={"warning": 5},
            sources=["network"],
        )
    )

    core.persistence.save(
        AssessmentSnapshot(
            assessment_id="assessment-b-002",
            target="host-b",
            started_at="2026-09-29T15:00:00+00:00",
            finding_count=3,
            severity_counts={"warning": 3},
            sources=["network"],
        )
    )

    result = core.analyse_assessment_trends_for_all_targets()

    assert result == {
        "host-a": {
            "state": "increased",
            "finding_count_change": 3,
            "latest_direction": "increased",
            "severity_changes": {
                "info": 3,
            },
        },
        "host-b": {
            "state": "decreased",
            "finding_count_change": -2,
            "latest_direction": "decreased",
            "severity_changes": {
                "warning": -2,
            },
        },
    }
