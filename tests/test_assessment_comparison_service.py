from core.assessment_comparison_service import (
    AssessmentComparisonService,
)
from core.assessment_persistence import AssessmentPersistence
from core.assessment_query import AssessmentQuery
from core.assessment_snapshot import AssessmentSnapshot


def make_snapshot(
    assessment_id,
    target,
    started_at,
    finding_count=1,
):
    return AssessmentSnapshot(
        assessment_id=assessment_id,
        target=target,
        started_at=started_at,
        finding_count=finding_count,
        severity_counts={"info": finding_count},
        sources=["host_intelligence"],
    )


def make_service(tmp_path):
    persistence = AssessmentPersistence(tmp_path)
    query = AssessmentQuery(persistence)

    return (
        persistence,
        AssessmentComparisonService(query),
    )


def test_service_compares_two_persisted_snapshots(tmp_path):
    persistence, service = make_service(tmp_path)

    persistence.save(
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
            finding_count=2,
        )
    )
    persistence.save(
        make_snapshot(
            "assessment-002",
            "host-a",
            "2026-09-29T13:00:00+00:00",
            finding_count=5,
        )
    )

    result = service.compare_assessment_snapshots(
        "assessment-001",
        "assessment-002",
    )

    assert result["finding_count_change"] == 3
    assert result["previous_assessment_id"] == "assessment-001"
    assert result["current_assessment_id"] == "assessment-002"


def test_service_compares_latest_snapshots_for_target(tmp_path):
    persistence, service = make_service(tmp_path)

    persistence.save(
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
            finding_count=2,
        )
    )
    persistence.save(
        make_snapshot(
            "assessment-002",
            "host-a",
            "2026-09-29T13:00:00+00:00",
            finding_count=4,
        )
    )

    result = service.compare_latest_assessment_snapshots_for_target(
        "host-a",
    )

    assert result is not None
    assert result["finding_count_change"] == 2
    assert result["previous_assessment_id"] == "assessment-001"
    assert result["current_assessment_id"] == "assessment-002"


def test_service_returns_none_without_two_snapshots(tmp_path):
    persistence, service = make_service(tmp_path)

    persistence.save(
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
        )
    )

    assert (
        service.compare_latest_assessment_snapshots_for_target(
            "host-a",
        )
        is None
    )


def test_service_compares_target_history(tmp_path):
    persistence, service = make_service(tmp_path)

    for snapshot in (
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
            finding_count=1,
        ),
        make_snapshot(
            "assessment-002",
            "host-a",
            "2026-09-29T13:00:00+00:00",
            finding_count=3,
        ),
        make_snapshot(
            "assessment-003",
            "host-a",
            "2026-09-29T14:00:00+00:00",
            finding_count=2,
        ),
    ):
        persistence.save(snapshot)

    result = service.compare_assessment_history_for_target(
        "host-a",
    )

    assert [
        comparison["finding_count_change"]
        for comparison in result
    ] == [
        2,
        -1,
    ]


def test_service_compares_latest_snapshots_for_all_targets(
    tmp_path,
):
    persistence, service = make_service(tmp_path)

    for snapshot in (
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
            finding_count=1,
        ),
        make_snapshot(
            "assessment-002",
            "host-a",
            "2026-09-29T13:00:00+00:00",
            finding_count=3,
        ),
        make_snapshot(
            "assessment-003",
            "host-b",
            "2026-09-29T14:00:00+00:00",
            finding_count=5,
        ),
        make_snapshot(
            "assessment-004",
            "host-b",
            "2026-09-29T15:00:00+00:00",
            finding_count=4,
        ),
    ):
        persistence.save(snapshot)

    result = (
        service.compare_latest_assessment_snapshots_for_all_targets()
    )

    assert result["host-a"]["finding_count_change"] == 2
    assert result["host-b"]["finding_count_change"] == -1
