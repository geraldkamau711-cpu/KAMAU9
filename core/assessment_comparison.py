from core.assessment_snapshot import AssessmentSnapshot


class AssessmentComparison:
    """Compare two immutable assessment snapshots."""

    def compare(
        self,
        previous: AssessmentSnapshot,
        current: AssessmentSnapshot,
    ) -> dict:
        """Return objective differences between two assessments."""

        previous_sources = set(previous.sources)
        current_sources = set(current.sources)

        return {
            "previous_assessment_id": previous.assessment_id,
            "current_assessment_id": current.assessment_id,
            "target_changed": previous.target != current.target,
            "finding_count_change": (
                current.finding_count - previous.finding_count
            ),
            "severity_counts": {
                "previous": dict(previous.severity_counts),
                "current": dict(current.severity_counts),
            },
            "module_execution_counts": {
                "previous": {
                    "total": previous.modules_total,
                    "succeeded": previous.modules_succeeded,
                    "failed": previous.modules_failed,
                },
                "current": {
                    "total": current.modules_total,
                    "succeeded": current.modules_succeeded,
                    "failed": current.modules_failed,
                },
            },
            "new_sources": sorted(current_sources - previous_sources),
            "removed_sources": sorted(previous_sources - current_sources),
        }
