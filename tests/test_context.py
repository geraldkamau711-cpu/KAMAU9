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


def test_store_module_result_stores_result():
    context = AssessmentContext(target="lab-target")
    result = {"findings": [], "status": "ok"}

    context.store_module_result("example", result)

    assert context.module_results["example"] is result


def test_store_module_result_replaces_existing_result():
    context = AssessmentContext(target="lab-target")
    first = {"status": "first"}
    second = {"status": "second"}

    context.store_module_result("example", first)
    context.store_module_result("example", second)

    assert context.get_module_result("example") is second
    assert context.get_module_result("example") is not first


def test_get_module_result_returns_none_for_unknown_module():
    context = AssessmentContext(target="lab-target")

    assert context.get_module_result("unknown") is None


def test_store_module_result_rejects_empty_name():
    context = AssessmentContext(target="lab-target")

    try:
        context.store_module_result("", {"findings": []})
    except ValueError as exc:
        assert str(exc) == "Module result name must be a non-empty string."
    else:
        raise AssertionError("Expected ValueError")


def test_store_module_result_rejects_non_dictionary_result():
    context = AssessmentContext(target="lab-target")

    try:
        context.store_module_result("example", [])
    except TypeError as exc:
        assert str(exc) == "Module result must be a dictionary."
    else:
        raise AssertionError("Expected TypeError")


def test_has_module_result_returns_false_when_missing():
    context = AssessmentContext(target="lab-target")

    assert context.has_module_result("example") is False


def test_has_module_result_returns_true_when_present():
    context = AssessmentContext(target="lab-target")

    context.store_module_result("example", {"status": "ok"})

    assert context.has_module_result("example") is True


def test_list_module_results_returns_stored_module_names():
    context = AssessmentContext(target="lab-target")

    context.store_module_result("host_intelligence", {"status": "ok"})
    context.store_module_result("network_interfaces", {"status": "ok"})

    assert context.list_module_results() == [
        "host_intelligence",
        "network_interfaces",
    ]


def test_list_module_results_returns_copy_of_names():
    context = AssessmentContext(target="lab-target")

    context.store_module_result("example", {"status": "ok"})

    names = context.list_module_results()
    names.append("another")

    assert context.list_module_results() == ["example"]


def test_context_stores_module_status():
    context = AssessmentContext(target="lab-target")

    context.store_module_status("host_intelligence", "success")

    assert context.get_module_status("host_intelligence") == "success"


def test_context_stores_failed_module_status():
    context = AssessmentContext(target="lab-target")

    context.store_module_status("host_intelligence", "failed")

    assert context.get_module_status("host_intelligence") == "failed"


def test_context_lists_module_statuses_as_copy():
    context = AssessmentContext(target="lab-target")

    context.store_module_status("host_intelligence", "success")

    statuses = context.list_module_statuses()
    statuses["other_module"] = "failed"

    assert context.list_module_statuses() == {
        "host_intelligence": "success",
    }


def test_context_rejects_invalid_module_status():
    context = AssessmentContext(target="lab-target")

    try:
        context.store_module_status("host_intelligence", "unknown")
    except ValueError as exc:
        assert "success" in str(exc)
        assert "failed" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
