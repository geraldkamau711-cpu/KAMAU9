import platform
import socket
import sys

from modules.host.host_intelligence import HostIntelligenceModule


def test_host_intelligence_module_name():
    module = HostIntelligenceModule()

    assert module.name == "host_intelligence"


def test_host_intelligence_collects_local_host_data():
    module = HostIntelligenceModule()

    result = module.run({})

    assert result["module"] == "host_intelligence"
    assert result["status"] == "ok"
    assert result["target"] == socket.gethostname()

    assert len(result["findings"]) == 1

    finding = result["findings"][0]

    assert finding.title == "Local host intelligence collected"
    assert finding.severity == "info"
    assert finding.source == "host_intelligence"

    evidence = finding.evidence

    assert evidence["hostname"] == socket.gethostname()
    assert evidence["os"] == platform.system()
    assert evidence["os_release"] == platform.release()
    assert evidence["platform"] == platform.platform()
    assert evidence["architecture"] == platform.machine()
    assert evidence["python_version"] == sys.version.split()[0]
