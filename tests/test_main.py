from core.config import K9Config
from core.main import K9Core
from core.mode import K9Mode
from core.module import K9Module


class ContextCaptureModule(K9Module):
    name = "context_capture"

    def __init__(self):
        self.received_context = None

    def run(self, context):
        self.received_context = context
        return {"findings": []}


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
