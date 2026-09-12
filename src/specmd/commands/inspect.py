"""`specmd inspect` (INSP-001..008)."""

from __future__ import annotations

from pathlib import Path

from specmd import core_profile, exit_codes, module_resolver, structural, trace_pair
from specmd.cognitive import negotiate
from specmd.envelope import build_envelope
from specmd.findings import SEVERITY_INFORMATION
from specmd.ids import extract_acceptance_entries, extract_requirement_ids


def run(
    *,
    root_spec_path: Path,
    set_root: Path,
    display_path: str,
    profile: str,
    trace_mode: str,
    cognitive_mode: str,
) -> tuple[dict, int]:
    report = structural.analyze(root_spec_path, profile)
    findings = list(report.findings)

    # PORT-006/007/008 (SPEC.md 4.14): when the exact declared standards
    # version cannot be resolved, surface the proposed-spec-change
    # remediation as the first suggested next step.
    version_finding = structural.version_alignment_finding(report, str(root_spec_path))
    if version_finding is not None:
        findings.append(version_finding)

    # INSP-005/006/007: line/token counts are always informational; the
    # compactness target only applies when the DOCUMENT ITSELF claims to be
    # the Core standard artifact (never a project spec like ours), so no
    # such document exists in this MVP's expected inputs. Report the target
    # for comparison only if a document explicitly names itself "SPEC.md
    # Core" in its `name` field, as the closest available signal.
    is_core_artifact = str((report.doc.frontmatter or {}).get("name", "")).strip().lower() == "spec.md core"
    measurement_finding_extra = {}
    if is_core_artifact:
        over_lines = report.measurements["line_count"] > core_profile.CORE_COMPACTNESS_MAX_LINES
        over_tokens = report.measurements["estimated_token_count"] > core_profile.CORE_COMPACTNESS_MAX_TOKENS
        measurement_finding_extra = {
            "compactness_target_lines": core_profile.CORE_COMPACTNESS_MAX_LINES,
            "compactness_target_tokens": core_profile.CORE_COMPACTNESS_MAX_TOKENS,
            "exceeds_compactness_target": over_lines or over_tokens,
        }
        if over_lines or over_tokens:
            findings.append(
                structural.make_finding(
                    "INSP-007",
                    SEVERITY_INFORMATION,
                    "document identifies itself as SPEC.md Core and exceeds the Core compactness target",
                    str(root_spec_path),
                )
            )

    module_res = module_resolver.resolve_modules(root_spec_path, set_root)
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
    # COG-003: Deterministic-Only Mode must identify that semantic/ambiguity/
    # completeness/portability analysis was not performed.
    if not cog.complete and cog.message:
        findings.append(
            structural.make_finding("INSP-008", SEVERITY_INFORMATION, cog.message, str(root_spec_path))
        )

    if structural.version_unresolved(report):
        # PORT-007: an unresolved exact standards version makes the result
        # indeterminate — the same status validate() reports for this exact
        # condition (ICD-EXIT-001 requires consistent status/exit semantics
        # for the same root cause across commands).
        status = "indeterminate"
        exit_code = exit_codes.INPUT_ERROR
    else:
        status = "findings" if any(f.severity == "error" for f in findings) else "succeeded"
        exit_code = exit_codes.FINDINGS if status == "findings" else exit_codes.SUCCESS
    if cog.exit_override is not None:
        # COG-009 / ICD-EXIT-001: keep JSON `status` and exit code consistent
        # when cognitive mode 'required' is unavailable.
        exit_code = cog.exit_override
        status = "indeterminate"

    results = {
        "measurements": {**report.measurements, **measurement_finding_extra},
        "core_profile": {
            "version": core_profile.CORE_VERSION,
            "optional_version": core_profile.OPTIONAL_VERSION,
            "provenance": core_profile.PROFILE_PROVENANCE,
        },
        "effective_profile": report.effective_profile,
        "trace": {
            "trace_result": trace_report.trace_result,
            "pair_result": trace_report.pair_result,
            "missing_requirement_ids": trace_report.missing_requirement_ids,
            "missing_acceptance_ids": trace_report.missing_acceptance_ids,
            "unknown_ids": trace_report.unknown_ids,
        },
    }

    envelope = build_envelope(
        command="inspect",
        status=status,
        inputs={"root_spec": display_path, "profile": profile, "trace": trace_mode},
        results=results,
        findings=findings,
        writes=[],
        cognitive_requested=cog.requested,
        cognitive_used=cog.used,
        cognitive_complete=cog.complete,
    )
    return envelope, exit_code
