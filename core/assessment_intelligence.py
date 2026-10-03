class AssessmentIntelligence:
    """Derive a descriptive state from an assessment trend summary."""

    def analyse(self, trend: dict) -> dict:
        """Return a deterministic assessment state from trend data."""
        direction = trend["latest_direction"]

        if direction == "increased":
            state = "increased"
        elif direction == "decreased":
            state = "decreased"
        elif direction == "unchanged":
            state = "stable"
        elif direction == "no_history":
            state = "no_history"
        else:
            raise ValueError(
                f"Unsupported assessment trend direction: {direction!r}"
            )

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
