from dataclasses import dataclass, field
from typing import Any


@dataclass
class HostProfile:
    """Structured intelligence profile for the local host."""

    hostname: str
    operating_system: str
    os_release: str
    platform: str
    architecture: str
    python_version: str
    interfaces: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "hostname": self.hostname,
            "operating_system": self.operating_system,
            "os_release": self.os_release,
            "platform": self.platform,
            "architecture": self.architecture,
            "python_version": self.python_version,
            "interfaces": list(self.interfaces),
        }
