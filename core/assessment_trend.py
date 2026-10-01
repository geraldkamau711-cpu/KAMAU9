class AssessmentTrend:
    """Summarise objective finding-count changes across assessments."""

    def summarise(self, comparisons: list[dict]) -> dict:
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

        return {
            "comparison_count": len(comparisons),
            "total_finding_count_change": total_change,
            "increases": increases,
            "decreases": decreases,
            "unchanged": unchanged,
            "latest_change": latest_change,
            "latest_direction": latest_direction,
        }
