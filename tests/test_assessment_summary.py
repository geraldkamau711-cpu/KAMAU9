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


def test_empty_summary_has_no_modules():
    summary = AssessmentSummary(
        target="localhost",
        assessment_id="assessment-123",
    )

    result = summary.build([])

    assert result["modules"] == []


def test_summary_tracks_executed_modules():
    summary = AssessmentSummary(
        target="localhost",
        assessment_id="assessment-123",
    )

    result = summary.build(
        [],
        modules=[
            "network_interfaces",
            "host_intelligence",
        ],
    )

    assert result["modules"] == [
        "host_intelligence",
        "network_interfaces",
    ]


def test_summary_deduplicates_module_names():
    summary = AssessmentSummary(
        target="localhost",
        assessment_id="assessment-123",
    )

    result = summary.build(
        [],
        modules=[
            "host_intelligence",
            "host_intelligence",
            "network_interfaces",
        ],
    )

    assert result["modules"] == [
        "host_intelligence",
        "network_interfaces",
    ]


def test_summary_tracks_modules_with_findings():
    summary = AssessmentSummary(
        target="localhost",
        assessment_id="assessment-123",
    )

    result = summary.build(
        [
            make_finding("Host issue", "warning", "host_intelligence"),
            make_finding("Interface issue", "info", "network_interfaces"),
        ],
        modules=[
            "host_intelligence",
            "network_interfaces",
            "empty_module",
        ],
    )

    assert result["modules_with_findings"] == [
        "host_intelligence",
        "network_interfaces",
    ]


def test_summary_tracks_modules_without_findings():
    summary = AssessmentSummary(
        target="localhost",
        assessment_id="assessment-123",
    )

    result = summary.build(
        [
            make_finding("Host issue", "warning", "host_intelligence"),
        ],
        modules=[
            "host_intelligence",
            "network_interfaces",
            "empty_module",
        ],
    )

    assert result["modules_without_findings"] == [
        "empty_module",
        "network_interfaces",
    ]


def test_summary_empty_modules_have_no_status():
    summary = AssessmentSummary(
        target="localhost",
        assessment_id="assessment-123",
    )

    result = summary.build([])

    assert result["modules"] == []
    assert result["modules_with_findings"] == []
    assert result["modules_without_findings"] == []


def test_empty_summary_has_no_module_statuses():
    summary = AssessmentSummary(
        target="localhost",
        assessment_id="assessment-123",
    )

    result = summary.build([])

    assert result["module_statuses"] == {}


def test_summary_tracks_module_statuses():
    summary = AssessmentSummary(
        target="localhost",
        assessment_id="assessment-123",
    )

    result = summary.build(
        [],
        modules=[
            "host_intelligence",
            "network_interfaces",
        ],
        module_statuses={
            "network_interfaces": "success",
            "host_intelligence": "failed",
        },
    )

    assert result["module_statuses"] == {
        "host_intelligence": "failed",
        "network_interfaces": "success",
    }


def test_summary_sorts_module_statuses():
    summary = AssessmentSummary(
        target="localhost",
        assessment_id="assessment-123",
    )

    result = summary.build(
        [],
        module_statuses={
            "z_module": "success",
            "a_module": "failed",
            "m_module": "success",
        },
    )

    assert list(result["module_statuses"]) == [
        "a_module",
        "m_module",
        "z_module",
    ]


def test_summary_includes_failed_modules_in_executed_modules():
    summary = AssessmentSummary(
        target="localhost",
        assessment_id="assessment-123",
    )

    result = summary.build(
        [],
        module_statuses={
            "failing_module": "failed",
        },
    )

    assert result["modules"] == ["failing_module"]
    assert result["modules_with_findings"] == []
    assert result["modules_without_findings"] == [
        "failing_module",
    ]
