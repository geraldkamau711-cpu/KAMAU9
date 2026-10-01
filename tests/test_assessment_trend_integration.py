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
