from core.host_profile import HostProfile
from core.host_profile_builder import HostProfileBuilder


def test_builder_creates_host_profile():
    builder = HostProfileBuilder()

    host_finding = {
        "hostname": "test-host",
        "os": "Linux",
        "os_release": "6.19",
        "platform": "Linux-test",
        "architecture": "x86_64",
        "python_version": "3.14.0",
    }

    profile = builder.build(
        host_finding=host_finding,
        interface_findings=[],
    )

    assert isinstance(profile, HostProfile)
    assert profile.hostname == "test-host"
    assert profile.operating_system == "Linux"
    assert profile.os_release == "6.19"
    assert profile.architecture == "x86_64"


def test_builder_adds_network_interfaces():
    builder = HostProfileBuilder()

    host_finding = {
        "hostname": "test-host",
        "os": "Linux",
        "os_release": "6.19",
        "platform": "Linux-test",
        "architecture": "x86_64",
        "python_version": "3.14.0",
    }

    interface_findings = [
        {
            "interface": "lo",
            "state": "up",
            "ipv4": "127.0.0.1",
        },
        {
            "interface": "wlan0",
            "state": "up",
            "ipv4": "10.20.0.91",
        },
    ]

    profile = builder.build(
        host_finding=host_finding,
        interface_findings=interface_findings,
    )

    assert len(profile.interfaces) == 2
    assert profile.interfaces[0]["interface"] == "lo"
    assert profile.interfaces[1]["interface"] == "wlan0"
