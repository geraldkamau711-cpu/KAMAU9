from core.assessment_comparison import AssessmentComparisonResult
from core.assessment_trend_result import AssessmentTrendResult


class AssessmentTrend:
    """Summarise objective changes across assessment comparisons."""

    def summarise(
        self,
        comparisons: list[AssessmentComparisonResult],
    ) -> AssessmentTrendResult:
        """Return deterministic trend information from comparisons."""

        increases = sum(
            comparison["finding_count_change"] > 0
            for comparison in comparisons
        )
        decreases = sum(
            comparison["finding_count_change"] < 0
            for comparison in comparisons
        )
        unchanged = sum(
            comparison["finding_count_change"] == 0
            for comparison in comparisons
        )

        total_change = sum(
            comparison["finding_count_change"]
            for comparison in comparisons
        )

        severity_changes = {}
        has_severity_history = False

        module_execution_changes = {
            "total": 0,
            "succeeded": 0,
            "failed": 0,
        }
        has_module_execution_history = False

        source_changes = {
            "new": 0,
            "removed": 0,
        }
        has_source_history = False

        for comparison in comparisons:
            severity_counts = comparison.get("severity_counts")

            if severity_counts is not None:
                has_severity_history = True

                previous = severity_counts.get(
                    "previous",
                    {},
                )
                current = severity_counts.get(
                    "current",
                    {},
                )

                severities = set(previous) | set(current)

                for severity in severities:
                    severity_changes[severity] = (
                        severity_changes.get(severity, 0)
                        + current.get(severity, 0)
                        - previous.get(severity, 0)
                    )

            module_execution_counts = comparison.get(
                "module_execution_counts",
            )

            if module_execution_counts is not None:
                previous = module_execution_counts.get(
                    "previous",
                    {},
                )
                current = module_execution_counts.get(
                    "current",
                    {},
                )

                deltas = {
                    metric: (
                        current.get(metric, 0)
                        - previous.get(metric, 0)
                    )
                    for metric in module_execution_changes
                }

                if any(deltas.values()):
                    has_module_execution_history = True

                    for metric, delta in deltas.items():
                        module_execution_changes[metric] += delta

            new_sources = comparison.get("new_sources")
            removed_sources = comparison.get("removed_sources")

            if new_sources or removed_sources:
                has_source_history = True

                source_changes["new"] += len(new_sources or [])
                source_changes["removed"] += len(
                    removed_sources or []
                )

        if not comparisons:
            latest_change = None
            latest_direction = "no_history"
        else:
            latest_change = comparisons[-1]["finding_count_change"]

            if latest_change > 0:
                latest_direction = "increased"
            elif latest_change < 0:
                latest_direction = "decreased"
            else:
                latest_direction = "unchanged"

        return AssessmentTrendResult(
            comparison_count=len(comparisons),
            total_finding_count_change=total_change,
            increases=increases,
            decreases=decreases,
            unchanged=unchanged,
            latest_change=latest_change,
            latest_direction=latest_direction,
            severity_changes=(
                {
                    severity: severity_changes[severity]
                    for severity in sorted(severity_changes)
                }
                if has_severity_history
                else {}
            ),
            module_execution_changes=(
                dict(module_execution_changes)
                if has_module_execution_history
                else {}
            ),
            source_changes=(
                dict(source_changes)
                if has_source_history
                else {}
            ),
        )
