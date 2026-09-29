from core.finding import Finding


class EvidenceStore:
    """Central store for findings collected during a K9 run."""

    def __init__(self):
        self._findings: list[Finding] = []

    def add(self, finding: Finding):
        self._findings.append(finding)

    def all(self) -> list[Finding]:
        return list(self._findings)

    def count(self) -> int:
        return len(self._findings)

    def clear(self):
        self._findings.clear()
