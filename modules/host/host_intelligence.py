import platform
import socket
import sys

from core.finding import Finding
from core.module import K9Module


class HostIntelligenceModule(K9Module):
    """Collect non-invasive intelligence about the local host."""

    name = "host_intelligence"

    def run(self, context):
        hostname = socket.gethostname()

        host_data = {
            "hostname": hostname,
            "os": platform.system(),
            "os_release": platform.release(),
            "platform": platform.platform(),
            "architecture": platform.machine(),
            "python_version": sys.version.split()[0],
        }

        finding = Finding(
            title="Local host intelligence collected",
            severity="info",
            description=(
                "K9 collected non-invasive operating-system and "
                "runtime information from the local host."
            ),
            source=self.name,
            target=hostname,
            evidence=host_data,
        )

        return {
            "module": self.name,
            "status": "ok",
            "target": hostname,
            "findings": [finding],
        }
