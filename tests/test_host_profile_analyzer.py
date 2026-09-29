from core.host_profile import HostProfile
from core.host_profile_analyzer import HostProfileAnalyzer


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


def test_analyzer_returns_host_observations():
    analyzer = HostProfileAnalyzer()

    profile = make_profile()

    result = analyzer.analyze(profile)

    assert result["hostname"] == "test-host"
    assert result["operating_system"] == "Linux"
    assert result["architecture"] == "x86_64"


def test_analyzer_counts_interfaces():
    analyzer = HostProfileAnalyzer()

    profile = make_profile()

    result = analyzer.analyze(profile)

    assert result["interface_count"] == 2
    assert result["active_interface_count"] == 2


def test_analyzer_identifies_ipv4_interfaces():
    analyzer = HostProfileAnalyzer()

    profile = make_profile()

    result = analyzer.analyze(profile)

    assert result["ipv4_interface_count"] == 2
