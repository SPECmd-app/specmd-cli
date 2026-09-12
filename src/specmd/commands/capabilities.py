"""`specmd capabilities` (ICD-CLI section 8.9)."""

from __future__ import annotations

from specmd import __version__ as TOOL_VERSION
from specmd import core_profile, exit_codes
from specmd.command_metadata import COMMANDS
from specmd.commands.adapt import ADAPTER_FORMAT_VERSION, TARGETS as ADAPTER_TARGETS
from specmd.envelope import build_envelope

CLI_ICD_VERSION = "1.0.0"


def run() -> tuple[dict, int]:
    results = {
        "tool_version": TOOL_VERSION,
        "cli_icd_version": CLI_ICD_VERSION,
        "json_schema_version": "1.1.0",
        "core_versions_supported": [core_profile.CORE_VERSION],
        "optional_versions_supported": [core_profile.OPTIONAL_VERSION],
        "core_profile_provenance": core_profile.PROFILE_PROVENANCE,
        "commands": [
            {
                "name": c.name,
                "summary": c.summary,
                "read_only": c.read_only,
                "writes": c.writes,
                "network": c.network,
                "executes_code": c.executes_code,
                "available": c.available,
                "unavailable_reason": c.unavailable_reason or None,
            }
            for c in COMMANDS
        ],
        "cognitive_modes_supported": ["off", "auto", "required"],
        "cognitive_providers_configured": [],
        "adapter_targets": [{"target": t, "adapter_format_version": ADAPTER_FORMAT_VERSION} for t in ADAPTER_TARGETS],
        "structured_tool_interfaces": {"available": False, "reason": "MCP server interface not implemented in this build."},
        "implementation_test_integrations": {"available": False, "reason": "Cucumber connector not implemented in this build."},
        "reviewer_agent_targets": [],
    }

    envelope = build_envelope(
        command="capabilities",
        status="succeeded",
        inputs={},
        results=results,
        findings=[],
        writes=[],
        cognitive_requested="off",
        cognitive_used="none",
        cognitive_complete=True,
    )
    return envelope, exit_codes.SUCCESS
