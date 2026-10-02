from core.main import K9Core


def test_k9_core_exposes_assessment_comparison_service(tmp_path):
    core = K9Core()
    core.persistence = core.persistence or __import__(
        "core.assessment_persistence",
        fromlist=["AssessmentPersistence"],
    ).AssessmentPersistence(tmp_path)

    service = core._require_assessment_comparison_service()

    from core.assessment_comparison_service import (
        AssessmentComparisonService,
    )

    assert isinstance(service, AssessmentComparisonService)
