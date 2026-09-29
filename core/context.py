from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class AssessmentContext:
    """State shared by K9 modules during one assessment."""

    target: str
    assessment_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict = field(default_factory=dict)
