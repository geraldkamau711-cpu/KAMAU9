from core.main import K9Core
from modules.host.host_intelligence import HostIntelligenceModule
from modules.host.network_interfaces import NetworkInterfaceModule


def test_k9_builds_host_profile_during_assessment():
    k9 = K9Core()

    k9.register_module(HostIntelligenceModule())
    k9.register_module(NetworkInterfaceModule())

    context = k9.start_assessment("localhost")

    profile = k9.build_host_profile()

    assert context.host_profile is profile
    assert profile.hostname
    assert profile.operating_system
    assert profile.os_release
    assert profile.platform
    assert profile.architecture
    assert profile.python_version

    assert isinstance(profile.interfaces, list)


def test_k9_profile_build_preserves_evidence():
    k9 = K9Core()

    k9.register_module(HostIntelligenceModule())
    k9.register_module(NetworkInterfaceModule())

    k9.start_assessment("localhost")

    profile = k9.build_host_profile()

    assert profile.hostname
    assert k9.evidence.count() >= 2
