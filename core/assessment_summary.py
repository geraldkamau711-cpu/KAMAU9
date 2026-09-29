from core.finding import Finding


class AssessmentSummary:
    """Build a structured summary from assessment findings."""

    def __init__(self, target: str, assessment_id: str):
        self.target = target
        self.assessment_id = assessment_id

    def build(self, findings: list[Finding]) -> dict:
        severity_counts = {}
        sources = set()

        for finding in findings:
            severity_counts[finding.severity] = (
                severity_counts.get(finding.severity, 0) + 1
            )
            sources.add(finding.source)

        return {
            "target": self.target,
            "assessment_id": self.assessment_id,
            "finding_count": len(findings),
            "severity_counts": severity_counts,
            "sources": sorted(sources),
        }
