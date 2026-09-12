import json

from specmd.mcp_server import TOOLS, handle_message


def _call(name, arguments=None, msg_id=1):
    return handle_message(
        {"jsonrpc": "2.0", "id": msg_id, "method": "tools/call", "params": {"name": name, "arguments": arguments or {}}}
    )


def test_initialize_handshake():
    resp = handle_message({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert resp["jsonrpc"] == "2.0"
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "specmd"
    assert resp["result"]["capabilities"] == {"tools": {}}


def test_initialized_notification_gets_no_response():
    resp = handle_message({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
    assert resp is None


def test_ping():
    resp = handle_message({"jsonrpc": "2.0", "id": 2, "method": "ping"})
    assert resp["result"] == {}


def test_tools_list_contains_all_nine_tools_with_read_only_hints():
    resp = handle_message({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
    tools = {t["name"]: t for t in resp["result"]["tools"]}
    assert set(tools) == set(TOOLS)
    assert tools["validate"]["annotations"]["readOnlyHint"] is True
    assert tools["create"]["annotations"]["readOnlyHint"] is False
    assert tools["blackbox"]["annotations"]["readOnlyHint"] is False  # --export can write
    for t in tools.values():
        assert "inputSchema" in t
        assert "description" in t


def test_unknown_method_is_json_rpc_error():
    resp = handle_message({"jsonrpc": "2.0", "id": 4, "method": "not/a/real/method"})
    assert resp["error"]["code"] == -32601


def test_unknown_tool_is_invalid_params_error():
    resp = _call("not-a-real-tool")
    assert resp["error"]["code"] == -32602


def test_malformed_top_level_message_is_invalid_request():
    resp = handle_message({"id": 5, "method": "ping"})  # missing "jsonrpc"
    assert resp["error"]["code"] == -32600


def test_notification_style_tools_call_gets_no_response():
    resp = handle_message({"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "capabilities", "arguments": {}}})
    assert resp is None


def test_capabilities_tool_matches_cli_envelope_shape(tmp_fixture):
    resp = _call("capabilities")
    payload = json.loads(resp["result"]["content"][0]["text"])
    assert payload["command"] == "capabilities"
    assert payload["status"] == "succeeded"
    assert resp["result"]["isError"] is False


def test_validate_tool_against_minimal_core_fixture(tmp_fixture):
    d = tmp_fixture("minimal_core")
    resp = _call("validate", {"root_spec": str(d / "SPEC.md"), "trace": "none"})
    payload = json.loads(resp["result"]["content"][0]["text"])
    assert payload["results"]["specification_result"] == "conforming"
    assert resp["result"]["isError"] is False


def test_validate_tool_missing_file_is_error():
    resp = _call("validate", {"root_spec": "/nonexistent/SPEC.md"})
    assert resp["result"]["isError"] is True


def test_create_tool_respects_no_overwrite_without_force(tmp_path):
    out = tmp_path / "SPEC.md"
    resp1 = _call("create", {"output": str(out)})
    assert resp1["result"]["isError"] is False
    resp2 = _call("create", {"output": str(out)})
    payload2 = json.loads(resp2["result"]["content"][0]["text"])
    assert resp2["result"]["isError"] is True
    assert payload2["writes"][0]["action"] == "refused"


def test_trace_create_respects_authorization_boundary(tmp_fixture):
    d = tmp_fixture("minimal_core")
    resp = _call("trace_create", {"root_spec": str(d / "SPEC.md"), "output": str(d / "TRACE.md")})
    # No enable_optional given, and force defaults False — must not write.
    assert resp["result"]["isError"] is True
    assert not (d / "TRACE.md").exists()


def test_validate_pair_aligned_on_optional_trace_fixture(tmp_fixture):
    d = tmp_fixture("optional_trace")
    resp = _call("validate_pair", {"root_spec": str(d / "SPEC.md"), "trace": "auto"})
    payload = json.loads(resp["result"]["content"][0]["text"])
    assert payload["pair_result"] == "aligned"
    assert resp["result"]["isError"] is False


def test_propose_patch_is_honest_stub():
    resp = _call("propose_patch")
    assert resp["result"]["isError"] is True
    payload = json.loads(resp["result"]["content"][0]["text"])
    assert "not implemented" in payload["error"]


def test_handler_exception_does_not_crash_server(monkeypatch):
    def boom(_args):
        raise RuntimeError("boom")

    monkeypatch.setitem(TOOLS, "capabilities", {**TOOLS["capabilities"], "handler": boom})
    resp = _call("capabilities")
    assert resp["result"]["isError"] is True
    payload = json.loads(resp["result"]["content"][0]["text"])
    assert "internal error" in payload["error"]
