"""Host-Agent Mode cognitive input (COG-001, SPECMD_CLI_ICD.md section 7.2).

specmd never calls a Cognitive Provider itself (see cognitive.py: no
Direct-Provider Mode is configured in this build, and none of PROV-001..009's
credential/network machinery exists on this path). Host-Agent Mode instead
lets the coding agent already driving specmd supply semantic analysis back
in — via `--cognitive-input` (CLI) or the `cognitive_input` MCP tool
argument — after reading the `cognitive_package` a prior `blackbox` call
returned.

That payload is treated as untrusted input until validated (PROV-006, applied
here to a Host-Agent's response rather than a remote provider's). Malformed
shape (wrong types, a missing required field) is a usage error — the caller
did not follow the response contract. A well-formed entry that cites a
requirement ID this tool cannot verify against what it already extracted
deterministically is not a shape error: that single citation is dropped and
reported, but the rest of the entry is kept (mirrors PROV-009 — a partial
problem must not erase the results that are still good).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import json


class HostAgentInputError(Exception):
    """Malformed --cognitive-input / cognitive_input payload (usage error)."""


@dataclass
class HostAgentResult:
    interfaces: dict[str, dict] = field(default_factory=dict)
    cross_mapping: dict = field(default_factory=lambda: {"unmatched_requirements": [], "unmatched_interface_elements": []})
    rejected_citations: list[str] = field(default_factory=list)
    covered_interface_elements: set[str] = field(default_factory=set)


def load_cognitive_input(raw: str | dict, stdin_text: str | None = None) -> dict:
    """`raw` is either an already-parsed object (the MCP `cognitive_input`
    argument) or a string naming a file path, or "-" for stdin (same
    convention as `init`'s `--input-json`/`load_input_json`).
    """
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        raise HostAgentInputError(f"--cognitive-input must be a JSON object, a file path, or '-'; got {type(raw).__name__}")
    if raw == "-":
        text = stdin_text if stdin_text is not None else sys.stdin.read()
    else:
        try:
            text = Path(raw).read_text(encoding="utf-8")
        except OSError as exc:
            raise HostAgentInputError(f"could not read --cognitive-input path '{raw}': {exc}") from exc
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HostAgentInputError(f"--cognitive-input is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise HostAgentInputError("--cognitive-input JSON must be an object")
    return parsed


def _require_list_of_str(value, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise HostAgentInputError(f"'{field_name}' must be a list of strings")
    return value


def validate_and_merge(
    payload: dict,
    *,
    known_requirement_ids: list[str],
    known_interface_elements: list[str],
) -> HostAgentResult:
    if not isinstance(payload, dict):
        raise HostAgentInputError("--cognitive-input JSON must be an object")

    known_req_set = set(known_requirement_ids)
    result = HostAgentResult()

    raw_interfaces = payload.get("interfaces", [])
    if not isinstance(raw_interfaces, list):
        raise HostAgentInputError("'interfaces' must be a list")

    for entry in raw_interfaces:
        if not isinstance(entry, dict) or not isinstance(entry.get("interface"), str) or not entry["interface"]:
            raise HostAgentInputError("each 'interfaces' entry must be an object with a non-empty string 'interface'")
        name = entry["interface"]
        input_contract = _require_list_of_str(entry.get("input_contract"), "input_contract")
        output_contract = _require_list_of_str(entry.get("output_contract"), "output_contract")
        gaps = _require_list_of_str(entry.get("gaps"), "gaps")
        confidence = entry.get("confidence", "unspecified")
        if not isinstance(confidence, str):
            raise HostAgentInputError("'confidence' must be a string")

        cited = _require_list_of_str(entry.get("supporting_requirement_ids"), "supporting_requirement_ids")
        verified = [rid for rid in cited if rid in known_req_set]
        for rid in cited:
            if rid not in known_req_set:
                result.rejected_citations.append(
                    f"interface '{name}' cited unrecognized requirement ID '{rid}' (not found by deterministic extraction); citation dropped"
                )

        result.interfaces[name] = {
            "input_contract": input_contract,
            "output_contract": output_contract,
            "supporting_requirement_ids": verified,
            "gaps": gaps,
            "confidence": confidence,
        }
        result.covered_interface_elements.add(name)

    raw_cross = payload.get("requirements_interface_cross_mapping", {})
    if not isinstance(raw_cross, dict):
        raise HostAgentInputError("'requirements_interface_cross_mapping' must be an object")
    unmatched_requirements = _require_list_of_str(raw_cross.get("unmatched_requirements"), "unmatched_requirements")
    unmatched_interface_elements = _require_list_of_str(
        raw_cross.get("unmatched_interface_elements"), "unmatched_interface_elements"
    )
    verified_unmatched_requirements = [rid for rid in unmatched_requirements if rid in known_req_set]
    for rid in unmatched_requirements:
        if rid not in known_req_set:
            result.rejected_citations.append(
                f"cross-mapping cited unrecognized requirement ID '{rid}' as unmatched; citation dropped"
            )
    result.cross_mapping = {
        "unmatched_requirements": verified_unmatched_requirements,
        "unmatched_interface_elements": unmatched_interface_elements,
    }

    return result
