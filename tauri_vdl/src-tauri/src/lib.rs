use std::io::{BufRead, BufReader, Write};
use std::process::{Command, Stdio};
use std::sync::{Arc, Mutex};
use tauri::Emitter;

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
async fn start_download(app: tauri::AppHandle, url: String) -> Result<(), String> {
    // Use absolute path to the sidecar
    let sidecar_path = "/home/yurix/Documentos/my-video-downloader/tauri_vdl/src_python/sidecar.py";

    let mut child = Command::new("python3")
        .arg(sidecar_path)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to spawn Python: {}", e))?;

    // Take ownership of stdin and wrap it for thread-safe sharing
    let stdin = child.stdin.take().ok_or("Failed to get stdin")?;
    let stdin = Arc::new(Mutex::new(stdin));

    // Send download command to sidecar
    {
        let mut stdin_lock = stdin.lock().map_err(|e| e.to_string())?;
        let cmd = serde_json::json!({
            "method": "start_download",
            "params": { "url": url, "mode": "video", "resolution": 1080 }
        });
        writeln!(&mut *stdin_lock, "{}", cmd.to_string())
            .map_err(|e| format!("Failed to write to stdin: {}", e))?;
        stdin_lock.flush().map_err(|e| format!("Failed to flush stdin: {}", e))?;
    }

    // Read stdout in a separate thread and emit events
    let stdout = child.stdout.take().ok_or("Failed to get stdout")?;
    let app_clone = app.clone();
    
    std::thread::spawn(move || {
        let reader = BufReader::new(stdout);
        for line in reader.lines().flatten() {
            if let Ok(msg) = serde_json::from_str::<serde_json::Value>(&line) {
                let _ = app_clone.emit("sidecar-event", msg);
            }
        }
    });

    // Read stderr in a separate thread for debugging
    if let Some(stderr) = child.stderr.take() {
        std::thread::spawn(move || {
            let reader = BufReader::new(stderr);
            for line in reader.lines().flatten() {
                eprintln!("Sidecar stderr: {}", line);
            }
        });
    }

    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![greet, start_download])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
