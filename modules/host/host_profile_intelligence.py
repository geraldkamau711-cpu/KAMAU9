from core.finding import Finding
from core.host_profile import HostProfile
from core.host_profile_analyzer import HostProfileAnalyzer
from core.module import K9Module


class HostProfileIntelligenceModule(K9Module):
    """Analyse an existing HostProfile and produce structured findings."""

    name = "host_profile_intelligence"

    def run(self, context):
        profile = context.get("host_profile")

        if not isinstance(profile, HostProfile):
            return {
                "module": self.name,
                "status": "error",
                "findings": [],
            }

        analyzer = HostProfileAnalyzer()
        observations = analyzer.analyze(profile)

        finding = Finding(
            title="Host profile analysed",
            severity="info",
            description=(
                "K9 analysed the collected host profile and "
                "derived structured local observations."
            ),
            source=self.name,
            target=profile.hostname,
            evidence=observations,
        )

        return {
            "module": self.name,
            "status": "ok",
            "target": profile.hostname,
            "findings": [finding],
        }
