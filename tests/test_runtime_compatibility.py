"""Verify the compatibility patch without runtime setuptools or pip."""

from types import SimpleNamespace
import builtins

from pypiserver.config import html_file_arg, strtobool
from pypiserver.manage import PipCmd, update_package
import pytest


@pytest.mark.parametrize("value", ["y", "YES", "t", "True", "on", "1"])
def test_true_boolean_values(value):
    assert strtobool(value) is True


@pytest.mark.parametrize("value", ["n", "NO", "f", "False", "off", "0"])
def test_false_boolean_values(value):
    assert strtobool(value) is False


def test_invalid_boolean_rejected():
    with pytest.raises(ValueError, match="invalid truth value"):
        strtobool("maybe")


def test_packaged_and_custom_welcome_templates(tmp_path):
    assert "<html" in html_file_arg(None)
    assert html_file_arg("pypiserver/welcome.html") == html_file_arg(None)
    custom = tmp_path / "welcome.html"
    custom.write_text("Custom welcome ✓", encoding="utf-8")
    assert html_file_arg(str(custom)) == "Custom welcome ✓"


@pytest.mark.parametrize(
    "version,operation",
    [
        ("9.0.3", "install"),
        ("10.0", "download"),
        ("26.3", "download"),
        ("10.0.0rc10", "download"),
        ("10.0.0b10", "download"),
        ("10.0.0.dev8", "download"),
    ],
)
def test_legacy_update_command_version_comparison(version, operation):
    assert list(PipCmd.update_root(version)) == ["pip", "-q", operation]


def test_update_command_explains_missing_optional_pip(monkeypatch):
    original = builtins.__import__

    def no_pip(name, *args, **kwargs):
        if name == "pip":
            raise ImportError("pip is not installed")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_pip)
    with pytest.raises(RuntimeError, match="optional 'update' extra"):
        update_package(SimpleNamespace(), None)
