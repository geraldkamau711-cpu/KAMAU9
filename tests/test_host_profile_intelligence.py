from core.host_profile import HostProfile
from modules.host.host_profile_intelligence import HostProfileIntelligenceModule


def make_profile():
    return HostProfile(
        hostname="test-host",
        operating_system="Linux",
        os_release="6.19",
        platform="Linux-test",
        architecture="x86_64",
        python_version="3.14.0",
        interfaces=[
            {
                "interface": "lo",
                "state": "up",
                "ipv4": "127.0.0.1",
            },
            {
                "interface": "wlan0",
                "state": "up",
                "ipv4": "192.168.1.10",
            },
        ],
    )


def test_host_profile_intelligence_module_name():
    module = HostProfileIntelligenceModule()

    assert module.name == "host_profile_intelligence"


def test_host_profile_intelligence_requires_profile():
    module = HostProfileIntelligenceModule()

    result = module.run({})

    assert result["module"] == "host_profile_intelligence"
    assert result["status"] == "error"
    assert result["findings"] == []


def test_host_profile_intelligence_produces_finding():
    module = HostProfileIntelligenceModule()

    result = module.run({
        "host_profile": make_profile(),
    })

    assert result["module"] == "host_profile_intelligence"
    assert result["status"] == "ok"
    assert len(result["findings"]) == 1

    finding = result["findings"][0]

    assert finding.title == "Host profile analysed"
    assert finding.severity == "info"
    assert finding.source == "host_profile_intelligence"
    assert finding.target == "test-host"

    assert finding.evidence["interface_count"] == 2
    assert finding.evidence["active_interface_count"] == 2
    assert finding.evidence["ipv4_interface_count"] == 2
