from core.assessment_comparison_service import (
    AssessmentComparisonService,
)
from core.assessment_intelligence import AssessmentIntelligence
from core.assessment_intelligence_result import (
    AssessmentIntelligenceResult,
)
from core.assessment_trend import AssessmentTrend
from core.assessment_trend_result import AssessmentTrendResult


class AssessmentTrendService:
    """Coordinate assessment comparison, trend, and intelligence logic."""

    def __init__(
        self,
        comparison_service: AssessmentComparisonService,
        intelligence: AssessmentIntelligence | None = None,
    ):
        self.comparison_service = comparison_service
        self.trend = AssessmentTrend()
        self.intelligence = intelligence or AssessmentIntelligence()

    def summarise_assessment_trend_for_target(
        self,
        target: str,
    ) -> AssessmentTrendResult:
        """Summarise assessment trends for a target."""
        comparisons = (
            self.comparison_service
            .compare_assessment_history_for_target(target)
        )

        return self.trend.summarise(comparisons)

    def analyse_assessment_trend_for_target(
        self,
        target: str,
    ) -> AssessmentIntelligenceResult:
        """Analyse the descriptive trend state for a target."""
        trend = self.summarise_assessment_trend_for_target(target)

        return self.intelligence.analyse(trend)

    def summarise_assessment_trends_for_all_targets(
        self,
    ) -> dict[str, AssessmentTrendResult]:
        """Summarise assessment trends for every persisted target."""
        targets = self.comparison_service.list_targets()

        return {
            target: self.summarise_assessment_trend_for_target(
                target,
            )
            for target in targets
        }

    def analyse_assessment_trends_for_all_targets(
        self,
    ) -> dict[str, AssessmentIntelligenceResult]:
        """Analyse assessment trends for every persisted target."""
        targets = self.comparison_service.list_targets()

        return {
            target: self.analyse_assessment_trend_for_target(
                target,
            )
            for target in targets
        }
