from abc import ABC, abstractmethod


class K9Module(ABC):
    """Base interface for every K9 module."""

    name = "unnamed"

    @abstractmethod
    def run(self, context):
        """Execute the module using the supplied context."""
        raise NotImplementedError
