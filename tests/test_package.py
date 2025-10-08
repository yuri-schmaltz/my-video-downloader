"""Smoke tests that cover the refactored package layout."""

import importlib
import importlib.util
import os
import types

import pytest

import video_downloader

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("gi") is None,
    reason="PyGObject (gi) is required to import the GTK application",
)


def test_get_version_returns_string():
    version = video_downloader.get_version()
    assert isinstance(version, str)
    assert version != ""


def test_legacy_modules_remain_importable():
    for name in [
        "about_dialog",
        "authentication_dialog",
        "main",
        "model",
        "playlist_dialog",
        "shortcuts_dialog",
        "window",
    ]:
        module = importlib.import_module(f"video_downloader.{name}")
        assert isinstance(module, types.ModuleType)


def test_languages_from_locale_handles_multiple_environment_variables(monkeypatch):
    monkeypatch.setitem(os.environ, "LANGUAGE", "pt_BR:en_US")
    monkeypatch.delenv("LC_ALL", raising=False)
    languages = video_downloader.util.languages_from_locale()
    assert languages[0].startswith("pt")
    assert "en" in languages


def test_lazy_attributes_resolve_without_side_effects():
    assert callable(video_downloader.run)
    assert hasattr(video_downloader, "Application")
