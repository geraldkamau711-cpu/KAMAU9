from core.finding import Finding
from modules.discovery.discovery import DiscoveryModule


def test_discovery_requires_target():
    module = DiscoveryModule()

    result = module.run({})

    assert result["status"] == "error"
    assert result["findings"] == []


def test_discovery_accepts_target():
    module = DiscoveryModule()

    result = module.run({"target": "lab-target"})

    assert result["status"] == "ready"
    assert result["target"] == "lab-target"
    assert len(result["findings"]) == 1
    assert isinstance(result["findings"][0], Finding)


def test_discovery_finding_contains_target():
    module = DiscoveryModule()

    result = module.run({"target": "lab-target"})
    finding = result["findings"][0]

    assert finding.target == "lab-target"
    assert finding.source == "discovery"
