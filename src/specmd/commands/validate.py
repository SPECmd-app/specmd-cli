"""`specmd validate` (VAL-001..017, TRACE-001..017, INV-001..008)."""

from __future__ import annotations

from pathlib import Path

from specmd import core_profile, exit_codes, module_resolver, structural, trace_pair
from specmd.cognitive import negotiate
from specmd.envelope import build_envelope
from specmd.ids import extract_acceptance_entries, extract_requirement_ids


def run(
    *,
    root_spec_path: Path,
    set_root: Path,
    display_path: str,
    profile: str,
    trace_mode: str,
    cognitive_mode: str,
    strict: bool,
) -> tuple[dict, int]:
    report = structural.analyze(root_spec_path, profile)
    spec_result = structural.overall_result(report)

    findings = list(report.findings)

    # PORT-006/007/008 (SPEC.md 4.14): when the exact declared standards
    # version cannot be resolved, surface the proposed-spec-change
    # remediation as the first suggested next step.
    version_finding = structural.version_alignment_finding(report, str(root_spec_path))
    if version_finding is not None:
        findings.append(version_finding)

    # VAL-005 / REL-001: report every evaluated file in the Specification Set;
    # a missing/unreadable module must not be reported as successful.
    module_res = module_resolver.resolve_modules(root_spec_path, set_root)
    evaluated_files = [str(root_spec_path)] + [str(m) for m in module_res.modules]
    for path, error in module_res.unreadable:
        findings.append(
            structural.make_finding("VAL-005", "error", f"Normative Module '{path}' could not be read: {error}", str(root_spec_path))
        )
        spec_result = structural.RESULT_NON_CONFORMING
    for cyc in module_res.cycles:
        findings.append(structural.make_finding("VAL-010", "error", f"Normative Module cycle detected: {cyc}", str(root_spec_path)))
        spec_result = structural.RESULT_NON_CONFORMING
    for esc in module_res.escaped:
        findings.append(
            structural.make_finding("VAL-011", "error", f"Normative Module path '{esc}' escapes the Specification Set root", str(root_spec_path))
        )
        spec_result = structural.RESULT_NON_CONFORMING
    for dup in module_res.duplicates:
        findings.append(structural.make_finding("VAL-010", "warning", f"Normative Module '{dup}' resolved more than once", str(root_spec_path)))

    if strict and any(f.severity == "warning" for f in findings) and spec_result == structural.RESULT_CONFORMING:
        # ICD-VAL §8.2: --strict promotes warnings to a non-successful
        # command result without reclassifying them as conformance errors.
        promoted_non_success = True
    else:
        promoted_non_success = False

    # Trace Pair validation.
    all_texts = [root_spec_path.read_text(encoding="utf-8")]
    for module_path in module_res.modules:
        try:
            all_texts.append(module_path.read_text(encoding="utf-8"))
        except OSError:
            pass
    requirement_ids: list[str] = []
    acceptance_ids: list[str] = []
    for t in all_texts:
        requirement_ids += extract_requirement_ids(t)
        acceptance_ids += [e.id for e in extract_acceptance_entries(t)]

    trace_report = trace_pair.validate_pair(
        trace_mode=trace_mode,
        root_spec_path=root_spec_path,
        root_spec_text=report.doc.text,
        root_spec_frontmatter=report.doc.frontmatter or {},
        requirement_ids=requirement_ids,
        acceptance_ids=acceptance_ids,
    )
    findings += trace_report.findings

    cog = negotiate(cognitive_mode)

    if spec_result == structural.RESULT_NON_CONFORMING:
        status = "findings"
    elif spec_result == structural.RESULT_INDETERMINATE:
        status = "indeterminate"
    elif promoted_non_success:
        status = "findings"
    elif any(f.severity == "error" for f in findings):
        status = "findings"
    else:
        status = "succeeded"

    exit_code = exit_codes.STATUS_TO_EXIT[status]
    # TRACE-002 / ICD-EXIT-002: a misaligned pair returns 1 even if the
    # independent spec result is conforming.
    if trace_report.pair_result == trace_pair.RESULT_MISALIGNED and exit_code == exit_codes.SUCCESS:
        exit_code = exit_codes.FINDINGS
        status = "findings"
    if trace_report.trace_result == trace_pair.TRACE_RESULT_INDETERMINATE and exit_code == exit_codes.SUCCESS:
        exit_code = exit_codes.INPUT_ERROR

    results = {
        "specification_result": spec_result,
        "core_profile": {
            "version": core_profile.CORE_VERSION,
            "optional_version": core_profile.OPTIONAL_VERSION,
            "provenance": core_profile.PROFILE_PROVENANCE,
        },
        "effective_profile": report.effective_profile,
        "evaluated_files": evaluated_files,
        "trace": {
            "mode_requested": trace_mode,
            "declared": trace_report.trace_declared,
            "path": str(trace_report.trace_path) if trace_report.trace_path else None,
            "trace_result": trace_report.trace_result,
            "pair_result": trace_report.pair_result,
            "missing_requirement_ids": trace_report.missing_requirement_ids,
            "missing_acceptance_ids": trace_report.missing_acceptance_ids,
            "unknown_ids": trace_report.unknown_ids,
        },
    }
    if cog.exit_override is not None:
        # COG-009 / ICD-EXIT-001: cognitive mode 'required' but unavailable
        # makes the semantic result indeterminate; the JSON `status` and the
        # process exit code must stay consistent, so both change together.
        exit_code = cog.exit_override
        status = "indeterminate"

    envelope = build_envelope(
        command="validate",
        status=status,
        inputs={"root_spec": display_path, "profile": profile, "trace": trace_mode, "strict": strict},
        results=results,
        findings=findings,
        writes=[],
        cognitive_requested=cog.requested,
        cognitive_used=cog.used,
        cognitive_complete=cog.complete,
    )
    return envelope, exit_code
