from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AssessmentTrendResult(
    Mapping[str, Any],
):
    """Immutable contract for descriptive assessment trend data."""

    comparison_count: int
    total_finding_count_change: int
    increases: int
    decreases: int
    unchanged: int
    latest_change: int | None
    latest_direction: str
    severity_changes: dict[str, int] = field(default_factory=dict)
    module_execution_changes: dict[str, int] = field(
        default_factory=dict,
    )
    source_changes: dict[str, int] = field(
        default_factory=dict,
    )

    def _as_dict(self) -> dict[str, Any]:
        """Return the legacy dictionary representation."""
        result = {
            "comparison_count": self.comparison_count,
            "total_finding_count_change": (
                self.total_finding_count_change
            ),
            "increases": self.increases,
            "decreases": self.decreases,
            "unchanged": self.unchanged,
            "latest_change": self.latest_change,
            "latest_direction": self.latest_direction,
        }

        if self.severity_changes:
            result["severity_changes"] = dict(
                self.severity_changes,
            )

        if self.module_execution_changes:
            result["module_execution_changes"] = dict(
                self.module_execution_changes,
            )

        if self.source_changes:
            result["source_changes"] = dict(
                self.source_changes,
            )

        return result

    def __getitem__(self, key: str) -> Any:
        """Provide dictionary-style field access."""
        if key == "severity_changes":
            return dict(self.severity_changes)

        if key == "module_execution_changes":
            return dict(self.module_execution_changes)

        if key == "source_changes":
            return dict(self.source_changes)

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
