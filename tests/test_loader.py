from core.loader import ModuleLoader
from core.registry import ModuleRegistry


def test_loader_loads_enabled_module():
    registry = ModuleRegistry()
    loader = ModuleLoader(registry)

    loader.load_from_file("config/modules.json")

    assert registry.list_modules() == ["example"]
