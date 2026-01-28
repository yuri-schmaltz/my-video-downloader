import { useState, useRef, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { Download, Link as LinkIcon, AlertCircle, CheckCircle2, Loader2, Gauge, HardDrive, Video, Music, Settings2 } from "lucide-react";
import "./App.css";

interface ProgressData {
  filename: string;
  progress: number;
  bytes: number;
  bytes_total: number;
  eta: number;
  speed: number;
}

function App() {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState<"idle" | "downloading" | "finished" | "error">("idle");
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [mode, setMode] = useState<"video" | "audio">("video");
  const [resolution, setResolution] = useState(1080);
  const unlistenRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    console.log("[REACT] ⚡ App mounted, setting up sidecar event listener...");
    const setupListener = async () => {
      unlistenRef.current = await listen<any>("sidecar-event", (event) => {
        const msg = event.payload;
        console.log("[REACT] 📩 Sidecar event received:", JSON.stringify(msg, null, 2));
        if (msg.event === "progress") {
          console.log(`[REACT] 📊 Progress: ${(msg.data.progress * 100).toFixed(1)}% | Speed: ${msg.data.speed} B/s`);
          setProgress(msg.data);
        } else if (msg.event === "finished") {
          console.log(`[REACT] ✅ Finished! Success: ${msg.data.success}`);
          setStatus(msg.data.success ? "finished" : "error");
        } else if (msg.event === "error") {
          console.error("[REACT] ❌ Error from sidecar:", msg.data.message);
          setErrorMessage(msg.data.message);
          setStatus("error");
        } else if (msg.event === "download_start") {
          console.log(`[REACT] 🎬 Download started: ${msg.data.title} (${msg.data.index}/${msg.data.count})`);
        } else if (msg.event === "download_finished") {
          console.log(`[REACT] 📁 File saved: ${msg.data.filename}`);
        } else if (msg.event === "pulse") {
          console.log("[REACT] 💓 Pulse received (alive signal)");
        } else {
          console.log("[REACT] ❓ Unknown event type:", msg.event);
        }
      });
      console.log("[REACT] ✅ Sidecar listener registered successfully");
    };
    setupListener();

    return () => {
      if (unlistenRef.current) unlistenRef.current();
    };
  }, []);

  const startDownload = async () => {
    if (!url) {
      console.warn("[REACT] ⚠️ startDownload called but URL is empty");
      return;
    }

    console.log("[REACT] 🚀 Starting download...");
    console.log("[REACT] 🔗 URL:", url);
    console.log("[REACT] 📦 Mode:", mode, "| Resolution:", resolution);
    setStatus("downloading");
    console.log("[REACT] 📍 Status changed: idle → downloading");
    setErrorMessage("");
    setProgress(null);

    try {
      console.log("[REACT] 📡 Invoking Rust 'start_download' command...");
      await invoke("start_download", { url, mode, resolution });
      console.log("[REACT] ✅ Rust command invoked successfully (sidecar spawned)");
    } catch (e: any) {
      console.error("[REACT] ❌ Failed to invoke Rust command:", e);
      setErrorMessage(e.toString() || "Failed to start download");
      setStatus("error");
      console.log("[REACT] 📍 Status changed: downloading → error");
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === -1 || bytes === undefined) return "—";
    const units = ["B", "KB", "MB", "GB"];
    let i = 0;
    while (bytes >= 1024 && i < units.length - 1) {
      bytes /= 1024;
      i++;
    }
    return `${bytes.toFixed(1)} ${units[i]}`;
  };

  const resetState = () => {
    console.log("[REACT] 🔄 Resetting state to idle");
    setStatus("idle");
    setProgress(null);
    setErrorMessage("");
  };

  return (
    <main>
      <div className="glass-card">
        <header>
          <h1 className="gradient-text">Video Downloader</h1>
          <p>AEGIS EVO • Tauri Rebirth</p>
        </header>

        <div className="input-group">
          <div className="input-wrapper">
            <LinkIcon size={18} />
            <input
              className="input-box"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Paste your video URL here..."
              disabled={status === "downloading"}
              onKeyDown={(e) => e.key === "Enter" && startDownload()}
            />
          </div>

          <button
            className="download-btn"
            onClick={status === "error" || status === "finished" ? resetState : startDownload}
            disabled={status === "downloading" || (!url && status === "idle")}
          >
            {status === "downloading" ? (
              <Loader2 size={20} className="animate-spin" />
            ) : status === "error" || status === "finished" ? (
              <Download size={20} />
            ) : (
              <Download size={20} />
            )}
            {status === "downloading" ? "Downloading..." :
              status === "error" || status === "finished" ? "Try Again" : "Start Download"}
          </button>
        </div>

        {/* Format Options */}
        <div className="options-section">
          <div className="options-header">
            <Settings2 size={16} />
            <span>Format Options</span>
          </div>

          <div className="options-grid">
            <div className="option-group">
              <label className="option-label">Type</label>
              <div className="toggle-group">
                <button
                  className={`toggle-btn ${mode === "video" ? "active" : ""}`}
                  onClick={() => setMode("video")}
                  disabled={status === "downloading"}
                >
                  <Video size={16} />
                  Video
                </button>
                <button
                  className={`toggle-btn ${mode === "audio" ? "active" : ""}`}
                  onClick={() => setMode("audio")}
                  disabled={status === "downloading"}
                >
                  <Music size={16} />
                  Audio
                </button>
              </div>
            </div>

            <div className={`option-group ${mode === "audio" ? "disabled" : ""}`}>
              <label className="option-label">Resolution</label>
              <select
                className="select-box"
                value={resolution}
                onChange={(e) => setResolution(Number(e.target.value))}
                disabled={status === "downloading" || mode === "audio"}
              >
                <option value={2160}>4K (2160p)</option>
                <option value={1440}>1440p</option>
                <option value={1080}>1080p (Full HD)</option>
                <option value={720}>720p (HD)</option>
                <option value={480}>480p</option>
                <option value={360}>360p</option>
              </select>
            </div>
          </div>
        </div>

        {status !== "idle" && (
          <div className="progress-container">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className={`status-badge status-${status}`}>
                {status}
              </span>
              {progress && (
                <span style={{ fontSize: "0.875rem", color: "#818cf8", fontWeight: "600" }}>
                  {(progress.progress * 100).toFixed(1)}%
                </span>
              )}
            </div>

            {progress && (
              <>
                <div className="progress-bar-bg">
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${progress.progress * 100}%` }}
                  />
                </div>

                <div className="stats-grid">
                  <div>
                    <Gauge size={14} />
                    {formatBytes(progress.speed)}/s
                  </div>
                  <div>
                    <HardDrive size={14} />
                    {formatBytes(progress.bytes)} / {formatBytes(progress.bytes_total)}
                  </div>
                </div>

                <p className="filename-text">{progress.filename}</p>
              </>
            )}

            {status === "error" && (
              <div className="error-message">
                <AlertCircle size={16} style={{ flexShrink: 0, marginTop: 2 }} />
                <span>{errorMessage || "An unexpected error occurred"}</span>
              </div>
            )}

            {status === "finished" && (
              <div className="success-message">
                <CheckCircle2 size={16} style={{ flexShrink: 0, marginTop: 2 }} />
                <span>Download completed successfully!</span>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}

export default App;
