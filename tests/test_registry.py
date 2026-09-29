from core.registry import ModuleRegistry
from modules.example import ExampleModule


def test_module_registration():
    registry = ModuleRegistry()
    registry.register(ExampleModule())

    assert registry.list_modules() == ["example"]
    assert registry.get("example").name == "example"


def test_module_execution():
    module = ExampleModule()
    result = module.run({})

    assert result["status"] == "ok"
