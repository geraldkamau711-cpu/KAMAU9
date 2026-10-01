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

        return {
            "state": state,
            "finding_count_change": trend["total_finding_count_change"],
            "latest_direction": direction,
        }
