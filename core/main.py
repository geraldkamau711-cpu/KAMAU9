from core.assessment_snapshot import AssessmentSnapshot
from core.assessment_summary import AssessmentSummary
from core.config import K9Config
from core.context import AssessmentContext
from core.evidence import EvidenceStore
from core.host_profile_builder import HostProfileBuilder
from core.loader import ModuleLoader
from core.logger import get_logger
from core.registry import ModuleRegistry


class K9Core:
    """Central K9 orchestrator."""

    def __init__(self, config: K9Config | None = None):
        self.config = config or K9Config()
        self.logger = get_logger("K9")
        self.registry = ModuleRegistry()
        self.loader = ModuleLoader(self.registry, mode=self.config.mode)
        self.evidence = EvidenceStore()
        self.context: AssessmentContext | None = None

    def load_modules(self, path: str = "config/modules.json"):
        self.loader.load_from_file(path)

    def register_module(self, module):
        self.registry.register(module)

    def start_assessment(self, target: str):
        self.context = AssessmentContext(target=target)

        self.logger.info(
            "Assessment started: %s",
            self.context.assessment_id,
        )
        self.logger.info(
            "Assessment target: %s",
            self.context.target,
        )

        return self.context

    def build_host_profile(self):
        """Build a unified HostProfile from local host intelligence."""

        if self.context is None:
            raise RuntimeError("No active assessment.")

        self.run_module("host_intelligence")
        self.run_module("network_interfaces")

        host_result = self.context.get_module_result(
            "host_intelligence"
        )
        interface_result = self.context.get_module_result(
            "network_interfaces"
        )

        if host_result is None:
            raise RuntimeError(
                "Host intelligence produced no result."
            )

        if interface_result is None:
            raise RuntimeError(
                "Network interface intelligence produced no result."
            )

        host_findings = host_result.get("findings", [])
        interface_findings = interface_result.get("findings", [])

        if not host_findings:
            raise RuntimeError(
                "Host intelligence produced no findings."
            )

        host_evidence = host_findings[0].evidence

        interface_evidence = [
            finding.evidence
            for finding in interface_findings
        ]

        builder = HostProfileBuilder()

        profile = builder.build(
            host_finding=host_evidence,
            interface_findings=interface_evidence,
        )

        self.context.host_profile = profile

        self.logger.info(
            "Host profile built: %s | interfaces=%d",
            profile.hostname,
            len(profile.interfaces),
        )

        return profile

    def build_assessment_summary(self):
        """Build a summary from the current assessment evidence."""

        if self.context is None:
            raise RuntimeError("No active assessment.")

        summary_builder = AssessmentSummary(
            target=self.context.target,
            assessment_id=self.context.assessment_id,
        )

        return summary_builder.build(
            self.evidence.all(),
            modules=self.context.list_module_results(),
            module_statuses=self.context.list_module_statuses(),
        )

    def create_assessment_snapshot(self):
        """Create an immutable snapshot of the current assessment."""

        if self.context is None:
            raise RuntimeError("No active assessment.")

        summary = self.build_assessment_summary()

        return AssessmentSnapshot(
            assessment_id=self.context.assessment_id,
            target=self.context.target,
            started_at=self.context.started_at,
            finding_count=summary["finding_count"],
            severity_counts=summary["severity_counts"],
            sources=summary["sources"],
        )

    def run_module(self, name: str, context: dict | None = None):
        module = self.registry.get(name)

        if self.context is None:
            raise RuntimeError("No active assessment.")

        execution_context = {
            "target": self.context.target,
            "assessment_id": self.context.assessment_id,
            "module_results": self.context.module_result_view(),
            **(context or {}),
            "mode": self.config.mode,
        }

        self.logger.info(
            "Executing module: %s",
            name,
        )

        try:
            result = module.run(execution_context)

            if not isinstance(result, dict):
                raise TypeError(
                    "K9 modules must return a dictionary result."
                )

            self.context.store_module_result(name, result)
            self.context.store_module_status(name, "success")

        except Exception:
            self.context.store_module_status(name, "failed")
            self.logger.exception(
                "Module failed: %s",
                name,
            )
            raise

        for finding in result.get("findings", []):
            self.evidence.add(finding)

        self.logger.info(
            "Module completed: %s | findings=%d",
            name,
            len(result.get("findings", [])),
        )

        return result

    def start(self):
        self.logger.info(
            "%s Core v%s starting...",
            self.config.name,
            self.config.version,
        )
        self.logger.info(
            "Operating mode: %s",
            self.config.mode,
        )

        self.load_modules()

        self.logger.info(
            "Loaded modules: %s",
            self.registry.list_modules() or "none",
        )


if __name__ == "__main__":
    K9Core().start()
