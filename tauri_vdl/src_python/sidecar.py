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
        print(f"[PYTHON] ⚡ TauriHandler initialized | download_dir: {self.download_dir}", file=sys.stderr, flush=True)

    def emit(self, event, data):
        print(f"[PYTHON] 📤 Emitting event: {event} | data: {data}", file=sys.stderr, flush=True)
        print(json.dumps({"event": event, "data": data}), flush=True)

    def get_url(self): return self.url
    def get_mode(self): return self.mode
    def get_resolution(self): return self.resolution
    def get_prefer_mpeg(self): return self.prefer_mpeg
    def get_automatic_subtitles(self): return self.automatic_subtitles
    def get_download_dir(self): return self.download_dir

    def on_pulse(self):
        print("[PYTHON] 💓 Pulse (keep-alive)", file=sys.stderr, flush=True)
        self.emit("pulse", {})
    
    def on_progress(self, filename, progress, bytes_, bytes_total, eta, speed):
        pct = progress * 100 if progress else 0
        print(f"[PYTHON] 📊 Progress: {pct:.1f}% | {bytes_}/{bytes_total} bytes | Speed: {speed} B/s | ETA: {eta}s", file=sys.stderr, flush=True)
        self.emit("progress", {
            "filename": filename,
            "progress": progress,
            "bytes": bytes_,
            "bytes_total": bytes_total,
            "eta": eta,
            "speed": speed
        })

    def on_download_start(self, index, count, title):
        print(f"[PYTHON] 🎬 Download starting: '{title}' ({index}/{count})", file=sys.stderr, flush=True)
        self.emit("download_start", {"index": index, "count": count, "title": title})

    def on_download_finished(self, filename):
        print(f"[PYTHON] ✅ Download finished: {filename}", file=sys.stderr, flush=True)
        self.emit("download_finished", {"filename": filename})

    def on_download_lock(self, name):
        print(f"[PYTHON] 🔒 Download lock acquired: {name}", file=sys.stderr, flush=True)
        return True
    
    def on_download_thumbnail(self, path):
        print(f"[PYTHON] 🖼️ Thumbnail: {path}", file=sys.stderr, flush=True)
        self.emit("thumbnail", {"path": path})
    
    def on_finished(self, success):
        print(f"[PYTHON] 🏁 Finished! Success: {success}", file=sys.stderr, flush=True)
        self.emit("finished", {"success": success})
    
    def on_error(self, msg):
        from video_downloader.util.logging import StructuredLogger
        msg = StructuredLogger._mask_sensitive(msg)
        print(f"[PYTHON] ❌ ERROR: {msg}", file=sys.stderr, flush=True)
        self.emit("error", {"message": msg})

def main():
    print("[PYTHON] 🚀 Sidecar starting...", file=sys.stderr, flush=True)
    handler = TauriHandler()
    
    print("[PYTHON] 👂 Listening for commands on stdin...", file=sys.stderr, flush=True)
    # Listen for commands from Tauri (stdin)
    for line in sys.stdin:
        print(f"[PYTHON] 📥 Received command: {line.strip()}", file=sys.stderr, flush=True)
        try:
            req = json.loads(line)
            method = req.get("method")
            params = req.get("params", {})
            print(f"[PYTHON] 📋 Method: {method} | Params: {params}", file=sys.stderr, flush=True)
            
            if method == "start_download":
                handler.url = params.get("url")
                handler.mode = params.get("mode", "video")
                handler.resolution = params.get("resolution", 1080)
                handler.download_dir = params.get("download_dir", handler.download_dir)
                
                print(f"[PYTHON] 🔧 Download config:", file=sys.stderr, flush=True)
                print(f"[PYTHON]    URL: {handler.url}", file=sys.stderr, flush=True)
                print(f"[PYTHON]    Mode: {handler.mode}", file=sys.stderr, flush=True)
                print(f"[PYTHON]    Resolution: {handler.resolution}p", file=sys.stderr, flush=True)
                print(f"[PYTHON]    Output dir: {handler.download_dir}", file=sys.stderr, flush=True)
                
                # Run the slave
                print("[PYTHON] 🎬 Starting YoutubeDLSlave...", file=sys.stderr, flush=True)
                try:
                    YoutubeDLSlave(handler)
                    print("[PYTHON] ✅ YoutubeDLSlave completed", file=sys.stderr, flush=True)
                except Exception as e:
                    print(f"[PYTHON] ❌ YoutubeDLSlave error: {e}", file=sys.stderr, flush=True)
                    print(f"[PYTHON] 📜 Traceback: {traceback.format_exc()}", file=sys.stderr, flush=True)
                    handler.on_error(str(e))
            elif method == "ping":
                print("[PYTHON] 🏓 Ping received, sending pong", file=sys.stderr, flush=True)
                print(json.dumps({"pong": True}), flush=True)
            else:
                print(f"[PYTHON] ❓ Unknown method: {method}", file=sys.stderr, flush=True)
                
        except json.JSONDecodeError as e:
            print(f"[PYTHON] ❌ JSON parse error: {e}", file=sys.stderr, flush=True)
            print(json.dumps({"error": f"Invalid JSON: {e}"}), flush=True)
        except Exception:
            print(f"[PYTHON] ❌ Unexpected error: {traceback.format_exc()}", file=sys.stderr, flush=True)
            print(json.dumps({"error": traceback.format_exc()}), flush=True)
    
    print("[PYTHON] 🔚 Stdin closed, sidecar exiting", file=sys.stderr, flush=True)

if __name__ == "__main__":
    print("[PYTHON] ⚡ __main__ entry point", file=sys.stderr, flush=True)
    main()
