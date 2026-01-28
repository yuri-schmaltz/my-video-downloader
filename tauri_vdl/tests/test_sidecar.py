import json
import subprocess
import os
import pytest
import time

def run_sidecar_command(method, params):
    sidecar_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src_python", "sidecar.py"))
    original_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
    
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{original_src}:{env.get('PYTHONPATH', '')}"
    
    process = subprocess.Popen(
        [sys.executable, sidecar_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    request = json.dumps({"method": method, "params": params}) + "\n"
    stdout, stderr = process.communicate(input=request, timeout=10)
    
    return [json.loads(line) for line in stdout.splitlines() if line.strip()]

import sys

def test_sidecar_ping():
    results = run_sidecar_command("ping", {})
    assert any(res.get("pong") is True for res in results)

def test_sidecar_invalid_command():
    results = run_sidecar_command("invalid_cmd", {})
    # Should probably not return anything or return an error depending on implementation
    # Current implementation ignores unknown methods but the loop might catch something if it crashes
    assert len(results) == 0 or "error" in results[0]

def test_sidecar_handler_emit():
    from tauri_vdl.src_python.sidecar import TauriHandler
    handler = TauriHandler()
    # Check if emit prints valid JSON to stdout (mocking behavior)
    import io
    from contextlib import redirect_stdout
    f = io.StringIO()
    with redirect_stdout(f):
        handler.emit("test_event", {"foo": "bar"})
    
    output = json.loads(f.getvalue().strip())
    assert output["event"] == "test_event"
    assert output["data"] == {"foo": "bar"}
