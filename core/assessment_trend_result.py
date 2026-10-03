from dataclasses import dataclass, field


@dataclass(frozen=True)
class AssessmentTrendResult:
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
