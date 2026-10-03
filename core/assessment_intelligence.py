from core.assessment_trend_result import AssessmentTrendResult


class AssessmentIntelligence:
    """Derive a descriptive state from an assessment trend summary."""

    def _derive_state(self, direction: str) -> str:
        """Map an assessment trend direction to a descriptive state."""
        if direction == "increased":
            return "increased"

        if direction == "decreased":
            return "decreased"

        if direction == "unchanged":
            return "stable"

        if direction == "no_history":
            return "no_history"

        raise ValueError(
            f"Unsupported assessment trend direction: {direction!r}"
        )

    def analyse(
        self,
        trend: AssessmentTrendResult,
    ) -> dict:
        """Return a deterministic assessment state from trend data."""
        direction = trend["latest_direction"]
        state = self._derive_state(direction)

        result = {
            "state": state,
            "finding_count_change": trend["total_finding_count_change"],
            "latest_direction": direction,
        }

        if "severity_changes" in trend:
            result["severity_changes"] = dict(
                trend["severity_changes"]
            )

        if "module_execution_changes" in trend:
            result["module_execution_changes"] = dict(
                trend["module_execution_changes"]
            )

        if "source_changes" in trend:
            result["source_changes"] = dict(
                trend["source_changes"]
            )

        return result
