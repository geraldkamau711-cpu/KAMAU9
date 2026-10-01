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
