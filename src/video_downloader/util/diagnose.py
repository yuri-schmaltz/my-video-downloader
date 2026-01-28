#!/usr/bin/env python3
import sys
import os
import platform
import subprocess
from gi.repository import Gio, GLib

def get_dependency_version(name):
    try:
        if name == "yt-dlp":
            return subprocess.check_output(["yt-dlp", "--version"], text=True).strip()
        elif name == "python":
            return sys.version.split()[0]
        elif name == "gi":
            import gi
            return gi.__version__
        return "Unknown"
    except Exception as e:
        return f"Error: {e}"

def register_resources():
    resource_path = os.path.join("builddir", "src", "video-downloader.gresource")
    if os.path.exists(resource_path):
        try:
            resource = Gio.Resource.load(resource_path)
            resource._register()
            print(f"Registered GResource from: {resource_path}")
        except Exception as e:
            print(f"Failed to register GResource: {e}")
    else:
        print("GResource not found (run build first)")

def get_gsettings():
    schema_id = "com.github.unrud.VideoDownloader"
    
    # Try to find compiled schemas in data/
    data_schema_dir = os.path.abspath("data")
    if os.path.exists(os.path.join(data_schema_dir, "gschemas.compiled")):
        os.environ["GSETTINGS_SCHEMA_DIR"] = data_schema_dir
    
    try:
        settings = Gio.Settings.new(schema_id)
        keys = settings.list_keys()
        return {key: str(settings.get_value(key)) for key in keys}
    except Exception as e:
        return f"GSettings '{schema_id}' not available: {e}"

def main():
    print("=== Video Downloader Diagnostic ===")
    register_resources()
    
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {get_dependency_version('python')}")
    print(f"PyGObject (gi): {get_dependency_version('gi')}")
    print(f"yt-dlp: {get_dependency_version('yt-dlp')}")
    
    print("\n--- GSettings ---")
    settings = get_gsettings()
    if isinstance(settings, dict):
        for k, v in settings.items():
            print(f"{k}: {v}")
    else:
        print(settings)
    
    print("\n--- Environment ---")
    for var in ["PYTHONPATH", "G_MESSAGES_DEBUG", "XDG_DATA_DIRS", "GSETTINGS_SCHEMA_DIR"]:
        print(f"{var}: {os.environ.get(var, 'Unset')}")

    print("\n=== End of Diagnostic ===")

if __name__ == "__main__":
    main()
