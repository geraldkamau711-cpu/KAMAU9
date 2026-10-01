import json
from pathlib import Path

from core.assessment_snapshot import AssessmentSnapshot


class AssessmentPersistence:
    """Persist and restore immutable assessment snapshots."""

    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, snapshot: AssessmentSnapshot) -> Path:
        """Save a snapshot as JSON and return its path."""

        path = self.directory / f"{snapshot.assessment_id}.json"

        with path.open("w", encoding="utf-8") as file:
            json.dump(
                snapshot.to_dict(),
                file,
                indent=2,
                sort_keys=True,
            )

        return path

    def load(self, assessment_id: str) -> AssessmentSnapshot:
        """Load a snapshot from JSON."""

        path = self.directory / f"{assessment_id}.json"

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return AssessmentSnapshot(
            assessment_id=data["assessment_id"],
            target=data["target"],
            started_at=data["started_at"],
            finding_count=data["finding_count"],
            severity_counts=data["severity_counts"],
            sources=data["sources"],
            modules_total=data.get("modules_total", 0),
            modules_succeeded=data.get("modules_succeeded", 0),
            modules_failed=data.get("modules_failed", 0),
        )

    def list_assessments(self) -> list[str]:
        """Return persisted assessment IDs in deterministic order."""

        return sorted(
            path.stem
            for path in self.directory.glob("*.json")
            if path.is_file()
        )
