import json
import io
import pytest
from video_downloader.util.rpc import RpcClient, handle_rpc_request, rpc_response

class MockInterface:
    def hello(self, name):
        return f"Hello, {name}"
    
    def add(self, a, b):
        return a + b

def test_rpc_response_format():
    res = rpc_response("test")
    assert json.loads(res) == {"result": "test"}

def test_handle_rpc_request_success():
    impl = MockInterface()
    req = json.dumps({"method": "hello", "args": ["World"]})
    result = handle_rpc_request(MockInterface, impl, req)
    assert result == "Hello, World"

def test_handle_rpc_request_invalid_method():
    impl = MockInterface()
    req = json.dumps({"method": "unknown", "args": []})
    with pytest.raises(ValueError, match="unknown method"):
        handle_rpc_request(MockInterface, impl, req)

def test_handle_rpc_request_private_method():
    impl = MockInterface()
    req = json.dumps({"method": "_private", "args": []})
    with pytest.raises(ValueError, match="invalid method name"):
        handle_rpc_request(MockInterface, impl, req)

def test_rpc_client_output():
    output = io.StringIO()
    client = RpcClient(output)
    client.test_method("arg1", 2)
    
    output.seek(0)
    sent_request = json.loads(output.read())
    assert sent_request["method"] == "test_method"
    assert sent_request["args"] == ["arg1", 2]
