"""`specmd trace create` / `specmd trace update` (TRACEGEN-001..013,
Trace Binding Contract SPEC.md section 5.4).
"""

from __future__ import annotations

import datetime
from pathlib import Path

import yaml

from specmd import core_profile, exit_codes, module_resolver, structural, trace_pair, writer
from specmd.envelope import build_envelope
from specmd.frontmatter import parse_document
from specmd.ids import extract_acceptance_entries, extract_requirement_ids


class TraceUsageError(Exception):
    pass


def _version_alignment_refusal(root_spec_path: Path, display_path: str, command: str) -> tuple[dict, int] | None:
    """PORT-006/007/008 (SPEC.md 4.14): refuse, non-mutating, with the
    proposed-spec-change remediation as the first suggested step, when the
    target document's declared exact standards version cannot be resolved.
    Returns an (envelope, exit_code) pair to return immediately, or None
    when the version is resolved and the caller should proceed.
    """
    report = structural.analyze(root_spec_path, "auto")
    finding = structural.version_alignment_finding(report, str(root_spec_path))
    if finding is None:
        return None
    envelope = build_envelope(
        command=command,
        status="indeterminate",
        inputs={"root_spec": display_path},
        results={},
        findings=[finding],
        writes=[],
        cognitive_requested="off",
        cognitive_used="none",
        cognitive_complete=True,
    )
    return envelope, exit_codes.INPUT_ERROR


def _collect_ids(root_spec_path: Path, set_root: Path):
    module_res = module_resolver.resolve_modules(root_spec_path, set_root)
    texts = [root_spec_path.read_text(encoding="utf-8")]
    for m in module_res.modules:
        try:
            texts.append(m.read_text(encoding="utf-8"))
        except OSError:
            pass
    requirement_ids: list[str] = []
    acceptance_entries = []
    for t in texts:
        for rid in extract_requirement_ids(t):
            if rid not in requirement_ids:
                requirement_ids.append(rid)
        acceptance_entries += extract_acceptance_entries(t)
    return requirement_ids, acceptance_entries, module_res


def _bump_minor(spec_version: str) -> str:
    parts = spec_version.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        return spec_version
    major, minor, _patch = (int(p) for p in parts)
    return f"{major}.{minor + 1}.0"


def _render_trace_body(*, root_name: str, root_spec_version: str, requirement_ids: list[str], acceptance_entries) -> str:
    lines = [
        "",
        f"# {root_name} — TRACE.md",
        "",
        "## Purpose",
        "",
        "This informative companion maps the Specification Set to implementation "
        "and verification evidence. The normative specification remains "
        "authoritative; this document does not add, remove, or reinterpret "
        "required behavior.",
        "",
        "## Requirements Traceability Matrix",
        "",
        "| Requirement / Invariant ID | Implementation | Evidence |",
        "|---|---|---|",
    ]
    for rid in requirement_ids:
        lines.append(f"| {rid} | TBD | Planned |")
    lines += ["", "## Acceptance Identifiers", "", "| Acceptance ID | References | Implementation | Evidence |", "|---|---|---|---|"]
    for entry in acceptance_entries:
        refs = ", ".join(entry.references) if entry.references else "TBD"
        lines.append(f"| {entry.id} | {refs} | TBD | Planned |")
    lines.append("")
    return "\n".join(lines)


