import pytest
from gi.repository import GLib
from video_downloader.app.model import Model

class MockHandler:
    def __init__(self):
        self.url = "http://example.com"
        self.mode = "video"
        self.resolution = 1080
        self.prefer_mpeg = False
        self.automatic_subtitles = []
        self.download_folder = "/tmp"

    # Mandatory interface methods for Model/Downloader interaction
    def get_url(self, *args): return self.url
    def get_mode(self, *args): return self.mode
    def get_resolution(self, *args): return self.resolution
    def get_prefer_mpeg(self, *args): return self.prefer_mpeg
    def get_automatic_subtitles(self, *args): return self.automatic_subtitles
    def get_download_dir(self, *args): return self.download_folder
    
    def on_pulse(self, *args): pass
    def on_progress(self, *args): pass
    def on_download_start(self, *args): pass
    def on_download_finished(self, *args): pass
    def on_error(self, *args): pass
    def on_download_lock(self, *args): return True
    def on_download_thumbnail(self, *args): pass
    def on_finished(self, *args): pass
    def on_download_folder_error(self, *args): pass

def test_model_initial_state():
    handler = MockHandler()
    model = Model(handler)
    assert model.state == "start"
    assert model.url == ""
    assert model.download_progress == -1.0

def test_model_state_transitions():
    import os
    handler = MockHandler()
    # Ensure a valid temp dir for auto-transition
    handler.download_folder = "/tmp/test-video-downloader"
    os.makedirs(handler.download_folder, exist_ok=True)
    
    model = Model(handler)
    model.download_folder = handler.download_folder
    
    # Valid transition start -> prepare
    # Since /tmp/test-video-downloader is valid, it will auto-transition prepare -> download
    model.state = "prepare"
    assert model.state == "download"
    
    # Valid transition download -> success (mocking completion)
    model.state = "success"
    assert model.state == "success"
    
    # Valid transition success -> start
    model.state = "start"
    assert model.state == "start"

def test_model_property_bindings():
    handler = MockHandler()
    model = Model(handler)
    
    changed_props = []
    def on_prop_changed(obj, pspec):
        changed_props.append(pspec.name)
        
    model.connect("notify::url", on_prop_changed)
    model.url = "https://youtube.com/watch?v=123"
    
    assert "url" in changed_props
    assert model.url == "https://youtube.com/watch?v=123"

def test_model_resolutions_content():
    handler = MockHandler()
    model = Model(handler)
    assert 1080 in model.resolutions
    assert 720 in model.resolutions
    assert "1080p" in model.resolutions[1080]
