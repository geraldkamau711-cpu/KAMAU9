from core.loader import ModuleLoader
from core.mode import K9Mode
from core.registry import ModuleRegistry


def test_loader_loads_enabled_module():
    registry = ModuleRegistry()
    loader = ModuleLoader(registry)

    loader.load_from_file("config/modules.json")

    assert registry.list_modules() == ["example"]


def test_loader_loads_lab_module_in_lab_mode():
    registry = ModuleRegistry()
    loader = ModuleLoader(registry, mode=K9Mode.LAB)

    loader.load_from_file("config/modules.json")

    assert registry.list_modules() == ["example"]


def test_loader_loads_analysis_capable_module_in_analysis_mode():
    registry = ModuleRegistry()
    loader = ModuleLoader(registry, mode=K9Mode.ANALYSIS)

    loader.load_from_file("config/modules.json")

    assert registry.list_modules() == ["example"]


def test_loader_skips_lab_only_module_in_crypto_mode(tmp_path):
    config = tmp_path / "modules.json"
    config.write_text(
        '{"enabled": ["modules.example.ExampleModule"]}',
        encoding="utf-8",
    )

    registry = ModuleRegistry()
    loader = ModuleLoader(registry, mode=K9Mode.CRYPTO)

    loader.load_from_file(config)

    assert registry.list_modules() == []
