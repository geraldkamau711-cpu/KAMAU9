from core.assessment_comparison import AssessmentComparisonResult
from core.assessment_trend import AssessmentTrend


def test_assessment_trend_summarises_finding_count_changes():
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
        {
            "previous_assessment_id": "assessment-003",
            "current_assessment_id": "assessment-004",
            "finding_count_change": 0,
        },
    ]

    result = AssessmentTrend().summarise(comparisons)

    assert result == {
        "comparison_count": 3,
        "total_finding_count_change": 1,
        "increases": 1,
        "decreases": 1,
        "unchanged": 1,
        "latest_change": 0,
        "latest_direction": "unchanged",
    }


def test_assessment_trend_identifies_increasing_latest_change():
    comparisons = [
        {
            "previous_assessment_id": "assessment-001",
            "current_assessment_id": "assessment-002",
            "finding_count_change": 1,
        },
        {
            "previous_assessment_id": "assessment-002",
            "current_assessment_id": "assessment-003",
            "finding_count_change": 3,
        },
    ]

    result = AssessmentTrend().summarise(comparisons)

    assert result["comparison_count"] == 2
    assert result["total_finding_count_change"] == 4
    assert result["increases"] == 2
    assert result["decreases"] == 0
    assert result["unchanged"] == 0
    assert result["latest_change"] == 3
    assert result["latest_direction"] == "increased"


def test_assessment_trend_handles_empty_history():
    assert AssessmentTrend().summarise([]) == {
        "comparison_count": 0,
        "total_finding_count_change": 0,
        "increases": 0,
        "decreases": 0,
        "unchanged": 0,
        "latest_change": None,
        "latest_direction": "no_history",
    }


def test_assessment_trend_summarises_severity_changes():
    comparisons = [
        {
            "finding_count_change": 2,
            "severity_counts": {
                "previous": {
                    "high": 1,
                    "medium": 2,
                    "low": 3,
                },
                "current": {
                    "high": 2,
                    "medium": 3,
                    "low": 2,
                },
            },
        },
        {
            "finding_count_change": -1,
            "severity_counts": {
                "previous": {
                    "high": 2,
                    "medium": 3,
                    "low": 2,
                },
                "current": {
                    "high": 1,
                    "medium": 3,
                    "low": 2,
                },
            },
        },
    ]

    result = AssessmentTrend().summarise(comparisons)

    assert result["severity_changes"] == {
        "high": 0,
        "low": -1,
        "medium": 1,
    }


def test_assessment_trend_handles_missing_severity_levels():
    comparisons = [
        {
            "finding_count_change": 1,
            "severity_counts": {
                "previous": {
                    "high": 1,
                },
                "current": {
                    "medium": 2,
                },
            },
        },
    ]

    result = AssessmentTrend().summarise(comparisons)

    assert result["severity_changes"] == {
        "high": -1,
        "medium": 2,
    }


def test_assessment_trend_handles_empty_severity_history():
    comparisons = [
        {
            "finding_count_change": 0,
            "severity_counts": {
                "previous": {},
                "current": {},
            },
        },
    ]

    result = AssessmentTrend().summarise(comparisons)

    assert result["severity_changes"] == {}


def test_assessment_trend_summarises_module_execution_changes():
    comparisons = [
        {
            "finding_count_change": 2,
            "module_execution_counts": {
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
            },
        },
        {
            "finding_count_change": -1,
            "module_execution_counts": {
                "previous": {
                    "total": 3,
                    "succeeded": 2,
                    "failed": 1,
                },
                "current": {
                    "total": 3,
                    "succeeded": 3,
                    "failed": 0,
                },
            },
        },
    ]

    result = AssessmentTrend().summarise(comparisons)

    assert result["module_execution_changes"] == {
        "total": 1,
        "succeeded": 1,
        "failed": 0,
    }


def test_assessment_trend_summarises_source_changes():
    comparisons = [
        {
            "finding_count_change": 1,
            "new_sources": ["network_interfaces"],
            "removed_sources": [],
        },
        {
            "finding_count_change": 0,
            "new_sources": ["host_profile"],
            "removed_sources": ["network_interfaces"],
        },
        {
            "finding_count_change": -1,
            "new_sources": [],
            "removed_sources": ["host_profile"],
        },
    ]

    result = AssessmentTrend().summarise(comparisons)

    assert result["source_changes"] == {
        "new": 2,
        "removed": 2,
    }


def test_assessment_trend_preserves_legacy_source_history_compatibility():
    comparisons = [
        {
            "finding_count_change": 2,
        },
        {
            "finding_count_change": -1,
        },
    ]

    result = AssessmentTrend().summarise(comparisons)

    assert "source_changes" not in result


def test_assessment_trend_returns_typed_result():
    from core.assessment_trend_result import AssessmentTrendResult

    result = AssessmentTrend().summarise(
        [
            {
                "finding_count_change": 2,
            },
        ]
    )

    assert isinstance(result, AssessmentTrendResult)


def test_assessment_trend_result_preserves_dictionary_compatibility():
    result = AssessmentTrend().summarise(
        [
            {
                "finding_count_change": 2,
            },
        ]
    )

    assert result["latest_direction"] == "increased"
    assert result["total_finding_count_change"] == 2
    assert result == {
        "comparison_count": 1,
        "total_finding_count_change": 2,
        "increases": 1,
        "decreases": 0,
        "unchanged": 0,
        "latest_change": 2,
        "latest_direction": "increased",
    }


def test_assessment_trend_accepts_typed_comparison_result():
    comparison = AssessmentComparisonResult(
        previous_assessment_id="assessment-001",
        current_assessment_id="assessment-002",
        target_changed=False,
        finding_count_change=2,
        severity_counts={},
        module_execution_counts={},
        new_sources=[],
        removed_sources=[],
    )

    result = AssessmentTrend().summarise(
        [comparison],
    )

    assert result["total_finding_count_change"] == 2
    assert result["latest_direction"] == "increased"
