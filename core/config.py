from dataclasses import dataclass


@dataclass
class K9Config:
    name: str = "KAMAU 9"
    codename: str = "K9"
    version: str = "0.1.0"
    description: str = "Autonomous Cybersecurity Intelligence Platform"
    mode: str = "lab"
