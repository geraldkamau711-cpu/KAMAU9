from core.context import AssessmentContext


def test_context_creates_id():
    context = AssessmentContext(target="lab-target")

    assert context.target == "lab-target"
    assert context.assessment_id
    assert context.started_at


def test_context_ids_are_unique():
    first = AssessmentContext(target="lab-target")
    second = AssessmentContext(target="lab-target")

    assert first.assessment_id != second.assessment_id


def test_assessment_context_can_store_host_profile():
    from core.host_profile import HostProfile

    profile = HostProfile(
        hostname="test-host",
        operating_system="Linux",
        os_release="test-release",
        platform="test-platform",
        architecture="x86_64",
        python_version="3.14.0",
    )

    context = AssessmentContext(target="localhost")
    context.host_profile = profile

    assert context.host_profile is profile
    assert context.host_profile.hostname == "test-host"


def test_assessment_context_initialises_empty_module_results():
    context = AssessmentContext(target="lab-target")

    assert context.module_results == {}


def test_assessment_context_module_results_are_isolated():
    first = AssessmentContext(target="lab-target")
    second = AssessmentContext(target="lab-target")

    first.module_results["example"] = {"status": "ok"}

    assert first.module_results == {
        "example": {"status": "ok"},
    }
    assert second.module_results == {}
