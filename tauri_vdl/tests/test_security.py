import json
import io
from contextlib import redirect_stdout
import pytest
import os
import sys

# Mocking for standalone test
original_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, original_src)

from tauri_vdl.src_python.sidecar import TauriHandler

def test_handler_error_masking():
    handler = TauriHandler()
    f = io.StringIO()
    with redirect_stdout(f):
        handler.on_error("Failed with password: secret_key_123")
    
    output = json.loads(f.getvalue().strip())
    # Note: Currently TauriHandler.on_error just emits the message.
    # The masking should happen in StructuredLogger, but let's see if 
    # we should add it to the handler too for extra safety.
    # Based on our ONDA 3 effort, let's verify if the message is masked.
    assert "secret_key_123" not in output["data"]["message"]
    assert "***" in output["data"]["message"]

def test_progress_event_integrity():
    handler = TauriHandler()
    f = io.StringIO()
    with redirect_stdout(f):
        handler.on_progress("video.mp4", 0.5, 500, 1000, 10, 50)
    
    output = json.loads(f.getvalue().strip())
    assert output["event"] == "progress"
    assert output["data"]["progress"] == 0.5
    assert output["data"]["filename"] == "video.mp4"
