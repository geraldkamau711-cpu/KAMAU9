from modules.host.network_interfaces import NetworkInterfaceModule


def test_network_interface_module_name():
    module = NetworkInterfaceModule()

    assert module.name == "network_interfaces"


def test_network_interface_module_returns_result():
    module = NetworkInterfaceModule()

    result = module.run({})

    assert result["module"] == "network_interfaces"
    assert result["status"] == "ok"
    assert isinstance(result["findings"], list)


def test_network_interface_findings_have_expected_structure():
    module = NetworkInterfaceModule()

    result = module.run({})

    for finding in result["findings"]:
        assert finding.source == "network_interfaces"
        assert finding.title == "Local network interface discovered"
        assert finding.severity == "info"
        assert isinstance(finding.evidence, dict)
        assert "interface" in finding.evidence
