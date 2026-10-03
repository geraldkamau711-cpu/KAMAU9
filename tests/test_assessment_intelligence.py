from core.assessment_intelligence import AssessmentIntelligence


def test_assessment_intelligence_detects_increased_state():
    result = AssessmentIntelligence().analyse(
        {
            "comparison_count": 2,
            "total_finding_count_change": 3,
            "increases": 2,
            "decreases": 0,
            "unchanged": 0,
            "latest_change": 2,
            "latest_direction": "increased",
        }
    )

    assert result == {
        "state": "increased",
        "finding_count_change": 3,
        "latest_direction": "increased",
    }


def test_assessment_intelligence_detects_decreased_state():
    result = AssessmentIntelligence().analyse(
        {
            "comparison_count": 2,
            "total_finding_count_change": -2,
            "increases": 0,
            "decreases": 2,
            "unchanged": 0,
            "latest_change": -1,
            "latest_direction": "decreased",
        }
    )

    assert result == {
        "state": "decreased",
        "finding_count_change": -2,
        "latest_direction": "decreased",
    }


def test_assessment_intelligence_detects_stable_state():
    result = AssessmentIntelligence().analyse(
        {
            "comparison_count": 2,
            "total_finding_count_change": 0,
            "increases": 0,
            "decreases": 0,
            "unchanged": 2,
            "latest_change": 0,
            "latest_direction": "unchanged",
        }
    )

    assert result == {
        "state": "stable",
        "finding_count_change": 0,
        "latest_direction": "unchanged",
    }


def test_assessment_intelligence_detects_no_history():
    result = AssessmentIntelligence().analyse(
        {
            "comparison_count": 0,
            "total_finding_count_change": 0,
            "increases": 0,
            "decreases": 0,
            "unchanged": 0,
            "latest_change": None,
            "latest_direction": "no_history",
        }
    )

    assert result == {
        "state": "no_history",
        "finding_count_change": 0,
        "latest_direction": "no_history",
    }


def test_assessment_intelligence_rejects_unknown_direction():
    trend = {
        "comparison_count": 1,
        "total_finding_count_change": 1,
        "increases": 1,
        "decreases": 0,
        "unchanged": 0,
        "latest_change": 1,
        "latest_direction": "unknown",
    }

    try:
        AssessmentIntelligence().analyse(trend)
    except ValueError as exc:
        assert str(exc) == (
            "Unsupported assessment trend direction: 'unknown'"
        )
    else:
        raise AssertionError("Expected ValueError")


def test_assessment_intelligence_reports_severity_changes():
    result = AssessmentIntelligence().analyse(
        {
            "comparison_count": 1,
            "total_finding_count_change": 2,
            "increases": 1,
            "decreases": 0,
            "unchanged": 0,
            "latest_change": 2,
            "latest_direction": "increased",
            "severity_changes": {
                "info": 1,
                "warning": 1,
            },
        }
    )

    assert result == {
        "state": "increased",
        "finding_count_change": 2,
        "latest_direction": "increased",
        "severity_changes": {
            "info": 1,
            "warning": 1,
        },
    }


def test_assessment_intelligence_reports_negative_severity_changes():
    result = AssessmentIntelligence().analyse(
        {
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
        }
    )

    assert result == {
        "state": "decreased",
        "finding_count_change": -2,
        "latest_direction": "decreased",
        "severity_changes": {
            "warning": -2,
        },
    }


def test_assessment_intelligence_preserves_no_severity_history():
    result = AssessmentIntelligence().analyse(
        {
            "comparison_count": 1,
            "total_finding_count_change": 1,
            "increases": 1,
            "decreases": 0,
            "unchanged": 0,
            "latest_change": 1,
            "latest_direction": "increased",
        }
    )

    assert result == {
        "state": "increased",
        "finding_count_change": 1,
        "latest_direction": "increased",
    }


def test_assessment_intelligence_reports_module_execution_changes():
    result = AssessmentIntelligence().analyse(
        {
            "comparison_count": 1,
            "total_finding_count_change": 2,
            "increases": 1,
            "decreases": 0,
            "unchanged": 0,
            "latest_change": 2,
            "latest_direction": "increased",
            "module_execution_changes": {
                "total": 1,
                "succeeded": 1,
                "failed": 0,
            },
        }
    )

    assert result == {
        "state": "increased",
        "finding_count_change": 2,
        "latest_direction": "increased",
        "module_execution_changes": {
            "total": 1,
            "succeeded": 1,
            "failed": 0,
        },
    }

def test_assessment_intelligence_reports_source_changes():
    result = AssessmentIntelligence().analyse(
        {
            "comparison_count": 1,
            "total_finding_count_change": 1,
            "increases": 1,
            "decreases": 0,
            "unchanged": 0,
            "latest_change": 1,
            "latest_direction": "increased",
            "source_changes": {
                "new": 2,
                "removed": 1,
            },
        }
    )

    assert result == {
        "state": "increased",
        "finding_count_change": 1,
        "latest_direction": "increased",
        "source_changes": {
            "new": 2,
            "removed": 1,
        },
    }
