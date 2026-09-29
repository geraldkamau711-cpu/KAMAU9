from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AssessmentSnapshot:
    """Immutable snapshot of an assessment's observed state."""

    assessment_id: str
    target: str
    started_at: str
    finding_count: int
    severity_counts: dict[str, int]
    sources: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Serialise the snapshot into a dictionary."""

        return {
            "assessment_id": self.assessment_id,
            "target": self.target,
            "started_at": self.started_at,
            "finding_count": self.finding_count,
            "severity_counts": dict(self.severity_counts),
            "sources": list(self.sources),
        }
