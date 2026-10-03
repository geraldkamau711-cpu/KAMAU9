from core.assessment_comparison import AssessmentComparison
from core.assessment_query import AssessmentQuery


class AssessmentComparisonService:
    """Coordinate persisted assessment queries with comparison logic."""

    def __init__(self, query: AssessmentQuery):
        self.query = query
        self.comparison = AssessmentComparison()

    def list_targets(self) -> list[str]:
        """Return every persisted assessment target."""
        return self.query.list_targets()

    def compare_assessment_snapshots(
        self,
        previous_assessment_id: str,
        current_assessment_id: str,
    ) -> dict:
        """Compare two persisted assessment snapshots."""
        previous = self.query.get_snapshot(
            previous_assessment_id,
        )
        current = self.query.get_snapshot(
            current_assessment_id,
        )

        return self.comparison.compare(
            previous,
            current,
        )

    def compare_latest_assessment_snapshots_for_target(
        self,
        target: str,
    ) -> dict | None:
        """Compare the two most recent persisted snapshots for a target."""
        snapshot_pair = self.query.get_latest_snapshot_pair_for_target(
            target,
        )

        if snapshot_pair is None:
            return None

        previous, current = snapshot_pair

        return self.comparison.compare(
            previous,
            current,
        )

    def compare_assessment_history_for_target(
        self,
        target: str,
    ) -> list[dict]:
        """Compare every consecutive persisted snapshot for a target."""
        snapshot_pairs = self.query.list_snapshot_pairs_for_target(
            target,
        )

        return [
            self.comparison.compare(
                previous,
                current,
            )
            for previous, current in snapshot_pairs
        ]

    def compare_latest_assessment_snapshots_for_all_targets(
        self,
    ) -> dict[str, dict]:
        """Compare the two most recent persisted snapshots for each target."""
        snapshot_pairs = (
            self.query.get_latest_snapshot_pairs_by_target()
        )

        return {
            target: self.comparison.compare(
                previous,
                current,
            )
            for target, (previous, current) in snapshot_pairs.items()
        }
