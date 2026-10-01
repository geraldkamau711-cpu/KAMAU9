from core.config import K9Config
from core.main import K9Core
from core.mode import K9Mode
from core.module import K9Module


class ContextCaptureModule(K9Module):
    name = "context_capture"
    supported_modes = frozenset(
        {K9Mode.LAB, K9Mode.ANALYSIS, K9Mode.CRYPTO}
    )

    def __init__(self):
        self.received_context = None

    def run(self, context):
        self.received_context = context
        return {"findings": []}


class CryptoOnlyModule(K9Module):
    name = "crypto_only"
    supported_modes = frozenset({K9Mode.CRYPTO})

    def run(self, context):
        return {"findings": []}


def test_core_registers_module_supported_by_active_mode():
    core = K9Core(K9Config(mode=K9Mode.CRYPTO))
    module = CryptoOnlyModule()

    core.register_module(module)

    assert core.registry.list_modules() == ["crypto_only"]


def test_core_rejects_module_unsupported_by_active_mode():
    core = K9Core(K9Config(mode=K9Mode.LAB))
    module = CryptoOnlyModule()

    try:
        core.register_module(module)
    except ValueError as exc:
        assert str(exc) == (
            "Module 'crypto_only' does not support K9 mode 'lab'."
        )
    else:
        raise AssertionError("Expected ValueError")

    assert core.registry.list_modules() == []


def test_core_loader_uses_configured_mode():
    core = K9Core(K9Config(mode=K9Mode.CRYPTO))

    assert core.loader.mode is K9Mode.CRYPTO


def test_core_defaults_to_lab_mode():
    core = K9Core()

    assert core.config.mode is K9Mode.LAB
    assert core.loader.mode is K9Mode.LAB


def test_core_accepts_string_mode():
    core = K9Core(K9Config(mode="analysis"))

    assert core.config.mode is K9Mode.ANALYSIS
    assert core.loader.mode is K9Mode.ANALYSIS


def test_run_module_passes_active_mode_to_execution_context():
    core = K9Core(K9Config(mode=K9Mode.CRYPTO))
    module = ContextCaptureModule()

    core.register_module(module)
    core.start_assessment("test-target")
    core.run_module(module.name)

    assert module.received_context["mode"] is K9Mode.CRYPTO


def test_run_module_passes_assessment_context():
    core = K9Core(K9Config(mode=K9Mode.LAB))
    module = ContextCaptureModule()

    core.register_module(module)
    assessment = core.start_assessment("test-target")
    core.run_module(module.name)

    assert module.received_context["target"] == "test-target"
    assert module.received_context["assessment_id"] == assessment.assessment_id


def test_run_module_does_not_allow_mode_override():
    core = K9Core(K9Config(mode=K9Mode.CRYPTO))
    module = ContextCaptureModule()

    core.register_module(module)
    core.start_assessment("test-target")
    core.run_module(module.name, {"mode": K9Mode.LAB})

    assert module.received_context["mode"] is K9Mode.CRYPTO


def test_run_module_stores_structured_result_in_assessment_context():
    core = K9Core(K9Config(mode=K9Mode.LAB))
    module = ContextCaptureModule()

    core.register_module(module)
    core.start_assessment("test-target")

    result = core.run_module(module.name)

    assert core.context.module_results[module.name] is result
    assert core.context.module_results[module.name] == {
        "findings": [],
    }


def test_run_module_updates_existing_module_result():
    core = K9Core(K9Config(mode=K9Mode.LAB))
    module = ContextCaptureModule()

    core.register_module(module)
    core.start_assessment("test-target")

    first = core.run_module(module.name)
    second = core.run_module(module.name)

    assert core.context.module_results[module.name] is second
    assert core.context.module_results[module.name] is not first


def test_run_module_stores_result_through_context_api():
    core = K9Core(K9Config(mode=K9Mode.LAB))
    module = ContextCaptureModule()

    core.register_module(module)
    core.start_assessment("test-target")

    result = core.run_module(module.name)

    assert core.context.get_module_result(module.name) is result


def test_run_module_passes_read_only_module_result_view():
    core = K9Core(K9Config(mode=K9Mode.LAB))
    module = ContextCaptureModule()

    core.register_module(module)
    core.start_assessment("test-target")

    core.run_module(module.name)

    view = module.received_context["module_results"]

    assert view.has(module.name) is True
    assert view.get(module.name)["findings"] == []


def test_run_module_module_result_view_reflects_previous_results():
    core = K9Core(K9Config(mode=K9Mode.LAB))

    first = ContextCaptureModule()
    first.name = "first_module"

    second = ContextCaptureModule()
    second.name = "second_module"

    core.register_module(first)
    core.register_module(second)
    core.start_assessment("test-target")

    core.run_module(first.name)
    core.run_module(second.name)

    view = second.received_context["module_results"]

    assert view.has("first_module") is True
    assert view.get("first_module") == {
        "findings": [],
    }
    assert view.has("second_module") is True


class FailingModule(K9Module):
    name = "failing_module"

    def run(self, context):
        raise RuntimeError("module failure")


def test_run_module_records_success_status():
    core = K9Core(K9Config(mode=K9Mode.LAB))
    module = ContextCaptureModule()

    core.register_module(module)
    core.start_assessment("test-target")
    core.run_module(module.name)

    assert core.context.get_module_status(module.name) == "success"


def test_run_module_records_failed_status():
    core = K9Core(K9Config(mode=K9Mode.LAB))
    module = FailingModule()

    core.register_module(module)
    core.start_assessment("test-target")

    try:
        core.run_module(module.name)
    except RuntimeError as exc:
        assert str(exc) == "module failure"
    else:
        raise AssertionError("Expected RuntimeError")

    assert core.context.get_module_status(module.name) == "failed"


def test_failed_module_does_not_store_module_result():
    core = K9Core(K9Config(mode=K9Mode.LAB))
    module = FailingModule()

    core.register_module(module)
    core.start_assessment("test-target")

    try:
        core.run_module(module.name)
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected RuntimeError")

    assert core.context.get_module_result(module.name) is None
