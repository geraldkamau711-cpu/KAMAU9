from __future__ import annotations

from types import MappingProxyType
from typing import Mapping


class ModuleResultView:
    """Read-only access to structured assessment module results."""

    def __init__(self, results: Mapping[str, dict]):
        self._results = results

    def get(self, name: str) -> Mapping | None:
        """Return a read-only view of a module result, or None."""

        result = self._results.get(name)

        if result is None:
            return None

        return MappingProxyType(result)

    def has(self, name: str) -> bool:
        """Return whether a module result exists."""

        return name in self._results

    def names(self) -> list[str]:
        """Return the names of modules with stored results."""

        return list(self._results)
