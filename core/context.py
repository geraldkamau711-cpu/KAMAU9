from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from core.host_profile import HostProfile


@dataclass
class AssessmentContext:
    """State shared by K9 modules during one assessment."""

    target: str
    assessment_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict = field(default_factory=dict)
    host_profile: HostProfile | None = None
    module_results: dict[str, dict] = field(default_factory=dict)

    def store_module_result(self, name: str, result: dict) -> None:
        """Store the latest structured result produced by a module."""

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Module result name must be a non-empty string.")

        if not isinstance(result, dict):
            raise TypeError("Module result must be a dictionary.")

        self.module_results[name] = result

    def get_module_result(self, name: str) -> dict | None:
        """Return the latest result for a module, or None if unavailable."""

        return self.module_results.get(name)
