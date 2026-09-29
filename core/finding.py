from dataclasses import dataclass, field
from typing import Any


@dataclass
class Finding:
    """Standardised K9 security finding."""

    title: str
    severity: str
    description: str
    source: str
    target: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "severity": self.severity,
            "description": self.description,
            "source": self.source,
            "target": self.target,
            "evidence": self.evidence,
        }
