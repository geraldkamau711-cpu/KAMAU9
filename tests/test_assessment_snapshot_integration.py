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


def test_k9_snapshot_contains_failed_module_execution_count():
    from core.module import K9Module

    class FailingSnapshotModule(K9Module):
        name = "failing_snapshot_module"

        def run(self, context):
            raise RuntimeError("snapshot module failure")

    k9 = K9Core()
    k9.register_module(FailingSnapshotModule())
    k9.start_assessment("localhost")

    try:
        k9.run_module("failing_snapshot_module")
    except RuntimeError as exc:
        assert str(exc) == "snapshot module failure"
    else:
        raise AssertionError("Expected RuntimeError")

    snapshot = k9.create_assessment_snapshot()

    assert snapshot.modules_total == 1
    assert snapshot.modules_succeeded == 0
    assert snapshot.modules_failed == 1


def test_k9_comparison_uses_real_assessment_snapshots():
    from core.assessment_comparison import AssessmentComparison
    from core.module import K9Module

    class FailingComparisonModule(K9Module):
        name = "failing_comparison_module"

        def run(self, context):
            raise RuntimeError("comparison module failure")

    k9 = K9Core()

    k9.register_module(HostIntelligenceModule())
    k9.register_module(NetworkInterfaceModule())
    k9.register_module(FailingComparisonModule())

    k9.start_assessment("localhost")
    k9.build_host_profile()
    previous = k9.create_assessment_snapshot()

    k9.start_assessment("localhost")
    k9.build_host_profile()

    try:
        k9.run_module("failing_comparison_module")
    except RuntimeError as exc:
        assert str(exc) == "comparison module failure"
    else:
        raise AssertionError("Expected RuntimeError")

    current = k9.create_assessment_snapshot()

    result = AssessmentComparison().compare(previous, current)

    assert result["previous_assessment_id"] != result["current_assessment_id"]
    assert result["module_execution_counts"] == {
        "previous": {
            "total": 2,
            "succeeded": 2,
            "failed": 0,
        },
        "current": {
            "total": 3,
            "succeeded": 2,
            "failed": 1,
        },
    }
