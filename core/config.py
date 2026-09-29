from dataclasses import dataclass


@dataclass
class K9Config:
    name: str = "K9"
    version: str = "0.1.0"
    mode: str = "lab"
