from core.main import K9Core
from modules.host.host_intelligence import HostIntelligenceModule
from modules.host.network_interfaces import NetworkInterfaceModule


def test_k9_creates_assessment_snapshot():
    k9 = K9Core()

    k9.register_module(HostIntelligenceModule())
    k9.register_module(NetworkInterfaceModule())

    context = k9.start_assessment("localhost")

    k9.build_host_profile()

    snapshot = k9.create_assessment_snapshot()

    assert snapshot.assessment_id == context.assessment_id
    assert snapshot.target == context.target
    assert snapshot.started_at == context.started_at
    assert snapshot.finding_count == k9.evidence.count()


def test_k9_snapshot_contains_evidence_statistics():
    k9 = K9Core()

    k9.register_module(HostIntelligenceModule())
    k9.register_module(NetworkInterfaceModule())

    k9.start_assessment("localhost")

    k9.build_host_profile()

    snapshot = k9.create_assessment_snapshot()

    assert snapshot.finding_count >= 2
    assert "host_intelligence" in snapshot.sources
    assert "network_interfaces" in snapshot.sources
    assert "info" in snapshot.severity_counts


def test_k9_snapshot_contains_module_execution_counts():
    k9 = K9Core()

    k9.register_module(HostIntelligenceModule())
    k9.register_module(NetworkInterfaceModule())

    k9.start_assessment("localhost")

    k9.build_host_profile()

    snapshot = k9.create_assessment_snapshot()

    assert snapshot.modules_total == 2
    assert snapshot.modules_succeeded == 2
    assert snapshot.modules_failed == 0


def test_k9_snapshot_serialises_module_execution_counts():
    k9 = K9Core()

    k9.register_module(HostIntelligenceModule())
    k9.register_module(NetworkInterfaceModule())

    k9.start_assessment("localhost")

    k9.build_host_profile()

    result = k9.create_assessment_snapshot().to_dict()

    assert result["modules_total"] == 2
    assert result["modules_succeeded"] == 2
    assert result["modules_failed"] == 0
