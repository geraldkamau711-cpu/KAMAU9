from core.config import K9Config
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

    def load_modules(self, path: str = "config/modules.json"):
        self.loader.load_from_file(path)

    def register_module(self, module):
        self.registry.register(module)

    def run_module(self, name: str, context: dict | None = None):
        module = self.registry.get(name)
        context = context or {}

        self.logger.info("Executing module: %s", name)

        result = module.run(context)

        self.logger.info("Module completed: %s", name)

        return result

    def start(self):
        self.logger.info(
            "%s Core v%s starting...",
            self.config.name,
            self.config.version,
        )
        self.logger.info("Operating mode: %s", self.config.mode)

        self.load_modules()

        self.logger.info(
            "Loaded modules: %s",
            self.registry.list_modules() or "none",
        )


if __name__ == "__main__":
    K9Core().start()
