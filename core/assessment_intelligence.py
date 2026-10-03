from core.assessment_intelligence_result import (
    AssessmentIntelligenceResult,
)
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
    ) -> AssessmentIntelligenceResult:
        """Return a deterministic assessment intelligence result."""
        direction = trend["latest_direction"]
        state = self._derive_state(direction)

        return AssessmentIntelligenceResult(
            state=state,
            finding_count_change=trend["total_finding_count_change"],
            latest_direction=direction,
            severity_changes=(
                dict(trend["severity_changes"])
                if "severity_changes" in trend
                else {}
            ),
            module_execution_changes=(
                dict(trend["module_execution_changes"])
                if "module_execution_changes" in trend
                else {}
            ),
            source_changes=(
                dict(trend["source_changes"])
                if "source_changes" in trend
                else {}
            ),
        )
