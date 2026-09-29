from core.logger import get_logger
from core.module import K9Module


class ModuleRegistry:
    """Registers and manages K9 modules."""

    def __init__(self):
        self.logger = get_logger("K9.Registry")
        self._modules: dict[str, K9Module] = {}

    def register(self, module: K9Module):
        if module.name in self._modules:
            raise ValueError(f"Module already registered: {module.name}")

        self._modules[module.name] = module
        self.logger.info("Registered module: %s", module.name)

    def get(self, name: str) -> K9Module:
        return self._modules[name]

    def list_modules(self) -> list[str]:
        return sorted(self._modules)