def create(
    *,
    root_spec_path: Path,
    set_root: Path,
    display_path: str,
    output_path: Path | None,
    enable_optional: bool,
    force: bool,
) -> tuple[dict, int]:
    refusal = _version_alignment_refusal(root_spec_path, display_path, "trace_create")
    if refusal is not None:
        return refusal

    root_text = root_spec_path.read_text(encoding="utf-8")
    root_doc = parse_document(str(root_spec_path), root_text)
    fm = dict(root_doc.frontmatter or {})

    trace_declared = bool(isinstance(fm.get("optional_features"), dict) and fm["optional_features"].get("trace") is True)

    spec_writes: list[dict] = []
    if not trace_declared:
        if not enable_optional:
            # TRACEGEN-007: remain non-mutating without explicit authorization.
            envelope = build_envelope(
                command="trace_create",
                status="failed",
                inputs={"root_spec": display_path, "enable_optional": enable_optional},
                results={
                    "reason": (
                        "Root Specification does not declare optional_features.trace: true. "
                        "Re-run with --enable-optional to add the required Optional declaration "
                        "and spec_version bump before generating TRACE.md."
                    )
                },
                findings=[],
                writes=[],
                cognitive_requested="off",
                cognitive_used="none",
                cognitive_complete=True,
            )
            return envelope, exit_codes.WRITE_ERROR

        # TRACEGEN-008: add a compatible specmd_optional declaration, enable
        # the trace feature, and bump spec_version, then write SPEC.md.
        # "Compatible" means matching the document's own already-declared
        # Core version (the Optional companion MUST match its declared Core
        # version) — by this point _version_alignment_refusal has already
        # confirmed that declared version is one this build supports, so it
        # is always a safe choice, not just a same-numbered convenience.
        fm.setdefault("specmd_optional", fm.get("specmd", core_profile.OPTIONAL_VERSION))
        features = dict(fm.get("optional_features") or {})
        features["trace"] = True
        fm["optional_features"] = features
        old_version = fm.get("spec_version", "0.1.0")
        fm["spec_version"] = _bump_minor(old_version)
        fm["last_updated"] = datetime.date.today().isoformat()

        new_root_text = "---\n" + yaml.safe_dump(fm, sort_keys=False).rstrip("\n") + "\n---\n" + root_doc.body
        write_result = writer.safe_write(root_spec_path, new_root_text, force=True)
        spec_writes.append({"path": write_result.path, "action": write_result.action})
        root_text = new_root_text

    trace_out_path = output_path or trace_pair.default_trace_path(root_spec_path)

    requirement_ids, acceptance_entries, _module_res = _collect_ids(root_spec_path, set_root)

    traces_file = trace_out_path.parent
    try:
        rel = root_spec_path.resolve().relative_to(traces_file.resolve())
        traces_file_value = str(rel)
    except ValueError:
        traces_file_value = str(root_spec_path.resolve())

    trace_frontmatter = {
        "specmd_trace": core_profile.TRACE_FORMAT_VERSION,
        "traces_file": traces_file_value,
        "traces_spec": fm.get("spec_version"),
        "status": "draft",
        "name": f"{fm.get('name', root_spec_path.stem)} Traceability",
        "last_updated": datetime.date.today().isoformat(),
    }
    body = _render_trace_body(
        root_name=fm.get("name", root_spec_path.stem),
        root_spec_version=fm.get("spec_version"),
        requirement_ids=requirement_ids,
        acceptance_entries=acceptance_entries,
    )
    trace_content = "---\n" + yaml.safe_dump(trace_frontmatter, sort_keys=False).rstrip("\n") + "\n---\n" + body

    try:
        write_result = writer.safe_write(trace_out_path, trace_content, force=force)
        writes = spec_writes + [{"path": write_result.path, "action": write_result.action}]
        write_ok = True
    except writer.WriteRefused as exc:
        writes = spec_writes + [{"path": str(exc.path), "action": "refused"}]
        write_ok = False

    if not write_ok:
        envelope = build_envelope(
            command="trace_create",
            status="failed",
            inputs={"root_spec": display_path, "output": str(trace_out_path)},
            results={},
            findings=[],
            writes=writes,
            cognitive_requested="off",
            cognitive_used="none",
            cognitive_complete=True,
        )
        return envelope, exit_codes.WRITE_ERROR

    # TRACEGEN-011: after create, perform Trace Pair validation.
    pair = trace_pair.validate_pair(
        trace_mode=str(trace_out_path),
        root_spec_path=root_spec_path,
        root_spec_text=root_text,
        root_spec_frontmatter=fm,
        requirement_ids=requirement_ids,
        acceptance_ids=[e.id for e in acceptance_entries],
    )

    envelope = build_envelope(
        command="trace_create",
        status="succeeded" if pair.pair_result == trace_pair.RESULT_ALIGNED else "findings",
        inputs={"root_spec": display_path, "output": str(trace_out_path), "enable_optional": enable_optional},
        results={
            "requirement_ids_mapped": requirement_ids,
            "acceptance_ids_mapped": [e.id for e in acceptance_entries],
            "pair_result": pair.pair_result,
            "core_profile": {"trace_format_version": core_profile.TRACE_FORMAT_VERSION, "provenance": core_profile.PROFILE_PROVENANCE},
        },
        findings=pair.findings,
        writes=writes,
        cognitive_requested="off",
        cognitive_used="none",
        cognitive_complete=True,
    )
    exit_code = exit_codes.SUCCESS if pair.pair_result == trace_pair.RESULT_ALIGNED else exit_codes.FINDINGS
    return envelope, exit_code


