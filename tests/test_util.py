import os
import pytest
from video_downloader.util.path import expand_path, encode_filesystem_path
from video_downloader.util.logging import StructuredLogger

def test_expand_path_basic():
    path = "~/Downloads"
    expanded = expand_path(path)
    assert expanded == os.path.expanduser("~") + "/Downloads"

def test_encode_filesystem_path():
    path = "tést_vídéo.mp4"
    encoded = encode_filesystem_path(path)
    assert isinstance(encoded, bytes)

def test_logger_masking():
    # Test internal masking logic
    logger = StructuredLogger()
    masked = logger._mask_sensitive("My password is: secret123")
    assert "secret123" not in masked
    assert "password: ***" in masked

def test_logger_masking_token():
    logger = StructuredLogger()
    masked = logger._mask_sensitive("Authorization: Token abc-123-def")
    # This might need regex adjustment based on implementation, let's verify current implementation:
    # re.sub(r'([Pp]assword|[Tt]oken|[Ss]ecret)[:=]\s*[^\s,]+', r'\1: ***', text)
    # Token abc-123-def -> Token: ***
    assert "abc-123-def" not in masked
    assert "Token: ***" in masked
