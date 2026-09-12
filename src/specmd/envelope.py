"""JSON Result Envelope 1.1.0 (SPECMD_CLI_ICD.md section 9)."""

from __future__ import annotations

from specmd import __version__ as TOOL_VERSION
from specmd.findings import Finding, sorted_findings

SCHEMA_VERSION = "1.1.0"


def build_envelope(
    *,
    command: str,
    status: str,
    inputs: dict,
    results: dict,
    findings: list[Finding],
    writes: list[dict],
    cognitive_requested: str,
    cognitive_used: str,
    cognitive_complete: bool,
    reviewer_policy: str = "best-effort",
    reviewers_requested: list[str] | None = None,
    reviewers_completed: list[str] | None = None,
    reviewers_failed: list[str] | None = None,
) -> dict:
    # ICD-JSON-001: all properties below must be present; empty arrays/objects
    # when the corresponding data is absent.
    return {
        "schema_version": SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "command": command,
        "status": status,
        "inputs": inputs,
        "results": results,
        "findings": [f.to_dict() for f in sorted_findings(findings)],
        "writes": writes,
        "cognitive": {
            "requested": cognitive_requested,
            "used": cognitive_used,
            "complete": cognitive_complete,
            "reviewers": {
                "policy": reviewer_policy,
                "requested": reviewers_requested or [],
                "completed": reviewers_completed or [],
                "failed": reviewers_failed or [],
            },
        },
    }
