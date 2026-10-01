from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from core.host_profile import HostProfile
from core.module_result import ModuleResultView


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
    module_statuses: dict[str, str] = field(default_factory=dict)

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

    def has_module_result(self, name: str) -> bool:
        """Return whether a result exists for the supplied module."""

        return name in self.module_results

    def list_module_results(self) -> list[str]:
        """Return the names of modules with stored results."""

        return list(self.module_results)

    def store_module_status(self, name: str, status: str) -> None:
        """Store the latest execution status for a module."""

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Module status name must be a non-empty string.")

        if status not in {"success", "failed"}:
            raise ValueError(
                "Module status must be either 'success' or 'failed'."
            )

        self.module_statuses[name] = status

    def get_module_status(self, name: str) -> str | None:
        """Return the latest execution status for a module."""

        return self.module_statuses.get(name)

    def list_module_statuses(self) -> dict[str, str]:
        """Return a copy of all module execution statuses."""

        return dict(self.module_statuses)

    def module_result_view(self) -> ModuleResultView:
        """Return read-only access to stored module results."""

        return ModuleResultView(self.module_results)
