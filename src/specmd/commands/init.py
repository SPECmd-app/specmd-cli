"""`specmd init` (INIT-001..015, Creation Profile Contract SPEC.md section 5.3)."""

from __future__ import annotations

import datetime
import json
from pathlib import Path

import yaml

from specmd import core_profile, exit_codes, writer
from specmd.envelope import build_envelope


class InitUsageError(Exception):
    pass


def _build_frontmatter(*, profile: str, name: str, spec_version: str, status: str, last_updated: str, features: list[str]) -> dict:
    fm = {
        "specmd": core_profile.CORE_VERSION,
        "spec_version": spec_version,
        "status": status,
        "name": name,
        "last_updated": last_updated,
    }
    if profile == "optional":
        fm["specmd_optional"] = core_profile.OPTIONAL_VERSION
        fm["optional_features"] = {f: True for f in features}
    return fm


def _build_body() -> str:
    # INIT-006: no invented product behavior — every section is a TBD/Open
    # Issue placeholder, not a guessed requirement.
    lines = ["", "# Specification", "", "## Specification Contract", "", "TBD: describe what this document normatively governs.", ""]
    for section in core_profile.REQUIRED_SECTIONS:
        lines += [f"## {section}", "", "TBD", ""]
    lines += ["### Open Issues", "", "1. TBD", ""]
    return "\n".join(lines)


def run(
    *,
    output_path: Path,
    profile: str,
    features: list[str],
    input_json: dict | None,
    force: bool,
) -> tuple[dict, int]:
    if profile not in ("core", "optional"):
        raise InitUsageError(f"unsupported --profile '{profile}'")

    if profile == "core" and features:
        raise InitUsageError("--feature is invalid under the Core-only profile")
    if profile == "optional" and not features:
        # INIT-015: optional profile requires at least one selected feature.
        raise InitUsageError("--profile optional requires at least one --feature in non-interactive mode")
    for f in features:
        if f not in core_profile.RECOGNIZED_OPTIONAL_FEATURES:
            raise InitUsageError(f"unrecognized optional feature '{f}'")

    data = input_json or {}
    name = data.get("name", output_path.stem)
    spec_version = data.get("spec_version", "0.1.0")
    status = data.get("status", "draft")
    last_updated = data.get("last_updated", datetime.date.today().isoformat())

    frontmatter = _build_frontmatter(
        profile=profile, name=name, spec_version=spec_version, status=status, last_updated=last_updated, features=features
    )
    content = "---\n" + yaml.safe_dump(frontmatter, sort_keys=False).rstrip("\n") + "\n---\n" + _build_body()

    try:
        write_result = writer.safe_write(output_path, content, force=force)
        exit_code = exit_codes.SUCCESS
        status_str = "succeeded"
        writes = [{"path": write_result.path, "action": write_result.action}]
    except writer.WriteRefused as exc:
        exit_code = exit_codes.WRITE_ERROR
        status_str = "failed"
        writes = [{"path": str(exc.path), "action": "refused"}]

    envelope = build_envelope(
        command="init",
        status=status_str,
        inputs={"output": str(output_path), "profile": profile, "features": features},
        results={"frontmatter": frontmatter},
        findings=[],
        writes=writes,
        cognitive_requested="off",
        cognitive_used="none",
        cognitive_complete=True,
    )
    return envelope, exit_code


def load_input_json(raw: str | None, stdin_text: str | None) -> dict | None:
    if raw is None:
        return None
    text = stdin_text if raw == "-" else Path(raw).read_text(encoding="utf-8")
    return json.loads(text)
