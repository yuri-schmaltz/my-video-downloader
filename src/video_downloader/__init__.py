"""High level helpers for interacting with Video Downloader."""

from __future__ import annotations
"""High level helpers for interacting with Video Downloader."""

import sys
from importlib import import_module, metadata
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imported for static type checkers only
    from .app.application import Application, build_application, run
    from .app.model import HandlerInterface, Model, check_download_dir

try:  # pragma: no cover - executed during runtime
    __version__ = metadata.version("video-downloader")
except metadata.PackageNotFoundError:  # pragma: no cover - fallback for src checkout
    __version__ = "0.0.0"


__all__ = [
    "Application",
    "HandlerInterface",
    "Model",
    "__version__",
    "app",
    "build_application",
    "check_download_dir",
    "downloader",
    "get_version",
    "run",
    "ui",
    "util",
]


def get_version() -> str:
    """Return the detected package version."""

    return __version__


_LAZY_OBJECTS = {
    "Application": ("app.application", "Application"),
    "HandlerInterface": ("app.model", "HandlerInterface"),
    "Model": ("app.model", "Model"),
    "build_application": ("app.application", "build_application"),
    "check_download_dir": ("app.model", "check_download_dir"),
    "run": ("app.application", "run"),
    "app": ("app", None),
    "downloader": ("downloader", None),
    "ui": ("ui", None),
    "util": ("util", None),
}

_LEGACY_MODULE_ALIASES = {
    "about_dialog": "ui.about",
    "authentication_dialog": "ui.authentication",
    "downloader": "downloader",
    "main": "app.application",
    "model": "app.model",
    "playlist_dialog": "ui.playlist",
    "shortcuts_dialog": "ui.shortcuts",
    "util": "util",
    "window": "ui.window",
}


def __getattr__(name: str):
    """Lazily resolve legacy module paths.

    Historic versions of the project exposed modules such as
    :mod:`video_downloader.window`. The refactor keeps the public API stable by
    loading those modules on demand and caching them in :mod:`sys.modules`.
    """

    if name in _LAZY_OBJECTS:
        module_name, attribute = _LAZY_OBJECTS[name]
        module = import_module(f".{module_name}", __name__)
        if attribute is None:
            value = module
        else:
            value = getattr(module, attribute)
        setattr(sys.modules[__name__], name, value)
        return value
    if name in _LEGACY_MODULE_ALIASES:
        module = import_module(f".{_LEGACY_MODULE_ALIASES[name]}", __name__)
        sys.modules[f"{__name__}.{name}"] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:  # pragma: no cover - simple delegation helper
    return sorted(set(__all__) | set(_LAZY_OBJECTS) | set(_LEGACY_MODULE_ALIASES))
