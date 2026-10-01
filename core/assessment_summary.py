from collections.abc import Iterable, Mapping

from core.finding import Finding


class AssessmentSummary:
    """Build a structured summary from assessment findings."""

    def __init__(self, target: str, assessment_id: str):
        self.target = target
        self.assessment_id = assessment_id

    def build(
        self,
        findings: list[Finding],
        modules: Iterable[str] = (),
        module_statuses: Mapping[str, str] | None = None,
    ) -> dict:
        severity_counts = {}
        sources = set()
        modules_with_findings = set()

        for finding in findings:
            severity_counts[finding.severity] = (
                severity_counts.get(finding.severity, 0) + 1
            )
            sources.add(finding.source)
            modules_with_findings.add(finding.source)

        statuses = dict(module_statuses or {})

        executed_modules = sorted(
            set(modules) | set(statuses)
        )

        modules_succeeded = sum(
            status == "success"
            for status in statuses.values()
        )
        modules_failed = sum(
            status == "failed"
            for status in statuses.values()
        )

        return {
            "target": self.target,
            "assessment_id": self.assessment_id,
            "finding_count": len(findings),
            "severity_counts": severity_counts,
            "sources": sorted(sources),
            "modules": executed_modules,
            "modules_total": len(executed_modules),
            "modules_succeeded": modules_succeeded,
            "modules_failed": modules_failed,
            "modules_with_findings": sorted(modules_with_findings),
            "modules_without_findings": sorted(
                set(executed_modules) - modules_with_findings
            ),
            "module_statuses": {
                name: statuses[name]
                for name in sorted(statuses)
            },
        }
