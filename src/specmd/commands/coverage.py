"""`specmd test` (TEST-001..007). Module named coverage.py, not test.py, so
it never collides with pytest's own test-file discovery; the CLI subcommand
name is still "test".
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from specmd import exit_codes, module_resolver, structural, writer
from specmd.envelope import build_envelope
from specmd.ids import AcceptanceEntry, extract_acceptance_entries, extract_requirement_ids

_ACCEPTANCE_BLOCK_RE = re.compile(
    r"\*\*([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+)\s+—\s+[^:*]+:\*\*\s*(.*)"
)


def _acceptance_text_by_id(text: str, entries: list[AcceptanceEntry]) -> dict[str, str]:
    """Best-effort: capture the sentence following each acceptance ID's
    bold marker, verbatim — never fabricated (TEST-004 export content)."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        m = _ACCEPTANCE_BLOCK_RE.search(line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def run(
    *,
    root_spec_path: Path,
    set_root: Path,
    display_path: str,
    trace_mode: str,
    export_path: Path | None,
    run_integration: str | None,
) -> tuple[dict, int]:
    if run_integration:
        # TEST-005/006/007: no implementation-test integration is configured
        # in this build; never silently proceed as if one ran.
        envelope = build_envelope(
            command="test",
            status="failed",
            inputs={"root_spec": display_path, "run_integration": run_integration},
            results={"reason": f"no implementation-test integration named '{run_integration}' is configured in this build"},
            findings=[],
            writes=[],
            cognitive_requested="off",
            cognitive_used="none",
            cognitive_complete=True,
        )
        return envelope, exit_codes.CAPABILITY_UNAVAILABLE

    report = structural.analyze(root_spec_path, "auto")
    findings = list(report.findings)
    version_finding = structural.version_alignment_finding(report, str(root_spec_path))
    if version_finding is not None:
        findings.append(version_finding)

    module_res = module_resolver.resolve_modules(root_spec_path, set_root)
    all_texts = [root_spec_path.read_text(encoding="utf-8")]
    for m in module_res.modules:
        try:
            all_texts.append(m.read_text(encoding="utf-8"))
        except OSError:
            pass

    requirement_ids: list[str] = []
    acceptance_entries: list[AcceptanceEntry] = []
    acceptance_text: dict[str, str] = {}
    for t in all_texts:
        for rid in extract_requirement_ids(t):
            if rid not in requirement_ids:
                requirement_ids.append(rid)
        entries = extract_acceptance_entries(t)
        acceptance_entries += entries
        acceptance_text.update(_acceptance_text_by_id(t, entries))

    covered_ids: set[str] = set()
    for entry in acceptance_entries:
        covered_ids.update(entry.references)

    uncovered = [r for r in requirement_ids if r not in covered_ids]
    known = set(requirement_ids)
    unreferenced_acceptance = [e.id for e in acceptance_entries if not (set(e.references) & known)]

    for rid in uncovered:
        findings.append(
            structural.make_finding("TEST-003", "warning", f"requirement '{rid}' has no acceptance criterion referencing it", str(root_spec_path))
        )
    for aid in unreferenced_acceptance:
        findings.append(
            structural.make_finding(
                "TEST-003", "warning", f"acceptance criterion '{aid}' does not reference any known requirement ID", str(root_spec_path)
            )
        )

    results = {
        "requirement_ids": requirement_ids,
        "covered_requirement_ids": sorted(known & covered_ids),
        "uncovered_requirement_ids": uncovered,
        "acceptance_ids": [e.id for e in acceptance_entries],
        "unreferenced_acceptance_ids": unreferenced_acceptance,
    }

    writes = []
    if export_path is not None:
        plan = []
        for rid in requirement_ids:
            refs = [e.id for e in acceptance_entries if rid in e.references]
            plan.append(
                {
                    "requirement_id": rid,
                    "covered": rid in covered_ids,
                    "acceptance_ids": refs,
                    # TEST-004 lists preconditions/actions/expected outcomes as
                    # export content; those require semantic extraction this
                    # Deterministic-Only build cannot honestly perform, so they
                    # are left null rather than fabricated. The verbatim
                    # acceptance text (when found) is included instead.
                    "acceptance_text_verbatim": [acceptance_text.get(a) for a in refs if a in acceptance_text],
                    "preconditions": None,
                    "actions": None,
                    "expected_outcomes": None,
                    "verification_method": None,
                    "export_note": "preconditions/actions/expected_outcomes/verification_method require semantic "
                    "extraction not available in Deterministic-Only Mode (COG-003); left null rather than invented.",
                }
            )
        try:
            write_result = writer.safe_write(export_path, json.dumps(plan, indent=2) + "\n", force=True)
            writes.append({"path": write_result.path, "action": write_result.action})
        except writer.WriteRefused as exc:
            writes.append({"path": str(exc.path), "action": "refused"})

    status = "findings" if any(f.severity == "error" for f in findings) else "succeeded"
    if structural.version_unresolved(report):
        status = "indeterminate"
    exit_code = {"succeeded": exit_codes.SUCCESS, "findings": exit_codes.FINDINGS, "indeterminate": exit_codes.INPUT_ERROR}[status]

    envelope = build_envelope(
        command="test",
        status=status,
        inputs={"root_spec": display_path, "trace": trace_mode, "export": str(export_path) if export_path else None},
        results=results,
        findings=findings,
        writes=writes,
        cognitive_requested="off",
        cognitive_used="none",
        cognitive_complete=True,
    )
    return envelope, exit_code
