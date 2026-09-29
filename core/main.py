from core.config import K9Config
from core.context import AssessmentContext
from core.evidence import EvidenceStore
from core.loader import ModuleLoader
from core.logger import get_logger
from core.registry import ModuleRegistry


class K9Core:
    """Central K9 orchestrator."""

    def __init__(self, config: K9Config | None = None):
        self.config = config or K9Config()
        self.logger = get_logger("K9")
        self.registry = ModuleRegistry()
        self.loader = ModuleLoader(self.registry)
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

    def run_module(self, name: str, context: dict | None = None):
        module = self.registry.get(name)

        if self.context is None:
            raise RuntimeError("No active assessment.")

        execution_context = {
            "target": self.context.target,
            "assessment_id": self.context.assessment_id,
            **(context or {}),
        }

        self.logger.info("Executing module: %s", name)

        result = module.run(execution_context)

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
