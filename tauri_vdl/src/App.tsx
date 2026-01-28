import { useState, useEffect, useRef } from "react";
import { Command } from "@tauri-apps/plugin-shell";
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
  const sidecarRef = useRef<any>(null);

  const startDownload = async () => {
    if (!url) return;
    
    setStatus("downloading");
    setErrorMessage("");
    setProgress(null);

    try {
      // Initialize the sidecar
      const command = Command.sidecar("python-sidecar");
      
      command.on("close", (data) => {
        console.log(`Sidecar closed with code ${data.code}`);
      });

      command.stderr.on("data", (line) => {
        console.error(`Sidecar error: ${line}`);
      });

      command.stdout.on("data", (line) => {
        try {
          const msg = JSON.parse(line);
          if (msg.event === "progress") {
            setProgress(msg.data);
          } else if (msg.event === "finished") {
            setStatus(msg.data.success ? "finished" : "error");
          } else if (msg.event === "error") {
            setErrorMessage(msg.data.message);
            setStatus("error");
          }
        } catch (e) {
          console.log("Raw sidecar output:", line);
        }
      });

      const child = await command.spawn();
      sidecarRef.current = child;

      // Send the download command
      await child.write(JSON.stringify({
        method: "start_download",
        params: { url, mode: "video", resolution: 1080 }
      }) + "\n");

    } catch (e: any) {
      setErrorMessage(e.message || "Failed to start sidecar");
      setStatus("error");
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === -1) return "Unknown";
    const units = ["B", "KB", "MB", "GB", "TB"];
    let i = 0;
    while (bytes >= 1024 && i < units.length - 1) {
      bytes /= 1024;
      i++;
    }
    return `${bytes.toFixed(2)} ${units[i]}`;
  };

  return (
    <main>
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card"
      >
        <header style={{ marginBottom: "2rem" }}>
          <h1 className="gradient-text">Video Downloader</h1>
          <p style={{ color: "#94a3b8" }}>AEGIS EVO • Tauri Rebirth</p>
        </header>

        <div className="input-group">
          <div style={{ position: "relative" }}>
            <LinkIcon size={18} style={{ position: "absolute", left: "12px", top: "18px", color: "#64748b" }} />
            <input
              className="input-box"
              style={{ paddingLeft: "2.5rem" }}
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Paste your video URL here..."
              disabled={status === "downloading"}
            />
          </div>
          
          <button 
            className="download-btn" 
            onClick={startDownload}
            disabled={status === "downloading" || !url}
          >
            {status === "downloading" ? (
              <Loader2 className="animate-spin" />
            ) : (
              <Download size={20} />
            )}
            {status === "downloading" ? "Downloading..." : "Start Download"}
          </button>
        </div>

        <AnimatePresence>
          {status !== "idle" && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="progress-container"
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span className={`status-badge status-${status}`}>
                  {status}
                </span>
                {progress && (
                  <span style={{ fontSize: "0.875rem", color: "#6366f1", fontWeight: "bold" }}>
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
                    />
                  </div>
                  
                  <div className="stats-grid">
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <Gauge size={14} />
                      {formatBytes(progress.speed)}/s
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <HardDrive size={14} />
                      {formatBytes(progress.bytes)} / {formatBytes(progress.bytes_total)}
                    </div>
                  </div>
                  
                  <p style={{ fontSize: "0.75rem", marginTop: "1rem", color: "#64748b", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {progress.filename}
                  </p>
                </>
              )}

              {status === "error" && (
                <div style={{ marginTop: "1rem", color: "#f87171", display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.875rem" }}>
                  <AlertCircle size={16} />
                  {errorMessage || "An unexpected error occurred"}
                </div>
              )}

              {status === "finished" && (
                <div style={{ marginTop: "1rem", color: "#4ade80", display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.875rem" }}>
                  <CheckCircle2 size={16} />
                  Download completed successfully!
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
