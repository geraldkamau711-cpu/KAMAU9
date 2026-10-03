from core.assessment_persistence import AssessmentPersistence
from core.assessment_snapshot import AssessmentSnapshot


class AssessmentQuery:
    """Read-only queries over persisted assessment snapshots."""

    def __init__(self, persistence: AssessmentPersistence):
        self.persistence = persistence

    def get_snapshot(
        self,
        assessment_id: str,
    ) -> AssessmentSnapshot:
        """Load one persisted assessment snapshot by ID."""
        return self.persistence.load(assessment_id)

    def list_snapshots(self) -> list[AssessmentSnapshot]:
        """Load all persisted assessment snapshots in deterministic order."""
        return [
            self.persistence.load(assessment_id)
            for assessment_id in self.persistence.list_assessments()
        ]

    def list_targets(self) -> list[str]:
        """List persisted assessment targets in deterministic order."""
        return list(self.list_snapshots_by_target().keys())

    def list_snapshots_by_target(
        self,
    ) -> dict[str, list[AssessmentSnapshot]]:
        """Group persisted assessment snapshots by target chronologically."""
        grouped: dict[str, list[AssessmentSnapshot]] = {}

        for snapshot in self.list_snapshots():
            grouped.setdefault(
                snapshot.target,
                [],
            ).append(snapshot)

        for target in grouped:
            grouped[target].sort(
                key=lambda snapshot: snapshot.started_at,
            )

        return dict(
            sorted(
                grouped.items(),
                key=lambda item: item[0],
            )
        )

    def get_latest_snapshots_by_target(
        self,
    ) -> dict[str, AssessmentSnapshot]:
        """Load the latest persisted snapshot for each target."""
        grouped = self.list_snapshots_by_target()

        return {
            target: snapshots[-1]
            for target, snapshots in grouped.items()
            if snapshots
        }

    def get_latest_snapshot_pairs_by_target(
        self,
    ) -> dict[str, tuple[AssessmentSnapshot, AssessmentSnapshot]]:
        """Load the previous and latest snapshot for each target."""
        grouped = self.list_snapshots_by_target()

        return {
            target: (snapshots[-2], snapshots[-1])
            for target, snapshots in grouped.items()
            if len(snapshots) >= 2
        }

    def get_latest_snapshot_pair_for_target(
        self,
        target: str,
    ) -> tuple[AssessmentSnapshot, AssessmentSnapshot] | None:
        """Load the previous and latest snapshot for a target."""
        return self.get_latest_snapshot_pairs_by_target().get(
            target,
        )

    def get_latest_snapshot(self) -> AssessmentSnapshot | None:
        """Load the most recently started persisted assessment snapshot."""
        snapshots = self.list_snapshots()

        if not snapshots:
            return None

        return max(
            snapshots,
            key=lambda snapshot: snapshot.started_at,
        )

    def list_snapshots_for_target(
        self,
        target: str,
    ) -> list[AssessmentSnapshot]:
        """Load persisted snapshots for a target chronologically."""
        return self.list_snapshots_by_target().get(
            target,
            [],
        )

    def list_snapshot_pairs_for_target(
        self,
        target: str,
    ) -> list[
        tuple[AssessmentSnapshot, AssessmentSnapshot]
    ]:
        """Load consecutive persisted snapshot pairs for a target."""
        snapshots = self.list_snapshots_for_target(target)

        return list(
            zip(
                snapshots,
                snapshots[1:],
            )
        )

    def get_latest_snapshot_for_target(
        self,
        target: str,
    ) -> AssessmentSnapshot | None:
        """Load the most recently started snapshot for a target."""
        return self.get_latest_snapshots_by_target().get(
            target,
        )
