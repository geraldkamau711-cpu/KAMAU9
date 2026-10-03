from dataclasses import FrozenInstanceError

import pytest

from core.assessment_trend_result import AssessmentTrendResult


def test_assessment_trend_result_stores_core_fields():
    result = AssessmentTrendResult(
        comparison_count=2,
        total_finding_count_change=3,
        increases=2,
        decreases=0,
        unchanged=0,
        latest_change=2,
        latest_direction="increased",
    )

    assert result.comparison_count == 2
    assert result.total_finding_count_change == 3
    assert result.increases == 2
    assert result.decreases == 0
    assert result.unchanged == 0
    assert result.latest_change == 2
    assert result.latest_direction == "increased"


def test_assessment_trend_result_defaults_optional_dimensions():
    result = AssessmentTrendResult(
        comparison_count=0,
        total_finding_count_change=0,
        increases=0,
        decreases=0,
        unchanged=0,
        latest_change=None,
        latest_direction="no_history",
    )

    assert result.severity_changes == {}
    assert result.module_execution_changes == {}
    assert result.source_changes == {}


def test_assessment_trend_result_preserves_intelligence_dimensions():
    result = AssessmentTrendResult(
        comparison_count=2,
        total_finding_count_change=3,
        increases=2,
        decreases=0,
        unchanged=0,
        latest_change=1,
        latest_direction="increased",
        severity_changes={
            "info": 1,
            "warning": 2,
        },
        module_execution_changes={
            "total": 1,
            "succeeded": 1,
            "failed": 0,
        },
        source_changes={
            "new": 2,
            "removed": 1,
        },
    )

    assert result.severity_changes == {
        "info": 1,
        "warning": 2,
    }
    assert result.module_execution_changes == {
        "total": 1,
        "succeeded": 1,
        "failed": 0,
    }
    assert result.source_changes == {
        "new": 2,
        "removed": 1,
    }


def test_assessment_trend_result_is_immutable():
    result = AssessmentTrendResult(
        comparison_count=1,
        total_finding_count_change=1,
        increases=1,
        decreases=0,
        unchanged=0,
        latest_change=1,
        latest_direction="increased",
    )

    with pytest.raises(FrozenInstanceError):
        result.latest_direction = "decreased"
