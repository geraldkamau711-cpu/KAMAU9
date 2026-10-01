from enum import Enum


class K9Mode(str, Enum):
    """Supported KAMAU 9 operating modes."""

    LAB = "lab"
    CRYPTO = "crypto"
    ANALYSIS = "analysis"

    @classmethod
    def parse(cls, value: str) -> "K9Mode":
        """Parse a mode name and reject unsupported modes."""
        if not isinstance(value, str):
            raise TypeError("K9 mode must be a string")

        normalised = value.strip().lower()

        try:
            return cls(normalised)
        except ValueError as exc:
            valid = ", ".join(mode.value for mode in cls)
            raise ValueError(
                f"Unsupported K9 mode: {normalised!r}. "
                f"Expected one of: {valid}"
            ) from exc
