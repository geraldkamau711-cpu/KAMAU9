from core.main import K9Core
from modules.host.host_intelligence import HostIntelligenceModule
from modules.host.network_interfaces import NetworkInterfaceModule
from modules.host.host_profile_intelligence import (
    HostProfileIntelligenceModule,
)


def test_k9_builds_assessment_summary():
    k9 = K9Core()

    k9.register_module(HostIntelligenceModule())
    k9.register_module(NetworkInterfaceModule())
    k9.register_module(HostProfileIntelligenceModule())

    context = k9.start_assessment("localhost")

    profile = k9.build_host_profile()

    k9.run_module(
        "host_profile_intelligence",
        {"host_profile": profile},
    )

    summary = k9.build_assessment_summary()

    assert summary["target"] == context.target
    assert summary["assessment_id"] == context.assessment_id
    assert summary["finding_count"] >= 3
    assert "host_intelligence" in summary["sources"]
    assert "network_interfaces" in summary["sources"]
    assert "host_profile_intelligence" in summary["sources"]


def test_k9_summary_reflects_actual_evidence():
    k9 = K9Core()

    k9.register_module(HostIntelligenceModule())
    k9.register_module(NetworkInterfaceModule())

    k9.start_assessment("localhost")

    k9.build_host_profile()

    summary = k9.build_assessment_summary()

    assert summary["finding_count"] == k9.evidence.count()
    assert summary["finding_count"] >= 2


def test_k9_summary_tracks_executed_modules():
    k9 = K9Core()

    k9.register_module(HostIntelligenceModule())
    k9.register_module(NetworkInterfaceModule())

    k9.start_assessment("localhost")

    k9.build_host_profile()

    summary = k9.build_assessment_summary()

    assert summary["modules"] == [
        "host_intelligence",
        "network_interfaces",
    ]
