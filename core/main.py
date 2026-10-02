from core.assessment_comparison import AssessmentComparison
from core.assessment_intelligence import AssessmentIntelligence
from core.assessment_persistence import AssessmentPersistence
from core.assessment_snapshot import AssessmentSnapshot
from core.assessment_summary import AssessmentSummary
from core.assessment_trend import AssessmentTrend
from core.config import K9Config
from core.context import AssessmentContext
from core.evidence import EvidenceStore
from core.host_profile_builder import HostProfileBuilder
from core.loader import ModuleLoader
from core.logger import get_logger
from core.registry import ModuleRegistry


class K9Core:
    """Central K9 orchestrator."""

    def __init__(
        self,
        config: K9Config | None = None,
        persistence: AssessmentPersistence | None = None,
    ):
        self.config = config or K9Config()
        self.persistence = persistence
        self.logger = get_logger("K9")
        self.registry = ModuleRegistry()
        self.loader = ModuleLoader(self.registry, mode=self.config.mode)
        self.evidence = EvidenceStore()
        self.context: AssessmentContext | None = None

    def _require_persistence(self) -> AssessmentPersistence:
        """Return the configured assessment persistence layer."""
        if self.persistence is None:
            raise RuntimeError(
                "Assessment persistence is not configured."
            )

        return self.persistence

    def load_modules(self, path: str = "config/modules.json"):
        self.loader.load_from_file(path)

    def register_module(self, module):
        if not module.supports_mode(self.config.mode):
            raise ValueError(
                f"Module {module.name!r} does not support K9 mode "
                f"{self.config.mode.value!r}."
            )

        self.registry.register(module)

    def start_assessment(self, target: str):
        self.context = AssessmentContext(target=target)

        self.logger.info(
            "Assessment started: %s",
            self.context.assessment_id,
        )
        self.logger.info(
            "Assessment target: %s",
            self.context.target,
        )

        return self.context

    def build_host_profile(self):
        """Build a unified HostProfile from local host intelligence."""

        if self.context is None:
            raise RuntimeError("No active assessment.")

        self.run_module("host_intelligence")
        self.run_module("network_interfaces")

        host_result = self.context.get_module_result(
            "host_intelligence"
        )
        interface_result = self.context.get_module_result(
            "network_interfaces"
        )

        if host_result is None:
            raise RuntimeError(
                "Host intelligence produced no result."
            )

        if interface_result is None:
            raise RuntimeError(
                "Network interface intelligence produced no result."
            )

        host_findings = host_result.get("findings", [])
        interface_findings = interface_result.get("findings", [])

        if not host_findings:
            raise RuntimeError(
                "Host intelligence produced no findings."
            )

        host_evidence = host_findings[0].evidence

        interface_evidence = [
            finding.evidence
            for finding in interface_findings
        ]

        builder = HostProfileBuilder()

        profile = builder.build(
            host_finding=host_evidence,
            interface_findings=interface_evidence,
        )

        self.context.host_profile = profile

        self.logger.info(
            "Host profile built: %s | interfaces=%d",
            profile.hostname,
            len(profile.interfaces),
        )

        return profile

    def build_assessment_summary(self):
        """Build a summary from the current assessment evidence."""

        if self.context is None:
            raise RuntimeError("No active assessment.")

        summary_builder = AssessmentSummary(
            target=self.context.target,
            assessment_id=self.context.assessment_id,
        )

        return summary_builder.build(
            self.evidence.all(),
            modules=self.context.list_module_results(),
            module_statuses=self.context.list_module_statuses(),
        )

    def create_assessment_snapshot(self):
        """Create an immutable snapshot of the current assessment."""

        if self.context is None:
            raise RuntimeError("No active assessment.")

        summary = self.build_assessment_summary()

        return AssessmentSnapshot(
            assessment_id=self.context.assessment_id,
            target=self.context.target,
            started_at=self.context.started_at,
            finding_count=summary["finding_count"],
            severity_counts=summary["severity_counts"],
            sources=summary["sources"],
            modules_total=summary["modules_total"],
            modules_succeeded=summary["modules_succeeded"],
            modules_failed=summary["modules_failed"],
        )

    def save_assessment_snapshot(self) -> AssessmentSnapshot:
        """Create and persist the current assessment snapshot."""
        persistence = self._require_persistence()

        snapshot = self.create_assessment_snapshot()
        persistence.save(snapshot)

        return snapshot

    def load_assessment_snapshot(
        self,
        assessment_id: str,
    ) -> AssessmentSnapshot:
        """Load a persisted assessment snapshot."""
        persistence = self._require_persistence()

        return persistence.load(assessment_id)

    def list_assessments(self) -> list[str]:
        """List persisted assessment IDs."""
        persistence = self._require_persistence()

        return persistence.list_assessments()

    def list_assessment_snapshots(self) -> list[AssessmentSnapshot]:
        """Load all persisted assessment snapshots in deterministic order."""
        persistence = self._require_persistence()

        return [
            persistence.load(assessment_id)
            for assessment_id in persistence.list_assessments()
        ]

    def list_assessment_targets(self) -> list[str]:
        """List persisted assessment targets in deterministic order."""
        persistence = self._require_persistence()

        return list(
            self.list_assessment_snapshots_by_target().keys()
        )

    def list_assessment_snapshots_by_target(
        self,
    ) -> dict[str, list[AssessmentSnapshot]]:
        """Group persisted assessment snapshots by target chronologically."""
        persistence = self._require_persistence()

        grouped: dict[str, list[AssessmentSnapshot]] = {}

        for snapshot in self.list_assessment_snapshots():
            grouped.setdefault(
                snapshot.target,
                [],
            ).append(snapshot)

        for target in grouped:
            grouped[target].sort(
                key=lambda snapshot: snapshot.started_at,
            )

        return dict(
            sorted(
                grouped.items(),
                key=lambda item: item[0],
            )
        )

    def get_latest_assessment_snapshots_by_target(
        self,
    ) -> dict[str, AssessmentSnapshot]:
        """Load the latest persisted assessment snapshot for each target."""
        persistence = self._require_persistence()

        grouped = self.list_assessment_snapshots_by_target()

        return {
            target: snapshots[-1]
            for target, snapshots in grouped.items()
            if snapshots
        }

    def get_latest_assessment_snapshot_pairs_by_target(
        self,
    ) -> dict[str, tuple[AssessmentSnapshot, AssessmentSnapshot]]:
        """Load the previous and latest persisted snapshot for each target."""
        persistence = self._require_persistence()

        grouped = self.list_assessment_snapshots_by_target()

        return {
            target: (snapshots[-2], snapshots[-1])
            for target, snapshots in grouped.items()
            if len(snapshots) >= 2
        }

    def get_latest_assessment_snapshot_pair_for_target(
        self,
        target: str,
    ) -> tuple[AssessmentSnapshot, AssessmentSnapshot] | None:
        """Load the previous and latest persisted snapshot for a target."""
        persistence = self._require_persistence()

        return self.get_latest_assessment_snapshot_pairs_by_target().get(
            target,
        )

    def get_latest_assessment_snapshot(
        self,
    ) -> AssessmentSnapshot | None:
        """Load the most recently started persisted assessment snapshot."""
        persistence = self._require_persistence()

        snapshots = self.list_assessment_snapshots()

        if not snapshots:
            return None

        return max(
            snapshots,
            key=lambda snapshot: snapshot.started_at,
        )

    def list_assessment_snapshots_for_target(
        self,
        target: str,
    ) -> list[AssessmentSnapshot]:
        """Load persisted assessment snapshots for a target chronologically."""
        persistence = self._require_persistence()

        return self.list_assessment_snapshots_by_target().get(
            target,
            [],
        )

    def list_assessment_snapshot_pairs_for_target(
        self,
        target: str,
    ) -> list[
        tuple[AssessmentSnapshot, AssessmentSnapshot]
    ]:
        """Load consecutive persisted snapshot pairs for a target."""
        persistence = self._require_persistence()

        snapshots = self.list_assessment_snapshots_for_target(
            target,
        )

        return list(
            zip(
                snapshots,
                snapshots[1:],
            )
        )

    def get_latest_assessment_snapshot_for_target(
        self,
        target: str,
    ) -> AssessmentSnapshot | None:
        """Load the most recently started snapshot for a target."""
        persistence = self._require_persistence()

        return self.get_latest_assessment_snapshots_by_target().get(
            target,
        )

    def compare_assessment_snapshots(
        self,
        previous_assessment_id: str,
        current_assessment_id: str,
    ) -> dict:
        """Compare two persisted assessment snapshots."""
        persistence = self._require_persistence()

        previous = self.load_assessment_snapshot(
            previous_assessment_id,
        )
        current = self.load_assessment_snapshot(
            current_assessment_id,
        )

        return AssessmentComparison().compare(
            previous,
            current,
        )

    def compare_latest_assessment_snapshots_for_target(
        self,
        target: str,
    ) -> dict | None:
        """Compare the two most recent persisted snapshots for a target."""
        persistence = self._require_persistence()

        snapshot_pair = (
            self.get_latest_assessment_snapshot_pair_for_target(
                target,
            )
        )

        if snapshot_pair is None:
            return None

        previous, current = snapshot_pair

        return self.compare_assessment_snapshots(
            previous.assessment_id,
            current.assessment_id,
        )

    def compare_assessment_history_for_target(
        self,
        target: str,
    ) -> list[dict]:
        """Compare every consecutive persisted snapshot for a target."""
        persistence = self._require_persistence()

        snapshot_pairs = (
            self.list_assessment_snapshot_pairs_for_target(
                target,
            )
        )

        return [
            self.compare_assessment_snapshots(
                previous.assessment_id,
                current.assessment_id,
            )
            for previous, current in snapshot_pairs
        ]

    def summarise_assessment_trend_for_target(
        self,
        target: str,
    ) -> dict:
        """Summarise finding-count trends across a target's assessments."""
        comparisons = self.compare_assessment_history_for_target(
            target,
        )

        return AssessmentTrend().summarise(comparisons)

    def analyse_assessment_trend_for_target(
        self,
        target: str,
    ) -> dict:
        """Analyse the descriptive state of a target's assessment trend."""
        trend = self.summarise_assessment_trend_for_target(target)

        return AssessmentIntelligence().analyse(trend)

    def analyse_assessment_trends_for_all_targets(
        self,
    ) -> dict[str, dict]:
        """Analyse assessment trends for every persisted target."""
        targets = self.list_assessment_targets()

        return {
            target: self.analyse_assessment_trend_for_target(
                target,
            )
            for target in targets
        }

    def summarise_assessment_trends_for_all_targets(
        self,
    ) -> dict[str, dict]:
        """Summarise assessment trends for every persisted target."""
        targets = self.list_assessment_targets()

        return {
            target: self.summarise_assessment_trend_for_target(
                target,
            )
            for target in targets
        }

    def compare_latest_assessment_snapshots_for_all_targets(
        self,
    ) -> dict[str, dict]:
        """Compare the two most recent persisted snapshots for each target."""
        persistence = self._require_persistence()

        snapshot_pairs = (
            self.get_latest_assessment_snapshot_pairs_by_target()
        )

        return {
            target: self.compare_assessment_snapshots(
                previous.assessment_id,
                current.assessment_id,
            )
            for target, (previous, current) in snapshot_pairs.items()
        }

    def run_module(self, name: str, context: dict | None = None):
        module = self.registry.get(name)

        if self.context is None:
            raise RuntimeError("No active assessment.")

        execution_context = {
            "target": self.context.target,
            "assessment_id": self.context.assessment_id,
            "module_results": self.context.module_result_view(),
            **(context or {}),
            "mode": self.config.mode,
        }

        self.logger.info(
            "Executing module: %s",
            name,
        )

        try:
            result = module.run(execution_context)

            if not isinstance(result, dict):
                raise TypeError(
                    "K9 modules must return a dictionary result."
                )

            self.context.store_module_result(name, result)
            self.context.store_module_status(name, "success")

        except Exception:
            self.context.store_module_status(name, "failed")
            self.logger.exception(
                "Module failed: %s",
                name,
            )
            raise

        for finding in result.get("findings", []):
            self.evidence.add(finding)

        self.logger.info(
            "Module completed: %s | findings=%d",
            name,
            len(result.get("findings", [])),
        )

        return result

    def start(self):
        self.logger.info(
            "%s Core v%s starting...",
            self.config.name,
            self.config.version,
        )
        self.logger.info(
            "Operating mode: %s",
            self.config.mode,
        )

        self.load_modules()

        self.logger.info(
            "Loaded modules: %s",
            self.registry.list_modules() or "none",
        )


if __name__ == "__main__":
    K9Core().start()
