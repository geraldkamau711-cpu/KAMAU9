import importlib
import json

from core.logger import get_logger
from core.mode import K9Mode


class ModuleLoader:
    """Loads explicitly enabled K9 modules compatible with the active mode."""

    def __init__(self, registry, mode: K9Mode | str = K9Mode.LAB):
        self.registry = registry
        self.mode = (
            mode if isinstance(mode, K9Mode) else K9Mode.parse(mode)
        )
        self.logger = get_logger("K9.Loader")

    def load_from_file(self, path: str):
        with open(path, "r", encoding="utf-8") as file:
            config = json.load(file)

        for module_path in config.get("enabled", []):
            module_name, class_name = module_path.rsplit(".", 1)

            module = importlib.import_module(module_name)
            module_class = getattr(module, class_name)

            instance = module_class()

            if not instance.supports_mode(self.mode):
                self.logger.info(
                    "Skipped: %s (unsupported mode: %s)",
                    module_path,
                    self.mode.value,
                )
                continue

            self.registry.register(instance)

            self.logger.info("Loaded: %s", module_path)
