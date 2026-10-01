from core.config import K9Config
from core.main import K9Core
from core.mode import K9Mode


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
