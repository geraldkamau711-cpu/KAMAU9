from core.host_profile import HostProfile


class HostProfileBuilder:
    """Build a unified HostProfile from collector evidence."""

    def build(
        self,
        host_finding: dict,
        interface_findings: list[dict],
    ) -> HostProfile:
        return HostProfile(
            hostname=host_finding["hostname"],
            operating_system=host_finding["os"],
            os_release=host_finding["os_release"],
            platform=host_finding["platform"],
            architecture=host_finding["architecture"],
            python_version=host_finding["python_version"],
            interfaces=list(interface_findings),
        )
