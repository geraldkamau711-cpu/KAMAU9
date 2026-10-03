from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any

from core.assessment_snapshot import AssessmentSnapshot


@dataclass(frozen=True)
class AssessmentComparisonResult(
    Mapping[str, Any],
):
    """Immutable contract for objective assessment comparison data."""

    previous_assessment_id: str
    current_assessment_id: str
    target_changed: bool
    finding_count_change: int
    severity_counts: dict[str, dict[str, int]]
    module_execution_counts: dict[str, dict[str, int]]
    new_sources: list[str]
    removed_sources: list[str]

    def _as_dict(self) -> dict[str, Any]:
        """Return the legacy dictionary representation."""
        return {
            "previous_assessment_id": self.previous_assessment_id,
            "current_assessment_id": self.current_assessment_id,
            "target_changed": self.target_changed,
            "finding_count_change": self.finding_count_change,
            "severity_counts": {
                key: dict(value)
                for key, value in self.severity_counts.items()
            },
            "module_execution_counts": {
                key: dict(value)
                for key, value in self.module_execution_counts.items()
            },
            "new_sources": list(self.new_sources),
            "removed_sources": list(self.removed_sources),
        }

    def __getitem__(self, key: str) -> Any:
        """Provide dictionary-style field access."""
        return self._as_dict()[key]

    def __contains__(self, key: object) -> bool:
        """Preserve legacy membership semantics."""
        return key in self._as_dict()

    def __iter__(self) -> Iterator[str]:
        """Iterate over legacy dictionary keys."""
        return iter(self._as_dict())

    def __len__(self) -> int:
        """Return the number of exposed legacy fields."""
        return len(self._as_dict())

    def __eq__(self, other: object) -> bool:
        """Compare naturally with equivalent mapping data."""
        if isinstance(other, Mapping):
            return self._as_dict() == dict(other)

        return super().__eq__(other)


class AssessmentComparison:
    """Compare two immutable assessment snapshots."""

    def compare(
        self,
        previous: AssessmentSnapshot,
        current: AssessmentSnapshot,
    ) -> AssessmentComparisonResult:
        """Return objective differences between two assessments."""

        previous_sources = set(previous.sources)
        current_sources = set(current.sources)

        return AssessmentComparisonResult(
            previous_assessment_id=previous.assessment_id,
            current_assessment_id=current.assessment_id,
            target_changed=previous.target != current.target,
            finding_count_change=(
                current.finding_count - previous.finding_count
            ),
            severity_counts={
                "previous": dict(previous.severity_counts),
                "current": dict(current.severity_counts),
            },
            module_execution_counts={
                "previous": {
                    "total": previous.modules_total,
                    "succeeded": previous.modules_succeeded,
                    "failed": previous.modules_failed,
                },
                "current": {
                    "total": current.modules_total,
                    "succeeded": current.modules_succeeded,
                    "failed": current.modules_failed,
                },
            },
            new_sources=sorted(
                current_sources - previous_sources,
            ),
            removed_sources=sorted(
                previous_sources - current_sources,
            ),
        )
