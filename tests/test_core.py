from core.config import K9Config
from core.main import K9Core
from modules.example import ExampleModule


def test_k9_config():
    config = K9Config()

    assert config.name == "K9"
    assert config.version == "0.1.0"
    assert config.mode == "lab"


def test_k9_core():
    core = K9Core()

    assert core.config.name == "K9"


def test_core_registers_module():
    core = K9Core()
    core.register_module(ExampleModule())

    assert core.registry.list_modules() == ["example"]


def test_core_executes_module():
    core = K9Core()
    core.register_module(ExampleModule())

    result = core.run_module("example")

    assert result["status"] == "ok"
