import pytest

from core.main import K9Core


def test_assessment_starts():
    core = K9Core()

    context = core.start_assessment("lab-target")

    assert context.target == "lab-target"
    assert core.context is context


def test_module_requires_assessment():
    core = K9Core()
    core.load_modules()

    with pytest.raises(RuntimeError):
        core.run_module("example")


def test_discovery_result_enters_evidence_store():
    core = K9Core()
    core.load_modules()

    core.registry._modules.pop("example")

    from modules.discovery.discovery import DiscoveryModule

    core.register_module(DiscoveryModule())
    core.start_assessment("lab-target")

    result = core.run_module("discovery")

    assert result["status"] == "ready"
    assert core.evidence.count() == 1
    assert core.evidence.all()[0].target == "lab-target"
