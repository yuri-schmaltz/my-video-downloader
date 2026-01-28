import os
import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gio

def pytest_sessionstart(session):
    # Add src to sys.path for test discovery if not already there
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    # Register GResource bundle if it exists in builddir
    resource_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "builddir", "src", "video-downloader.gresource"
    ))
    if os.path.exists(resource_path):
        try:
            resource = Gio.Resource.load(resource_path)
            resource._register()
        except Exception as e:
            print(f"Warning: Failed to load GResource: {e}")

    # Point to GSettings schemas in data/
    schema_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    if os.path.exists(os.path.join(schema_dir, "gschemas.compiled")):
        os.environ["GSETTINGS_SCHEMA_DIR"] = schema_dir
