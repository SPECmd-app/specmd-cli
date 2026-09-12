"""A hand-rolled MCP (Model Context Protocol) stdio server (MCP-001..005,
SPECMD_AGENT_INTEGRATIONS.md section 4.5).

The official `mcp` Python SDK requires Python >=3.10; this build targets
3.9, so this implements the stdio JSON-RPC 2.0 wire protocol directly in
pure stdlib rather than depending on a newer interpreter or an unavailable
package. MCP-001 permits "an MCP server or equivalent structured tool
interface" — this is a real implementation of the protocol, not a stand-in.

Two layers, deliberately:
- `handle_message` is pure (dict in, dict-or-None out) so it is unit
  testable without a subprocess or real stdio.
- `run_stdio` is the thin, untested-in-isolation I/O shell that reads
  newline-delimited JSON from stdin and writes responses to stdout.

Every tool wraps an *existing* command module and returns the exact same
envelope dict the CLI's `--output-format json` mode returns (MCP-003: same
semantics as the CLI/JSON equivalents), JSON-serialized into the MCP
response's `content[0].text`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from specmd import __version__ as TOOL_VERSION
from specmd import module_resolver, structural, trace_pair
from specmd.commands import blackbox as cmd_blackbox
from specmd.commands import capabilities as cmd_capabilities
from specmd.commands import init as cmd_init
from specmd.commands import inspect as cmd_inspect
from specmd.commands import trace as cmd_trace
from specmd.commands import validate as cmd_validate
from specmd.ids import extract_acceptance_entries, extract_requirement_ids

PROTOCOL_VERSION = "2025-03-26"
SERVER_NAME = "specmd"

# JSON-RPC 2.0 error codes.
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


def _resolved_path(args: dict, key: str = "root_spec") -> Path:
    value = args.get(key) or "SPEC.md"
    return Path(value).resolve()


def _text_result(envelope: dict, *, is_error: bool = False) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(envelope, indent=2)}], "isError": is_error}


def _tool_create(args: dict) -> dict:
    output_path = Path(args.get("output", "SPEC.md")).resolve()
    profile = args.get("profile", "core")
    try:
        envelope, _exit = cmd_init.run(
            output_path=output_path,
            profile=profile,
            features=args.get("features", []),
            input_json=args.get("input_json"),
            force=bool(args.get("force", False)),
        )
    except cmd_init.InitUsageError as exc:
        return _text_result({"error": str(exc)}, is_error=True)
    return _text_result(envelope, is_error=envelope["status"] in ("failed",))


def _root_and_set(args: dict) -> tuple[Path, Path, str]:
    root = _resolved_path(args)
    return root, root.parent, str(root)


def _tool_validate(args: dict) -> dict:
    root, set_root, disp = _root_and_set(args)
    if not root.exists():
        return _text_result({"error": f"'{root}' does not exist"}, is_error=True)
    envelope, _exit = cmd_validate.run(
        root_spec_path=root,
        set_root=set_root,
        display_path=disp,
        profile=args.get("profile", "auto"),
        trace_mode=args.get("trace", "auto"),
        cognitive_mode=args.get("cognitive", "off"),
        strict=bool(args.get("strict", False)),
    )
    return _text_result(envelope, is_error=envelope["status"] in ("failed", "indeterminate"))


def _tool_inspect(args: dict) -> dict:
    root, set_root, disp = _root_and_set(args)
    if not root.exists():
        return _text_result({"error": f"'{root}' does not exist"}, is_error=True)
    envelope, _exit = cmd_inspect.run(
        root_spec_path=root,
        set_root=set_root,
        display_path=disp,
        profile=args.get("profile", "auto"),
        trace_mode=args.get("trace", "auto"),
        cognitive_mode=args.get("cognitive", "auto"),
    )
    return _text_result(envelope, is_error=envelope["status"] in ("failed", "indeterminate"))


def _tool_blackbox(args: dict) -> dict:
    root, set_root, disp = _root_and_set(args)
    if not root.exists():
        return _text_result({"error": f"'{root}' does not exist"}, is_error=True)
    export = args.get("export")
    envelope, _exit = cmd_blackbox.run(
        root_spec_path=root,
        set_root=set_root,
        display_path=disp,
        trace_mode=args.get("trace", "auto"),
        export_path=Path(export).resolve() if export else None,
    )
    return _text_result(envelope, is_error=envelope["status"] in ("failed", "indeterminate"))


def _tool_trace_create(args: dict) -> dict:
    root, set_root, disp = _root_and_set(args)
    if not root.exists():
        return _text_result({"error": f"'{root}' does not exist"}, is_error=True)
    output = args.get("output")
    envelope, _exit = cmd_trace.create(
        root_spec_path=root,
        set_root=set_root,
        display_path=disp,
        output_path=Path(output).resolve() if output else None,
        enable_optional=bool(args.get("enable_optional", False)),
        force=bool(args.get("force", False)),
    )
    return _text_result(envelope, is_error=envelope["status"] in ("failed",))


def _tool_trace_update(args: dict) -> dict:
    root, set_root, disp = _root_and_set(args)
    if not root.exists():
        return _text_result({"error": f"'{root}' does not exist"}, is_error=True)
    trace_path = args.get("trace")
    envelope, _exit = cmd_trace.update(
        root_spec_path=root,
        set_root=set_root,
        display_path=disp,
        trace_path=Path(trace_path).resolve() if trace_path else None,
        force=bool(args.get("force", False)),
    )
    return _text_result(envelope, is_error=envelope["status"] in ("failed",))


def _tool_validate_pair(args: dict) -> dict:
    """A narrower operation than `validate`: pair alignment only (MCP-002
    lists validate_pair separately from validate for exactly this reason).
    """
    root, set_root, disp = _root_and_set(args)
    if not root.exists():
        return _text_result({"error": f"'{root}' does not exist"}, is_error=True)

    report = structural.analyze(root, "auto")
    module_res = module_resolver.resolve_modules(root, set_root)
    texts = [root.read_text(encoding="utf-8")]
    for m in module_res.modules:
        try:
            texts.append(m.read_text(encoding="utf-8"))
        except OSError:
            pass
    requirement_ids: list[str] = []
    acceptance_ids: list[str] = []
    for t in texts:
        for rid in extract_requirement_ids(t):
            if rid not in requirement_ids:
                requirement_ids.append(rid)
        acceptance_ids += [e.id for e in extract_acceptance_entries(t)]

    pair = trace_pair.validate_pair(
        trace_mode=args.get("trace", "auto"),
        root_spec_path=root,
        root_spec_text=report.doc.text,
        root_spec_frontmatter=report.doc.frontmatter or {},
        requirement_ids=requirement_ids,
        acceptance_ids=acceptance_ids,
    )
    results = {
        "root_spec": disp,
        "trace_result": pair.trace_result,
        "pair_result": pair.pair_result,
        "missing_requirement_ids": pair.missing_requirement_ids,
        "missing_acceptance_ids": pair.missing_acceptance_ids,
        "unknown_ids": pair.unknown_ids,
    }
    is_error = pair.pair_result not in (None, trace_pair.RESULT_ALIGNED)
    return _text_result(results, is_error=is_error)


def _tool_propose_patch(args: dict) -> dict:
    # AGENT-002/MCP-004: a coding agent may request a Proposed Patch without
    # write authorization. This build has no patch-generation capability at
    # all — say so honestly rather than fabricate a diff.
    return _text_result(
        {
            "error": "propose_patch is not implemented in this build: no patch-generation capability exists yet.",
            "see": "capabilities tool for what is actually implemented",
        },
        is_error=True,
    )


def _tool_capabilities(_args: dict) -> dict:
    envelope, _exit = cmd_capabilities.run()
    return _text_result(envelope, is_error=False)


TOOLS: dict[str, dict[str, Any]] = {
    "create": {
        "description": "Create the smallest useful starting SPEC.md (core or core+optional profile).",
        "read_only": False,
        "handler": _tool_create,
        "input_schema": {
            "type": "object",
            "properties": {
                "output": {"type": "string", "default": "SPEC.md"},
                "profile": {"type": "string", "enum": ["core", "optional"], "default": "core"},
                "features": {"type": "array", "items": {"type": "string"}},
                "force": {"type": "boolean", "default": False},
            },
        },
    },
    "validate": {
        "description": "Structural conformance check plus Trace Pair validation.",
        "read_only": True,
        "handler": _tool_validate,
        "input_schema": {
            "type": "object",
            "properties": {
                "root_spec": {"type": "string", "default": "SPEC.md"},
                "profile": {"type": "string", "enum": ["auto", "core", "optional"], "default": "auto"},
                "trace": {"type": "string", "default": "auto"},
                "cognitive": {"type": "string", "enum": ["off", "auto", "required"], "default": "off"},
                "strict": {"type": "boolean", "default": False},
            },
        },
    },
    "inspect": {
        "description": "Read-only quality/measurement report.",
        "read_only": True,
        "handler": _tool_inspect,
        "input_schema": {
            "type": "object",
            "properties": {
                "root_spec": {"type": "string", "default": "SPEC.md"},
                "profile": {"type": "string", "enum": ["auto", "core", "optional"], "default": "auto"},
                "trace": {"type": "string", "default": "auto"},
                "cognitive": {"type": "string", "enum": ["off", "auto", "required"], "default": "auto"},
            },
        },
    },
    "blackbox": {
        "description": "Deterministic, outside-in Black-Box Contract inventory. May write a report if 'export' is given.",
        "read_only": False,
        "handler": _tool_blackbox,
        "input_schema": {
            "type": "object",
            "properties": {
                "root_spec": {"type": "string", "default": "SPEC.md"},
                "trace": {"type": "string", "default": "auto"},
                "export": {"type": "string", "description": "optional path to write a JSON report to"},
            },
        },
    },
    "trace_create": {
        "description": "Generate TRACE.md from the resolved Specification Set.",
        "read_only": False,
        "handler": _tool_trace_create,
        "input_schema": {
            "type": "object",
            "properties": {
                "root_spec": {"type": "string", "default": "SPEC.md"},
                "output": {"type": "string"},
                "enable_optional": {"type": "boolean", "default": False},
                "force": {"type": "boolean", "default": False},
            },
        },
    },
    "trace_update": {
        "description": "Reconcile an existing TRACE.md with the current Specification Set.",
        "read_only": False,
        "handler": _tool_trace_update,
        "input_schema": {
            "type": "object",
            "properties": {
                "root_spec": {"type": "string", "default": "SPEC.md"},
                "trace": {"type": "string"},
                "force": {"type": "boolean", "default": False},
            },
        },
    },
    "validate_pair": {
        "description": "Trace Pair alignment only (narrower than 'validate' — no structural findings).",
        "read_only": True,
        "handler": _tool_validate_pair,
        "input_schema": {
            "type": "object",
            "properties": {"root_spec": {"type": "string", "default": "SPEC.md"}, "trace": {"type": "string", "default": "auto"}},
        },
    },
    "propose_patch": {
        "description": "Request a Proposed Patch. Not implemented in this build (always returns an error).",
        "read_only": True,
        "handler": _tool_propose_patch,
        "input_schema": {"type": "object", "properties": {}},
    },
    "capabilities": {
        "description": "Report tool version, supported standards, commands, and available integrations.",
        "read_only": True,
        "handler": _tool_capabilities,
        "input_schema": {"type": "object", "properties": {}},
    },
}


def _tools_list_result() -> dict:
    return {
        "tools": [
            {
                "name": name,
                "description": spec["description"],
                "inputSchema": spec["input_schema"],
                "annotations": {"readOnlyHint": spec["read_only"]},
            }
            for name, spec in TOOLS.items()
        ]
    }


def _rpc_result(msg_id, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _rpc_error(msg_id, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def handle_message(msg: dict) -> dict | None:
    """Pure JSON-RPC 2.0 dispatch. Returns None for notifications (no
    response owed) or when msg has no 'id' and isn't a recognized request.
    """
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
        return _rpc_error(msg.get("id") if isinstance(msg, dict) else None, INVALID_REQUEST, "invalid JSON-RPC 2.0 message")

    method = msg.get("method")
    msg_id = msg.get("id")
    is_notification = "id" not in msg

    if method == "initialize":
        result = {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": TOOL_VERSION},
        }
        return None if is_notification else _rpc_result(msg_id, result)

    if method == "notifications/initialized":
        return None

    if method == "ping":
        return None if is_notification else _rpc_result(msg_id, {})

    if method == "tools/list":
        return None if is_notification else _rpc_result(msg_id, _tools_list_result())

    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        tool = TOOLS.get(name)
        if tool is None:
            if is_notification:
                return None
            return _rpc_error(msg_id, INVALID_PARAMS, f"unknown tool '{name}'")
        try:
            result = tool["handler"](args)
        except Exception as exc:  # noqa: BLE001 — must not crash the server on a bad call
            result = _text_result({"error": f"internal error: {exc}"}, is_error=True)
        return None if is_notification else _rpc_result(msg_id, result)

    if is_notification:
        return None
    return _rpc_error(msg_id, METHOD_NOT_FOUND, f"unknown method '{method}'")


def run_stdio() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            response = _rpc_error(None, PARSE_ERROR, "invalid JSON")
        else:
            response = handle_message(msg)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


def main() -> None:
    run_stdio()


if __name__ == "__main__":
    main()
