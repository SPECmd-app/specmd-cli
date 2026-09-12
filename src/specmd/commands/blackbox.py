"""`specmd blackbox` (BBX-001..012).

Deterministic, structural-only Black-Box Contract inventory: no Cognitive
Provider is configured in this build, so this command does not attempt
semantic inference (BBX-004/005) — it reports what the Specification Set's
structure explicitly contains, distinguished from what a Trace Document
says about implementation/evidence status (BBX-007..010), and never touches
an implementation (BBX-012).
"""

from __future__ import annotations

import json
from pathlib import Path

from specmd import core_profile, exit_codes, module_resolver, structural, trace_pair, writer
from specmd.envelope import build_envelope
from specmd.frontmatter import strip_leading_numeral
from specmd.ids import extract_acceptance_entries, extract_requirement_ids

# Sections that, per the reconstructed Core profile, typically carry
# black-box-relevant content: actors/interfaces/errors/state.
_INTERFACE_SECTION_NAMES = ("Interfaces and External Contracts", "System Model")


def run(
    *,
    root_spec_path: Path,
    set_root: Path,
    display_path: str,
    trace_mode: str,
    export_path: Path | None,
) -> tuple[dict, int]:
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
    acceptance_ids: list[str] = []
    for t in all_texts:
        for rid in extract_requirement_ids(t):
            if rid not in requirement_ids:
                requirement_ids.append(rid)
        acceptance_ids += [e.id for e in extract_acceptance_entries(t)]

    # BBX-002/003: inventory explicitly present interface-relevant sections;
    # report absence as a gap rather than guessing content.
    present_sections = {strip_leading_numeral(h[1]) for h in report.doc.headings if h[0] <= 2}
    interface_inventory = {name: (name in present_sections) for name in _INTERFACE_SECTION_NAMES}
    missing_interface_sections = [name for name, present in interface_inventory.items() if not present]
    for name in missing_interface_sections:
        findings.append(
            structural.make_finding(
                "BBX-003",
                "warning",
                f"expected black-box-relevant section '{name}' was not found; interface inventory is incomplete",
                str(root_spec_path),
            )
        )

    # BBX-006/007/009/010: trace correlation, kept as a separate dimension.
    trace_report = trace_pair.validate_pair(
        trace_mode=trace_mode,
        root_spec_path=root_spec_path,
        root_spec_text=report.doc.text,
        root_spec_frontmatter=report.doc.frontmatter or {},
        requirement_ids=requirement_ids,
        acceptance_ids=acceptance_ids,
    )
    findings += trace_report.findings

    implementation_reference_status: dict[str, str] = {}
    executed_evidence_status: dict[str, str] = {}
    trace_available = trace_report.trace_path is not None and trace_report.trace_result == trace_pair.TRACE_RESULT_SUCCESS
    if trace_available:
        trace_text = trace_report.trace_path.read_text(encoding="utf-8")
        row_map = trace_pair.row_evidence_map(trace_text)
        for rid in requirement_ids:
            row = row_map.get(rid)
            if row is None:
                implementation_reference_status[rid] = "unmapped"
                executed_evidence_status[rid] = "unmapped"
                continue
            implementation_reference_status[rid] = "TBD" if trace_pair.is_placeholder(row["implementation"]) else "referenced"
            # Heuristic (disclosed): "executed" requires a non-placeholder
            # Implementation cell that also looks like it names test evidence,
            # or an Evidence-like cell that is itself non-placeholder text —
            # never invented, only read from what the Trace Document states.
            impl = row["implementation"]
            evid = row["evidence"]
            looks_executed = (not trace_pair.is_placeholder(impl) and "test" in impl.lower()) or (
                evid and not trace_pair.is_placeholder(evid)
            )
            executed_evidence_status[rid] = "planned_or_unclear" if trace_pair.is_placeholder(impl) else (
                "likely_executed" if looks_executed else "unclear"
            )

    results = {
        "core_profile": {
            "version": core_profile.CORE_VERSION,
            "optional_version": core_profile.OPTIONAL_VERSION,
            "provenance": core_profile.PROFILE_PROVENANCE,
        },
        "requirement_ids": requirement_ids,
        "acceptance_ids": acceptance_ids,
        "interface_section_inventory": interface_inventory,
        # BBX-010: four separate completeness dimensions.
        "completeness": {
            "specification_completeness": {
                "missing_interface_sections": missing_interface_sections,
                "structural_errors": [f.to_dict() for f in report.findings if f.severity == "error"],
            },
            "trace_coverage": {
                "available": trace_available,
                "pair_result": trace_report.pair_result,
                "missing_requirement_ids": trace_report.missing_requirement_ids,
                "missing_acceptance_ids": trace_report.missing_acceptance_ids,
            },
            "implementation_reference_completeness": {
                "available": trace_available,
                "by_requirement_id": implementation_reference_status,
            },
            "executed_evidence_completeness": {
                "available": trace_available,
                "by_requirement_id": executed_evidence_status,
                "note": (
                    "heuristic: derived from Trace Document cell text, not from actually running anything "
                    "(BBX-012); 'likely_executed' is a textual signal, not proof"
                ),
            },
        },
    }

    writes = []
    if export_path is not None:
        try:
            write_result = writer.safe_write(export_path, json.dumps(results, indent=2) + "\n", force=True)
            writes.append({"path": write_result.path, "action": write_result.action})
        except writer.WriteRefused as exc:
            writes.append({"path": str(exc.path), "action": "refused"})

    status = "findings" if any(f.severity == "error" for f in findings) else "succeeded"
    if structural.version_unresolved(report):
        status = "indeterminate"
    exit_code = {"succeeded": exit_codes.SUCCESS, "findings": exit_codes.FINDINGS, "indeterminate": exit_codes.INPUT_ERROR}[status]

    envelope = build_envelope(
        command="blackbox",
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