def update(
    *,
    root_spec_path: Path,
    set_root: Path,
    display_path: str,
    trace_path: Path | None,
    force: bool,
) -> tuple[dict, int]:
    refusal = _version_alignment_refusal(root_spec_path, display_path, "trace_update")
    if refusal is not None:
        return refusal

    resolved_trace_path = trace_path or trace_pair.default_trace_path(root_spec_path)
    if not resolved_trace_path.exists():
        envelope = build_envelope(
            command="trace_update",
            status="failed",
            inputs={"root_spec": display_path, "trace": str(resolved_trace_path)},
            results={"reason": f"'{resolved_trace_path}' does not exist; run `specmd trace create` first"},
            findings=[],
            writes=[],
            cognitive_requested="off",
            cognitive_used="none",
            cognitive_complete=True,
        )
        return envelope, exit_codes.INPUT_ERROR

    root_text = root_spec_path.read_text(encoding="utf-8")
    root_doc = parse_document(str(root_spec_path), root_text)
    fm = root_doc.frontmatter or {}

    requirement_ids, acceptance_entries, _module_res = _collect_ids(root_spec_path, set_root)
    acceptance_ids = [e.id for e in acceptance_entries]

    existing_text = resolved_trace_path.read_text(encoding="utf-8")
    # Reconciliation must key off genuine table mappings, not any mention of
    # an ID anywhere in the document (see trace_pair.table_mapped_ids).
    mentioned = trace_pair.table_mapped_ids(existing_text)

    new_requirement_ids = [r for r in requirement_ids if r not in mentioned]
    new_acceptance_ids = [a for a in acceptance_ids if a not in mentioned]
    # TRACEGEN-009/010: surface (never silently delete) IDs that were
    # mentioned before but no longer exist in the current Specification Set.
    current_known = set(requirement_ids) | set(acceptance_ids)
    removed_ids = sorted(mentioned - current_known)

    appended = ""
    if new_requirement_ids or new_acceptance_ids:
        today = datetime.date.today().isoformat()
        appended += f"\n\n## Newly Discovered Identifiers (added by `specmd trace update` on {today})\n\n"
        if new_requirement_ids:
            appended += "| Requirement / Invariant ID | Implementation | Evidence |\n|---|---|---|\n"
            for rid in new_requirement_ids:
                appended += f"| {rid} | TBD | Planned |\n"
        if new_acceptance_ids:
            appended += "\n| Acceptance ID | Implementation | Evidence |\n|---|---|---|\n"
            for aid in new_acceptance_ids:
                appended += f"| {aid} | TBD | Planned |\n"

    removed_note = ""
    if removed_ids:
        today = datetime.date.today().isoformat()
        removed_note = (
            f"\n\n## Identifiers No Longer Present in the Specification Set (flagged by `specmd trace update` on {today})\n\n"
            "The following identifiers were previously mapped in this document but were not found in the "
            "current Root Specification or its Normative Modules. They are preserved above for manual review "
            "rather than deleted (TRACEGEN-010).\n\n"
            + "\n".join(f"- {rid}" for rid in removed_ids)
            + "\n"
        )

    new_text = existing_text
    # traces_spec must track the Root Specification's current spec_version.
    trace_doc = parse_document(str(resolved_trace_path), existing_text)
    trace_fm = trace_doc.frontmatter or {}
    if trace_fm.get("traces_spec") != fm.get("spec_version"):
        new_frontmatter = dict(trace_fm)
        new_frontmatter["traces_spec"] = fm.get("spec_version")
        new_frontmatter["last_updated"] = datetime.date.today().isoformat()
        new_text = "---\n" + yaml.safe_dump(new_frontmatter, sort_keys=False).rstrip("\n") + "\n---\n" + trace_doc.body

    new_text = new_text + appended + removed_note

    try:
        write_result = writer.safe_write(resolved_trace_path, new_text, force=True)
        writes = [{"path": write_result.path, "action": write_result.action}]
    except writer.WriteRefused as exc:
        writes = [{"path": str(exc.path), "action": "refused"}]
        envelope = build_envelope(
            command="trace_update",
            status="failed",
            inputs={"root_spec": display_path, "trace": str(resolved_trace_path)},
            results={},
            findings=[],
            writes=writes,
            cognitive_requested="off",
            cognitive_used="none",
            cognitive_complete=True,
        )
        return envelope, exit_codes.WRITE_ERROR

    # TRACEGEN-011: run pair validation after the update.
    pair = trace_pair.validate_pair(
        trace_mode=str(resolved_trace_path),
        root_spec_path=root_spec_path,
        root_spec_text=root_text,
        root_spec_frontmatter=fm,
        requirement_ids=requirement_ids,
        acceptance_ids=acceptance_ids,
    )

    envelope = build_envelope(
        command="trace_update",
        status="succeeded" if pair.pair_result == trace_pair.RESULT_ALIGNED else "findings",
        inputs={"root_spec": display_path, "trace": str(resolved_trace_path)},
        results={
            "new_requirement_ids": new_requirement_ids,
            "new_acceptance_ids": new_acceptance_ids,
            "removed_ids_flagged": removed_ids,
            "pair_result": pair.pair_result,
        },
        findings=pair.findings,
        writes=writes,
        cognitive_requested="off",
        cognitive_used="none",
        cognitive_complete=True,
    )
    exit_code = exit_codes.SUCCESS if pair.pair_result == trace_pair.RESULT_ALIGNED else exit_codes.FINDINGS
    return envelope, exit_code
