from core.host_profile import HostProfile


def test_host_profile_stores_host_information():
    profile = HostProfile(
        hostname="test-host",
        operating_system="Linux",
        os_release="test-release",
        platform="test-platform",
        architecture="x86_64",
        python_version="3.14.0",
    )

    assert profile.hostname == "test-host"
    assert profile.operating_system == "Linux"
    assert profile.architecture == "x86_64"


def test_host_profile_to_dict():
    profile = HostProfile(
        hostname="test-host",
        operating_system="Linux",
        os_release="test-release",
        platform="test-platform",
        architecture="x86_64",
        python_version="3.14.0",
        interfaces=[
            {
                "interface": "lo",
                "state": "up",
                "ipv4": "127.0.0.1",
            }
        ],
    )

    data = profile.to_dict()

    assert data["hostname"] == "test-host"
    assert data["operating_system"] == "Linux"
    assert len(data["interfaces"]) == 1
    assert data["interfaces"][0]["interface"] == "lo"
