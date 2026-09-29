from core.main import K9Core
from modules.host.host_intelligence import HostIntelligenceModule
from modules.host.network_interfaces import NetworkInterfaceModule
from modules.host.host_profile_intelligence import (
    HostProfileIntelligenceModule,
)


def test_k9_can_analyse_built_host_profile():
    k9 = K9Core()

    k9.register_module(HostIntelligenceModule())
    k9.register_module(NetworkInterfaceModule())
    k9.register_module(HostProfileIntelligenceModule())

    context = k9.start_assessment("localhost")

    profile = k9.build_host_profile()

    result = k9.run_module(
        "host_profile_intelligence",
        {"host_profile": profile},
    )

    assert context.host_profile is profile
    assert result["module"] == "host_profile_intelligence"
    assert result["status"] == "ok"
    assert len(result["findings"]) == 1


def test_k9_stores_profile_intelligence_evidence():
    k9 = K9Core()

    k9.register_module(HostIntelligenceModule())
    k9.register_module(NetworkInterfaceModule())
    k9.register_module(HostProfileIntelligenceModule())

    k9.start_assessment("localhost")

    profile = k9.build_host_profile()

    k9.run_module(
        "host_profile_intelligence",
        {"host_profile": profile},
    )

    findings = k9.evidence.all()

    assert len(findings) >= 3

    intelligence_findings = [
        finding
        for finding in findings
        if finding.source == "host_profile_intelligence"
    ]

    assert len(intelligence_findings) == 1
    assert intelligence_findings[0].title == "Host profile analysed"
