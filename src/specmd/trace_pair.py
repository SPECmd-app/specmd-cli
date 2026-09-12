"""Trace Pair validation (TRACE-001..017, Trace Binding Contract SPEC.md
section 5.4).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from specmd.findings import EVIDENCE_DETERMINISTIC, SEVERITY_ERROR, SEVERITY_WARNING, Finding
from specmd.frontmatter import parse_document

RESULT_ALIGNED = "aligned"
RESULT_MISALIGNED = "misaligned"
RESULT_INDETERMINATE = "indeterminate"

TRACE_RESULT_SUCCESS = "resolved"
TRACE_RESULT_INDETERMINATE = "indeterminate"
TRACE_RESULT_NOT_REQUESTED = "not_requested"

_MENTIONED_ID_RE = re.compile(r"\b([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+)\b")
_TABLE_DIVIDER_CELL_RE = re.compile(r"^:?-+:?$")


def table_mapped_ids(trace_text: str) -> set[str]:
    """IDs that appear in an actual Markdown table row of the Trace Document
    — a genuine mapping — rather than merely being mentioned anywhere in the
    text (e.g. in an Open Issues paragraph explaining that an ID is *not yet*
    mapped, which must not itself count as coverage).
    """
    ids: set[str] = set()
    for line in trace_text.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|") and len(stripped) >= 2):
            continue
        cells = [c.strip() for c in stripped[1:-1].split("|")]
        if cells and all(_TABLE_DIVIDER_CELL_RE.match(c) for c in cells if c):
            continue  # header/body divider row, e.g. |---|---|
        for cell in cells:
            ids.update(_MENTIONED_ID_RE.findall(cell))
    return ids


@dataclass
class TracePairReport:
    trace_mode: str  # "auto" | "none" | explicit path string
    trace_declared: bool
    trace_path: Path | None
    trace_result: str
    pair_result: str | None
    missing_requirement_ids: list[str] = field(default_factory=list)
    missing_acceptance_ids: list[str] = field(default_factory=list)
    unknown_ids: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)


def _finding(rule_id, severity, message, file=None, line=None) -> Finding:
    return Finding(rule_id=rule_id, severity=severity, message=message, evidence_type=EVIDENCE_DETERMINISTIC, file=file, line=line)


def default_trace_path(root_spec_path: Path) -> Path:
    return root_spec_path.parent / "TRACE.md"


def validate_pair(
    *,
    trace_mode: str,
    root_spec_path: Path,
    root_spec_text: str,
    root_spec_frontmatter: dict,
    requirement_ids: list[str],
    acceptance_ids: list[str] | None = None,
) -> TracePairReport:
    acceptance_ids = acceptance_ids or []
    trace_declared = bool(
        isinstance(root_spec_frontmatter.get("optional_features"), dict)
        and root_spec_frontmatter["optional_features"].get("trace") is True
    )

    if trace_mode == "none":
        return TracePairReport(
            trace_mode="none",
            trace_declared=trace_declared,
            trace_path=None,
            trace_result=TRACE_RESULT_NOT_REQUESTED,
            pair_result=None,
        )

    explicit_path = Path(trace_mode) if trace_mode not in ("auto",) else None
    if explicit_path is not None:
        candidate = explicit_path
    elif trace_declared:
        candidate = default_trace_path(root_spec_path)
    else:
        # TRACE-004: under auto, an adjacent TRACE.md not declared by the
        # root spec must not affect validation.
        return TracePairReport(
            trace_mode="auto",
            trace_declared=False,
            trace_path=None,
            trace_result=TRACE_RESULT_NOT_REQUESTED,
            pair_result=None,
        )

    findings: list[Finding] = []
    if not candidate.exists():
        findings.append(_finding("TRACE-005", SEVERITY_ERROR, f"Trace Document '{candidate}' could not be resolved", str(candidate)))
        return TracePairReport(
            trace_mode=trace_mode,
            trace_declared=trace_declared,
            trace_path=candidate,
            trace_result=TRACE_RESULT_INDETERMINATE,
            pair_result=RESULT_INDETERMINATE,
            findings=findings,
        )

    trace_text = candidate.read_text(encoding="utf-8")
    trace_doc = parse_document(str(candidate), trace_text)
    trace_fm = trace_doc.frontmatter or {}

    pair_result = RESULT_ALIGNED

    traces_spec = trace_fm.get("traces_spec")
    root_spec_version = root_spec_frontmatter.get("spec_version")
    if traces_spec != root_spec_version:
        findings.append(
            _finding(
                "TRACE-006",
                SEVERITY_ERROR,
                f"TRACE.md traces_spec '{traces_spec}' does not match Root Specification spec_version '{root_spec_version}'",
                str(candidate),
            )
        )
        pair_result = RESULT_MISALIGNED

    traces_file = trace_fm.get("traces_file")
    resolved_traces_file = (candidate.parent / traces_file).resolve() if traces_file else None
    if resolved_traces_file != root_spec_path.resolve():
        findings.append(
            _finding(
                "TRACE-006",
                SEVERITY_ERROR,
                f"TRACE.md traces_file '{traces_file}' does not resolve to the validated Root Specification",
                str(candidate),
            )
        )
        pair_result = RESULT_MISALIGNED

    # TRACE-007/009 coverage is determined by genuine table mappings, not by
    # an ID merely being mentioned anywhere in the document (e.g. in prose
    # explaining that it is *not yet* mapped) — see table_mapped_ids.
    mentioned_ids = table_mapped_ids(trace_text)
    required_ids = set(requirement_ids)
    known_acceptance_ids = set(acceptance_ids)
    # TRACE-009: an identifier is "unknown" only if it matches neither a
    # requirement/invariant ID nor an acceptance ID from the Specification
    # Set — mentioning a legitimate ACC-*/IACC-* ID must not be flagged.
    known_ids = required_ids | known_acceptance_ids

    missing_requirement_ids = sorted(required_ids - mentioned_ids)
    missing_acceptance_ids = sorted(known_acceptance_ids - mentioned_ids)
    unknown_ids = sorted(mentioned_ids - known_ids)

    for rid in missing_requirement_ids:
        # TRACE-007 (MUST): every current requirement/invariant ID must appear.
        findings.append(_finding("TRACE-007", SEVERITY_ERROR, f"requirement/invariant '{rid}' is not mapped in TRACE.md", str(candidate)))
    for aid in missing_acceptance_ids:
        # TRACE-008 (SHOULD): acceptance IDs should be mapped too.
        findings.append(_finding("TRACE-008", SEVERITY_WARNING, f"acceptance identifier '{aid}' is not mapped in TRACE.md", str(candidate)))
    for rid in unknown_ids:
        findings.append(_finding("TRACE-009", SEVERITY_WARNING, f"TRACE.md references unknown identifier '{rid}'", str(candidate)))

    if missing_requirement_ids or unknown_ids:
        pair_result = RESULT_MISALIGNED

    return TracePairReport(
        trace_mode=trace_mode,
        trace_declared=trace_declared,
        trace_path=candidate,
        trace_result=TRACE_RESULT_SUCCESS,
        pair_result=pair_result,
        missing_requirement_ids=missing_requirement_ids,
        missing_acceptance_ids=missing_acceptance_ids,
        unknown_ids=unknown_ids,
        findings=findings,
    )
