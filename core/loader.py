import importlib
import json

from core.logger import get_logger


class ModuleLoader:
    """Loads explicitly enabled K9 modules."""

    def __init__(self, registry):
        self.registry = registry
        self.logger = get_logger("K9.Loader")

    def load_from_file(self, path: str):
        with open(path, "r", encoding="utf-8") as file:
            config = json.load(file)

        for module_path in config.get("enabled", []):
            module_name, class_name = module_path.rsplit(".", 1)

            module = importlib.import_module(module_name)
            module_class = getattr(module, class_name)

            instance = module_class()
            self.registry.register(instance)

            self.logger.info("Loaded: %s", module_path)
