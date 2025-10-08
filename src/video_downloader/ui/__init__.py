"""User interface components for the Video Downloader application."""

from .about import build_about_dialog, get_debug_info
from .authentication import LoginDialog, PasswordDialog
from .playlist import PlaylistDialog
from .shortcuts import ShortcutsDialog
from .window import Window

__all__ = [
    "LoginDialog",
    "PasswordDialog",
    "PlaylistDialog",
    "ShortcutsDialog",
    "Window",
    "build_about_dialog",
    "get_debug_info",
]
