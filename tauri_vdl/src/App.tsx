import { useState, useRef, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { motion, AnimatePresence } from "framer-motion";
import { Download, Link as LinkIcon, AlertCircle, CheckCircle2, Loader2, Gauge, HardDrive } from "lucide-react";
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
  const unlistenRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    const setupListener = async () => {
      unlistenRef.current = await listen<any>("sidecar-event", (event) => {
        const msg = event.payload;
        if (msg.event === "progress") {
          setProgress(msg.data);
        } else if (msg.event === "finished") {
          setStatus(msg.data.success ? "finished" : "error");
        } else if (msg.event === "error") {
          setErrorMessage(msg.data.message);
          setStatus("error");
        }
      });
    };
    setupListener();

    return () => {
      if (unlistenRef.current) unlistenRef.current();
    };
  }, []);

  const startDownload = async () => {
    if (!url) return;

    setStatus("downloading");
    setErrorMessage("");
    setProgress(null);

    try {
      await invoke("start_download", { url });
    } catch (e: any) {
      setErrorMessage(e.toString() || "Failed to start download");
      setStatus("error");
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
    setStatus("idle");
    setProgress(null);
    setErrorMessage("");
  };

  return (
    <main>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="glass-card"
      >
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

        <AnimatePresence>
          {status !== "idle" && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="progress-container"
            >
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
                    <motion.div
                      className="progress-bar-fill"
                      initial={{ width: 0 }}
                      animate={{ width: `${progress.progress * 100}%` }}
                      transition={{ duration: 0.3 }}
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
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </main>
  );
}

export default App;
