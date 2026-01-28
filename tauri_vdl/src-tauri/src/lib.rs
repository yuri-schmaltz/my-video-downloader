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
async fn start_download(app: tauri::AppHandle, url: String, mode: String, resolution: u32) -> Result<(), String> {
    println!("[RUST] 🚀 start_download command received");
    println!("[RUST] 🔗 URL: {}", url);
    println!("[RUST] 📦 Mode: {} | Resolution: {}p", mode, resolution);
    
    // Use absolute path to the sidecar
    let sidecar_path = "/home/yurix/Documentos/my-video-downloader/tauri_vdl/src_python/sidecar.py";
    println!("[RUST] 📁 Sidecar path: {}", sidecar_path);
    println!("[RUST] 🔄 Spawning Python sidecar process...");

    let mut child = Command::new("python3")
        .arg(sidecar_path)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| {
            eprintln!("[RUST] ❌ Failed to spawn Python: {}", e);
            format!("Failed to spawn Python: {}", e)
        })?;
    
    println!("[RUST] ✅ Python sidecar spawned successfully (PID: {:?})", child.id());

    // Take ownership of stdin and wrap it for thread-safe sharing
    let stdin = child.stdin.take().ok_or("Failed to get stdin")?;
    let stdin = Arc::new(Mutex::new(stdin));

    // Send download command to sidecar
    println!("[RUST] 📤 Sending download command to sidecar via stdin...");
    {
        let mut stdin_lock = stdin.lock().map_err(|e| e.to_string())?;
        let cmd = serde_json::json!({
            "method": "start_download",
            "params": { "url": url, "mode": mode, "resolution": resolution }
        });
        println!("[RUST] 📝 Command JSON: {}", cmd.to_string());
        writeln!(&mut *stdin_lock, "{}", cmd.to_string())
            .map_err(|e| {
                eprintln!("[RUST] ❌ Failed to write to stdin: {}", e);
                format!("Failed to write to stdin: {}", e)
            })?;
        stdin_lock.flush().map_err(|e| {
            eprintln!("[RUST] ❌ Failed to flush stdin: {}", e);
            format!("Failed to flush stdin: {}", e)
        })?;
        println!("[RUST] ✅ Command sent and flushed to sidecar");
    }

    // Read stdout in a separate thread and emit events
    let stdout = child.stdout.take().ok_or("Failed to get stdout")?;
    let app_clone = app.clone();
    
    println!("[RUST] 🧵 Starting stdout reader thread...");
    std::thread::spawn(move || {
        println!("[RUST:STDOUT] 👂 Listening for sidecar output...");
        let reader = BufReader::new(stdout);
        for line in reader.lines().flatten() {
            println!("[RUST:STDOUT] 📥 Raw line received: {}", line);
            if let Ok(msg) = serde_json::from_str::<serde_json::Value>(&line) {
                println!("[RUST:STDOUT] 📡 Emitting 'sidecar-event' to frontend: {:?}", msg.get("event").unwrap_or(&serde_json::Value::Null));
                let _ = app_clone.emit("sidecar-event", msg);
            } else {
                eprintln!("[RUST:STDOUT] ⚠️ Failed to parse JSON: {}", line);
            }
        }
        println!("[RUST:STDOUT] 🔚 Sidecar stdout stream ended");
    });

    // Read stderr in a separate thread for debugging
    if let Some(stderr) = child.stderr.take() {
        println!("[RUST] 🧵 Starting stderr reader thread...");
        std::thread::spawn(move || {
            println!("[RUST:STDERR] 👂 Listening for sidecar errors...");
            let reader = BufReader::new(stderr);
            for line in reader.lines().flatten() {
                eprintln!("[RUST:STDERR] ⚠️ {}", line);
            }
            println!("[RUST:STDERR] 🔚 Sidecar stderr stream ended");
        });
    }

    println!("[RUST] ✅ Download process initialized successfully");
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
