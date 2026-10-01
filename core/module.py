from abc import ABC, abstractmethod

from core.mode import K9Mode


class K9Module(ABC):
    """Base interface for every K9 module."""

    name = "unnamed"
    supported_modes = frozenset({K9Mode.LAB, K9Mode.ANALYSIS})

    def supports_mode(self, mode: K9Mode | str) -> bool:
        """Return whether this module supports the supplied K9 mode."""
        if not isinstance(mode, K9Mode):
            mode = K9Mode.parse(mode)

        return mode in self.supported_modes

    @abstractmethod
    def run(self, context):
        """Execute the module using the supplied context."""
        raise NotImplementedError
