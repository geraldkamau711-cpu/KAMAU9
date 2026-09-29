import os
import socket
import struct

from core.finding import Finding
from core.module import K9Module


class NetworkInterfaceModule(K9Module):
    """Collect non-invasive information about local network interfaces."""

    name = "network_interfaces"

    def _read_interface_state(self, interface):
        path = f"/sys/class/net/{interface}/operstate"

        try:
            with open(path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except OSError:
            return "unknown"

    def _read_mac_address(self, interface):
        path = f"/sys/class/net/{interface}/address"

        try:
            with open(path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except OSError:
            return "unknown"

    def _get_ipv4_address(self, interface):
        """Get IPv4 address using the local socket interface."""

        try:
            import fcntl

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            result = fcntl.ioctl(
                sock.fileno(),
                0x8915,
                struct.pack(
                    "256s",
                    interface[:15].encode("utf-8"),
                ),
            )

            sock.close()

            return socket.inet_ntoa(result[20:24])

        except (OSError, ImportError):
            return None

    def run(self, context):
        hostname = socket.gethostname()
        findings = []

        try:
            interfaces = sorted(os.listdir("/sys/class/net"))
        except OSError:
            interfaces = []

        for interface in interfaces:
            evidence = {
                "interface": interface,
                "state": self._read_interface_state(interface),
                "mac_address": self._read_mac_address(interface),
            }

            ipv4 = self._get_ipv4_address(interface)

            if ipv4:
                evidence["ipv4"] = ipv4

            finding = Finding(
                title="Local network interface discovered",
                severity="info",
                description=(
                    "K9 discovered a local network interface and "
                    "collected non-invasive metadata."
                ),
                source=self.name,
                target=hostname,
                evidence=evidence,
            )

            findings.append(finding)

        return {
            "module": self.name,
            "status": "ok",
            "target": hostname,
            "findings": findings,
        }
