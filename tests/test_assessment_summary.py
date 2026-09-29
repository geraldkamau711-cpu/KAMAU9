from core.assessment_summary import AssessmentSummary
from core.finding import Finding


def make_finding(
    title,
    severity,
    source="test_module",
):
    return Finding(
        title=title,
        severity=severity,
        description="Test finding",
        source=source,
        target="localhost",
        evidence={},
    )


def test_empty_summary():
    summary = AssessmentSummary(
        target="localhost",
        assessment_id="assessment-123",
    )

    result = summary.build([])

    assert result["target"] == "localhost"
    assert result["assessment_id"] == "assessment-123"
    assert result["finding_count"] == 0
    assert result["severity_counts"] == {}
    assert result["sources"] == []


def test_summary_counts_findings_by_severity():
    findings = [
        make_finding("Info", "info"),
        make_finding("Warning", "warning"),
        make_finding("Critical", "critical"),
        make_finding("Another warning", "warning"),
    ]

    summary = AssessmentSummary(
        target="localhost",
        assessment_id="assessment-123",
    )

    result = summary.build(findings)

    assert result["finding_count"] == 4
    assert result["severity_counts"] == {
        "info": 1,
        "warning": 2,
        "critical": 1,
    }


def test_summary_tracks_unique_sources():
    findings = [
        make_finding("One", "info", "module_a"),
        make_finding("Two", "info", "module_a"),
        make_finding("Three", "warning", "module_b"),
    ]

    summary = AssessmentSummary(
        target="localhost",
        assessment_id="assessment-123",
    )

    result = summary.build(findings)

    assert result["sources"] == [
        "module_a",
        "module_b",
    ]
