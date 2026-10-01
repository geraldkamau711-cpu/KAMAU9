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
    modules_total: int = 0
    modules_succeeded: int = 0
    modules_failed: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialise the snapshot into a dictionary."""

        return {
            "assessment_id": self.assessment_id,
            "target": self.target,
            "started_at": self.started_at,
            "finding_count": self.finding_count,
            "severity_counts": dict(self.severity_counts),
            "sources": list(self.sources),
            "modules_total": self.modules_total,
            "modules_succeeded": self.modules_succeeded,
            "modules_failed": self.modules_failed,
        }
