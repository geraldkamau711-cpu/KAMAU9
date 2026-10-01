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


def test_k9_summary_distinguishes_modules_with_and_without_findings():
    k9 = K9Core()

    k9.register_module(HostIntelligenceModule())
    k9.register_module(NetworkInterfaceModule())

    k9.start_assessment("localhost")

    k9.build_host_profile()

    summary = k9.build_assessment_summary()

    assert summary["modules_with_findings"] == [
        "host_intelligence",
        "network_interfaces",
    ]

    assert summary["modules_without_findings"] == []


def test_k9_summary_tracks_module_statuses():
    k9 = K9Core()

    k9.register_module(HostIntelligenceModule())
    k9.register_module(NetworkInterfaceModule())

    k9.start_assessment("localhost")

    k9.build_host_profile()

    summary = k9.build_assessment_summary()

    assert summary["module_statuses"] == {
        "host_intelligence": "success",
        "network_interfaces": "success",
    }
    assert summary["modules_total"] == 2
    assert summary["modules_succeeded"] == 2
    assert summary["modules_failed"] == 0


class FailingSummaryModule:
    name = "failing_summary_module"

    def run(self, context):
        raise RuntimeError("summary module failure")


def test_k9_failed_module_appears_in_assessment_summary():
    k9 = K9Core()

    k9.register_module(FailingSummaryModule())
    k9.start_assessment("localhost")

    try:
        k9.run_module("failing_summary_module")
    except RuntimeError as exc:
        assert str(exc) == "summary module failure"
    else:
        raise AssertionError("Expected RuntimeError")

    summary = k9.build_assessment_summary()

    assert summary["modules"] == [
        "failing_summary_module",
    ]
    assert summary["modules_with_findings"] == []
    assert summary["modules_without_findings"] == [
        "failing_summary_module",
    ]
    assert summary["module_statuses"] == {
        "failing_summary_module": "failed",
    }
    assert summary["modules_total"] == 1
    assert summary["modules_succeeded"] == 0
    assert summary["modules_failed"] == 1
