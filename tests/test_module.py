import pytest

from core.mode import K9Mode
from core.module import K9Module


class LabModule(K9Module):
    name = "lab"

    def run(self, context):
        return None


class CryptoModule(K9Module):
    name = "crypto"
    supported_modes = frozenset({K9Mode.CRYPTO, K9Mode.ANALYSIS})

    def run(self, context):
        return None


class MultiModeModule(K9Module):
    name = "multi"
    supported_modes = frozenset(
        {K9Mode.LAB, K9Mode.CRYPTO, K9Mode.ANALYSIS}
    )

    def run(self, context):
        return None


def test_default_module_supports_lab_and_analysis():
    module = LabModule()

    assert module.supports_mode(K9Mode.LAB)
    assert module.supports_mode(K9Mode.ANALYSIS)
    assert not module.supports_mode(K9Mode.CRYPTO)


def test_module_can_declare_crypto_support():
    module = CryptoModule()

    assert not module.supports_mode(K9Mode.LAB)
    assert module.supports_mode(K9Mode.CRYPTO)
    assert module.supports_mode(K9Mode.ANALYSIS)


def test_module_can_support_multiple_modes():
    module = MultiModeModule()

    assert module.supports_mode(K9Mode.LAB)
    assert module.supports_mode(K9Mode.CRYPTO)
    assert module.supports_mode(K9Mode.ANALYSIS)


def test_supports_mode_accepts_string():
    module = CryptoModule()

    assert module.supports_mode("crypto")
    assert module.supports_mode("ANALYSIS")


def test_supports_mode_rejects_invalid_mode():
    module = LabModule()

    with pytest.raises(ValueError, match="Unsupported K9 mode"):
        module.supports_mode("hacker")
