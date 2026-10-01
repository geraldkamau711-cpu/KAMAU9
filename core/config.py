from dataclasses import dataclass

from core.mode import K9Mode


@dataclass
class K9Config:
    name: str = "KAMAU 9"
    codename: str = "K9"
    version: str = "0.1.0"
    description: str = "Autonomous Cybersecurity Intelligence Platform"
    mode: K9Mode = K9Mode.LAB

    def __post_init__(self) -> None:
        if not isinstance(self.mode, K9Mode):
            self.mode = K9Mode.parse(self.mode)
