from core.host_profile import HostProfile


class HostProfileAnalyzer:
    """Derive structured observations from a HostProfile."""

    def analyze(self, profile: HostProfile) -> dict:
        interfaces = profile.interfaces

        active_interfaces = [
            interface
            for interface in interfaces
            if interface.get("state") == "up"
        ]

        ipv4_interfaces = [
            interface
            for interface in interfaces
            if interface.get("ipv4")
        ]

        return {
            "hostname": profile.hostname,
            "operating_system": profile.operating_system,
            "os_release": profile.os_release,
            "platform": profile.platform,
            "architecture": profile.architecture,
            "python_version": profile.python_version,
            "interface_count": len(interfaces),
            "active_interface_count": len(active_interfaces),
            "ipv4_interface_count": len(ipv4_interfaces),
        }
