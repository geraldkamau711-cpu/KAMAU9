from core.assessment_comparison_service import AssessmentComparisonService
from core.assessment_persistence import AssessmentPersistence
from core.assessment_query import AssessmentQuery
from core.assessment_snapshot import AssessmentSnapshot
from core.assessment_trend_service import AssessmentTrendService


def make_snapshot(
    assessment_id,
    target,
    started_at,
    finding_count,
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
    comparison_service = AssessmentComparisonService(query)

    return (
        persistence,
        AssessmentTrendService(comparison_service),
    )


def test_service_accepts_comparison_service(tmp_path):
    persistence = AssessmentPersistence(tmp_path)
    query = AssessmentQuery(persistence)
    comparison_service = AssessmentComparisonService(query)

    service = AssessmentTrendService(comparison_service)

    assert service.comparison_service is comparison_service


def test_service_summarises_target_trend(tmp_path):
    persistence, service = make_service(tmp_path)

    persistence.save(
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
            2,
        )
    )
    persistence.save(
        make_snapshot(
            "assessment-002",
            "host-a",
            "2026-09-29T13:00:00+00:00",
            5,
        )
    )

    result = service.summarise_assessment_trend_for_target(
        "host-a",
    )

    assert result["comparison_count"] == 1
    assert result["total_finding_count_change"] == 3
    assert result["latest_change"] == 3
    assert result["latest_direction"] == "increased"


def test_service_analyse_target_trend(tmp_path):
    persistence, service = make_service(tmp_path)

    persistence.save(
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
            5,
        )
    )
    persistence.save(
        make_snapshot(
            "assessment-002",
            "host-a",
            "2026-09-29T13:00:00+00:00",
            3,
        )
    )

    result = service.analyse_assessment_trend_for_target(
        "host-a",
    )

    assert result["state"] == "decreased"
    assert result["finding_count_change"] == -2
    assert result["latest_direction"] == "decreased"


def test_service_summarises_trends_for_all_targets(tmp_path):
    persistence, service = make_service(tmp_path)

    for snapshot in (
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
            1,
        ),
        make_snapshot(
            "assessment-002",
            "host-a",
            "2026-09-29T13:00:00+00:00",
            3,
        ),
        make_snapshot(
            "assessment-003",
            "host-b",
            "2026-09-29T14:00:00+00:00",
            5,
        ),
        make_snapshot(
            "assessment-004",
            "host-b",
            "2026-09-29T15:00:00+00:00",
            4,
        ),
    ):
        persistence.save(snapshot)

    result = service.summarise_assessment_trends_for_all_targets()

    assert set(result) == {"host-a", "host-b"}

    assert result["host-a"]["total_finding_count_change"] == 2
    assert result["host-a"]["latest_direction"] == "increased"

    assert result["host-b"]["total_finding_count_change"] == -1
    assert result["host-b"]["latest_direction"] == "decreased"


def test_service_analyse_trends_for_all_targets(tmp_path):
    persistence, service = make_service(tmp_path)

    for snapshot in (
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
            1,
        ),
        make_snapshot(
            "assessment-002",
            "host-a",
            "2026-09-29T13:00:00+00:00",
            3,
        ),
        make_snapshot(
            "assessment-003",
            "host-b",
            "2026-09-29T14:00:00+00:00",
            5,
        ),
        make_snapshot(
            "assessment-004",
            "host-b",
            "2026-09-29T15:00:00+00:00",
            4,
        ),
    ):
        persistence.save(snapshot)

    result = service.analyse_assessment_trends_for_all_targets()

    assert set(result) == {"host-a", "host-b"}

    assert result["host-a"]["state"] == "increased"
    assert result["host-a"]["finding_count_change"] == 2

    assert result["host-b"]["state"] == "decreased"
    assert result["host-b"]["finding_count_change"] == -1


def test_service_accepts_assessment_intelligence():
    from core.assessment_intelligence import AssessmentIntelligence

    comparison_service = object()
    intelligence = AssessmentIntelligence()

    service = AssessmentTrendService(
        comparison_service,
        intelligence=intelligence,
    )

    assert service.intelligence is intelligence
