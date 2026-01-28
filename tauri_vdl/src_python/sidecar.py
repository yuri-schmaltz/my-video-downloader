import sys
import json
import os
import traceback

# Mock gi only if not available (e.g. on Windows or headless without libs)
try:
    import gi
except ImportError:
    class Mock:
        def __init__(self, *args, **kwargs): pass
        def __getattr__(self, name): return Mock()
        def __call__(self, *args, **kwargs): return Mock()
        def __iter__(self): return iter([])
    sys.modules['gi'] = Mock()
    sys.modules['gi.repository'] = Mock()

# Add the original src directory to path to reuse yt_dlp_slave and other utilities
original_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, original_src)

from video_downloader.downloader.yt_dlp_slave import YoutubeDLSlave

class TauriHandler:
    def __init__(self):
        self.url = ""
        self.mode = "video"
        self.resolution = 1080
        self.prefer_mpeg = False
        self.automatic_subtitles = []
        self.download_dir = os.path.expanduser("~/Downloads")

    def emit(self, event, data):
        print(json.dumps({"event": event, "data": data}), flush=True)

    def get_url(self): return self.url
    def get_mode(self): return self.mode
    def get_resolution(self): return self.resolution
    def get_prefer_mpeg(self): return self.prefer_mpeg
    def get_automatic_subtitles(self): return self.automatic_subtitles
    def get_download_dir(self): return self.download_dir

    def on_pulse(self): self.emit("pulse", {})
    def on_progress(self, filename, progress, bytes_, bytes_total, eta, speed):
        self.emit("progress", {
            "filename": filename,
            "progress": progress,
            "bytes": bytes_,
            "bytes_total": bytes_total,
            "eta": eta,
            "speed": speed
        })

    def on_download_start(self, index, count, title):
        self.emit("download_start", {"index": index, "count": count, "title": title})

    def on_download_finished(self, filename):
        self.emit("download_finished", {"filename": filename})

    def on_download_lock(self, name): return True
    def on_download_thumbnail(self, path): self.emit("thumbnail", {"path": path})
    def on_finished(self, success): self.emit("finished", {"success": success})
    def on_error(self, msg):
        from video_downloader.util.logging import StructuredLogger
        msg = StructuredLogger._mask_sensitive(msg)
        self.emit("error", {"message": msg})

def main():
    handler = TauriHandler()
    
    # Listen for commands from Tauri (stdin)
    for line in sys.stdin:
        try:
            req = json.loads(line)
            method = req.get("method")
            params = req.get("params", {})
            
            if method == "start_download":
                handler.url = params.get("url")
                handler.mode = params.get("mode", "video")
                handler.resolution = params.get("resolution", 1080)
                handler.download_dir = params.get("download_dir", handler.download_dir)
                
                # Run the slave
                # Note: YoutubeDLSlave constructor runs the whole process
                try:
                    YoutubeDLSlave(handler)
                except Exception as e:
                    handler.on_error(str(e))
            elif method == "ping":
                print(json.dumps({"pong": True}), flush=True)
                
        except Exception:
            print(json.dumps({"error": traceback.format_all()}), flush=True)

if __name__ == "__main__":
    main()
