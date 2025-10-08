"""Allow ``python -m video_downloader`` to launch the application."""

from .app import run

if __name__ == "__main__":  # pragma: no cover - module entry point
    run()
