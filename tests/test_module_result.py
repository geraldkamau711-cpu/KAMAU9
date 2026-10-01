import pytest

from core.module_result import ModuleResultView


def test_module_result_view_returns_existing_result():
    results = {
        "example": {
            "status": "ok",
            "findings": [],
        }
    }

    view = ModuleResultView(results)

    result = view.get("example")

    assert result is not None
    assert result["status"] == "ok"
    assert result["findings"] == []


def test_module_result_view_returns_none_for_unknown_result():
    view = ModuleResultView({})

    assert view.get("unknown") is None


def test_module_result_view_reports_existing_result():
    view = ModuleResultView(
        {
            "example": {
                "status": "ok",
            }
        }
    )

    assert view.has("example") is True
    assert view.has("unknown") is False


def test_module_result_view_lists_result_names():
    view = ModuleResultView(
        {
            "host_intelligence": {"status": "ok"},
            "network_interfaces": {"status": "ok"},
        }
    )

    assert view.names() == [
        "host_intelligence",
        "network_interfaces",
    ]


def test_module_result_view_does_not_allow_top_level_mutation():
    results = {
        "example": {
            "status": "ok",
        }
    }

    view = ModuleResultView(results)
    result = view.get("example")

    assert result is not None

    with pytest.raises(TypeError):
        result["status"] = "changed"

    assert results["example"]["status"] == "ok"


def test_module_result_view_reflects_newly_stored_results():
    results = {}
    view = ModuleResultView(results)

    assert view.names() == []

    results["example"] = {"status": "ok"}

    assert view.has("example") is True
    assert view.get("example")["status"] == "ok"


def test_assessment_context_exposes_module_result_view():
    from core.context import AssessmentContext

    context = AssessmentContext(target="lab-target")
    context.store_module_result(
        "example",
        {
            "status": "ok",
        },
    )

    view = context.module_result_view()

    assert view.has("example") is True
    assert view.get("example")["status"] == "ok"
    assert view.names() == ["example"]
