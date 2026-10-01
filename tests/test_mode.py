import pytest

from core.config import K9Config
from core.mode import K9Mode


def test_supported_modes():
    assert K9Mode.LAB.value == "lab"
    assert K9Mode.CRYPTO.value == "crypto"
    assert K9Mode.ANALYSIS.value == "analysis"


def test_parse_mode_is_case_insensitive():
    assert K9Mode.parse("LAB") is K9Mode.LAB
    assert K9Mode.parse("Crypto") is K9Mode.CRYPTO
    assert K9Mode.parse(" analysis ") is K9Mode.ANALYSIS


def test_invalid_mode_is_rejected():
    with pytest.raises(ValueError, match="Unsupported K9 mode"):
        K9Mode.parse("hacker")


def test_non_string_mode_is_rejected():
    with pytest.raises(TypeError, match="K9 mode must be a string"):
        K9Mode.parse(123)


def test_config_defaults_to_lab():
    config = K9Config()

    assert config.mode is K9Mode.LAB


def test_config_accepts_string_mode():
    config = K9Config(mode="crypto")

    assert config.mode is K9Mode.CRYPTO
