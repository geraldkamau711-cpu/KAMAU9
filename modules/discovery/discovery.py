from core.finding import Finding
from core.module import K9Module


class DiscoveryModule(K9Module):
    """Basic authorised asset-discovery foundation."""

    name = "discovery"

    def run(self, context):
        target = context.get("target")

        if not target:
            return {
                "module": self.name,
                "status": "error",
                "findings": [],
                "error": "No target supplied.",
            }

        finding = Finding(
            title="Discovery target registered",
            severity="info",
            description="Target accepted for authorised assessment.",
            source=self.name,
            target=target,
            evidence={
                "stage": "discovery",
            },
        )

        return {
            "module": self.name,
            "status": "ready",
            "target": target,
            "findings": [finding],
        }
