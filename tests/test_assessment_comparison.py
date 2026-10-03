from core.assessment_comparison import (
    AssessmentComparison,
    AssessmentComparisonResult,
)
from core.assessment_snapshot import AssessmentSnapshot


def test_comparison_returns_typed_result():
    previous = AssessmentSnapshot(
        assessment_id="assessment-001",
        target="localhost",
        started_at="2026-09-29T12:00:00+00:00",
        finding_count=2,
        severity_counts={"info": 2},
        sources=["host_intelligence"],
    )

    current = AssessmentSnapshot(
        assessment_id="assessment-002",
        target="localhost",
        started_at="2026-09-29T13:00:00+00:00",
        finding_count=4,
        severity_counts={"info": 3, "low": 1},
        sources=["host_intelligence", "network_interfaces"],
    )

    result = AssessmentComparison().compare(previous, current)

    assert isinstance(result, AssessmentComparisonResult)


def test_comparison_preserves_dictionary_compatibility():
    previous = AssessmentSnapshot(
        assessment_id="assessment-001",
        target="localhost",
        started_at="2026-09-29T12:00:00+00:00",
        finding_count=2,
        severity_counts={"info": 2},
        sources=["host_intelligence"],
    )

    current = AssessmentSnapshot(
        assessment_id="assessment-002",
        target="localhost",
        started_at="2026-09-29T13:00:00+00:00",
        finding_count=4,
        severity_counts={"info": 3, "low": 1},
        sources=["host_intelligence", "network_interfaces"],
    )

    result = AssessmentComparison().compare(previous, current)

    assert result["finding_count_change"] == 2
    assert result["previous_assessment_id"] == "assessment-001"
    assert result == {
        "previous_assessment_id": "assessment-001",
        "current_assessment_id": "assessment-002",
        "target_changed": False,
        "finding_count_change": 2,
        "severity_counts": {
            "previous": {"info": 2},
            "current": {"info": 3, "low": 1},
        },
        "module_execution_counts": {
            "previous": {
                "total": 0,
                "succeeded": 0,
                "failed": 0,
            },
            "current": {
                "total": 0,
                "succeeded": 0,
                "failed": 0,
            },
        },
        "new_sources": ["network_interfaces"],
        "removed_sources": [],
    }


def test_comparison_detects_finding_count_change():
    previous = AssessmentSnapshot(
        assessment_id="assessment-001",
        target="localhost",
        started_at="2026-09-29T12:00:00+00:00",
        finding_count=2,
        severity_counts={"info": 2},
        sources=["host_intelligence"],
    )

    current = AssessmentSnapshot(
        assessment_id="assessment-002",
        target="localhost",
        started_at="2026-09-29T13:00:00+00:00",
        finding_count=4,
        severity_counts={"info": 3, "low": 1},
        sources=["host_intelligence", "network_interfaces"],
    )

    comparison = AssessmentComparison()

    result = comparison.compare(previous, current)

    assert result["finding_count_change"] == 2


def test_comparison_detects_new_and_removed_sources():
    previous = AssessmentSnapshot(
        assessment_id="assessment-001",
        target="localhost",
        started_at="2026-09-29T12:00:00+00:00",
        finding_count=2,
        severity_counts={"info": 2},
        sources=["host_intelligence", "network_interfaces"],
    )

    current = AssessmentSnapshot(
        assessment_id="assessment-002",
        target="localhost",
        started_at="2026-09-29T13:00:00+00:00",
        finding_count=2,
        severity_counts={"info": 2},
        sources=["host_intelligence", "host_profile_intelligence"],
    )

    comparison = AssessmentComparison()

    result = comparison.compare(previous, current)

    assert result["new_sources"] == ["host_profile_intelligence"]
    assert result["removed_sources"] == ["network_interfaces"]


def test_comparison_detects_module_execution_count_changes():
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
        finding_count=3,
        severity_counts={"info": 2, "warning": 1},
        sources=["host_intelligence"],
        modules_total=3,
        modules_succeeded=2,
        modules_failed=1,
    )

    comparison = AssessmentComparison()

    result = comparison.compare(previous, current)

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
