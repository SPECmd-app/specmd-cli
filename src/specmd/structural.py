"""Deterministic structural checks against the Core/Optional profile
(core_profile.py), reconciled against the authoritative standard text.
Shared by `validate` and `inspect`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from specmd import core_profile, human_only
from specmd.findings import EVIDENCE_DETERMINISTIC, SEVERITY_ERROR, SEVERITY_INFORMATION, SEVERITY_WARNING, Finding
from specmd.frontmatter import ParsedDocument, parse_document, strip_leading_numeral

RESULT_CONFORMING = "conforming"
RESULT_NON_CONFORMING = "non_conforming"
RESULT_INDETERMINATE = "indeterminate"

_REQUIREMENT_LINE_RE = re.compile(r"^\s*-\s+\*\*[A-Z][A-Z0-9-]*-\d+")
_MISCASED_KEYWORD_RE = re.compile(
    r"\b(Must Not|Must|Should Not|Should|May)\b(?!\s*[A-Z])"
)


@dataclass
class StructuralReport:
    doc: ParsedDocument
    effective_profile: str  # "core" | "optional"
    declared_core_version: str | None
    declared_optional_version: str | None
    declared_features: list[str]
    core_version_resolved: bool
    optional_version_resolved: bool | None
    findings: list[Finding] = field(default_factory=list)
    measurements: dict = field(default_factory=dict)


def make_finding(rule_id, severity, message, file, line=None, column=None) -> Finding:
    return Finding(
        rule_id=rule_id,
        severity=severity,
        message=message,
        evidence_type=EVIDENCE_DETERMINISTIC,
        file=file,
        line=line,
        column=column,
    )


# Backward-compatible private alias used internally in this module.
_finding = make_finding


def analyze(path: Path, requested_profile: str) -> StructuralReport:
    text = path.read_text(encoding="utf-8")
    doc = parse_document(str(path), text)
    findings: list[Finding] = []
    file_label = str(path)

    frontmatter = doc.frontmatter or {}

    if doc.frontmatter_error:
        findings.append(_finding("CORE-FRONTMATTER", SEVERITY_ERROR, doc.frontmatter_error, file_label, 1))

    declared_core_version = frontmatter.get("specmd") if isinstance(frontmatter, dict) else None
    declared_optional_version = frontmatter.get("specmd_optional") if isinstance(frontmatter, dict) else None
    declared_features_map = frontmatter.get("optional_features") if isinstance(frontmatter, dict) else None
    declared_features = list(declared_features_map.keys()) if isinstance(declared_features_map, dict) else []

    core_version_resolved = declared_core_version == core_profile.CORE_VERSION
    if declared_core_version is None:
        findings.append(_finding("CORE-VAL-006", SEVERITY_ERROR, "frontmatter is missing required field 'specmd'", file_label, 1))
    elif not core_version_resolved:
        findings.append(
            _finding(
                "CORE-VAL-006",
                SEVERITY_ERROR,
                f"declared Core version '{declared_core_version}' is not locally resolvable; "
                f"this build only has evidence for Core {core_profile.CORE_VERSION}",
                file_label,
                1,
            )
        )

    # VAL-012..017: profile resolution.
    has_optional_declaration = declared_optional_version is not None
    if requested_profile == "auto":
        effective_profile = "optional" if has_optional_declaration else "core"
    else:
        effective_profile = requested_profile

    optional_version_resolved: bool | None = None
    if effective_profile == "optional":
        if not has_optional_declaration:
            # VAL-016: explicit optional profile without a resolvable
            # specmd_optional declaration -> indeterminate.
            findings.append(
                _finding(
                    "CORE-VAL-016",
                    SEVERITY_ERROR,
                    "profile 'optional' was requested but frontmatter has no 'specmd_optional' declaration",
                    file_label,
                    1,
                )
            )
            optional_version_resolved = False
        else:
            optional_version_resolved = declared_optional_version == core_profile.OPTIONAL_VERSION
            if not optional_version_resolved:
                findings.append(
                    _finding(
                        "CORE-VAL-016",
                        SEVERITY_ERROR,
                        f"declared Optional version '{declared_optional_version}' is not locally resolvable; "
                        f"this build only has evidence for Optional {core_profile.OPTIONAL_VERSION}",
                        file_label,
                        1,
                    )
                )
            for feature in declared_features:
                if feature not in core_profile.RECOGNIZED_OPTIONAL_FEATURES:
                    # Optional 0.4.2 §44 frames optional_features as an open,
                    # extensible set ("Suggested... Example"), not a closed
                    # enum — an unlisted name is not itself a defect, only a
                    # feature this build has no dedicated structural checks
                    # for (VAL-017 still requires surfacing it, informationally).
                    findings.append(
                        _finding(
                            "CORE-VAL-017",
                            SEVERITY_INFORMATION,
                            f"optional_features declares '{feature}', which this build has no dedicated "
                            f"structural checks for (the Optional feature set is open-ended per SPEC.md "
                            f"Optional 0.4.2 §44 — this is not a defect)",
                            file_label,
                            1,
                        )
                    )

    # Frontmatter required-field checks for the effective profile.
    required_fields = list(core_profile.CORE_ONLY_REQUIRED_FRONTMATTER)
    if effective_profile == "optional":
        required_fields += list(core_profile.OPTIONAL_ADDITIONAL_REQUIRED_FRONTMATTER)
    for field_name in required_fields:
        if field_name == "specmd":
            continue  # already checked above with a more specific message
        if field_name not in frontmatter:
            findings.append(
                _finding("CORE-FRONTMATTER", SEVERITY_ERROR, f"frontmatter is missing required field '{field_name}'", file_label, 1)
            )
    if effective_profile == "optional" and isinstance(declared_features_map, dict) and len(declared_features_map) == 0:
        findings.append(
            _finding("CORE-INIT-015", SEVERITY_ERROR, "optional_features is present but empty; at least one feature is required", file_label, 1)
        )

    # Section sequence check.
    heading_texts = [strip_leading_numeral(h[1]) for h in doc.headings if h[0] <= 2]
    expected = [core_profile.LEADING_SECTION, *core_profile.REQUIRED_SECTIONS]
    idx = 0
    found_order: list[str] = []
    for text_heading in heading_texts:
        if idx < len(expected) and text_heading == expected[idx]:
            found_order.append(text_heading)
            idx += 1
    missing = expected[idx:]
    for section in missing:
        # Core §1 makes "Specification Contract" a SHOULD, and §2's "Empty
        # subsections MAY be omitted" was read, by product decision, as
        # permitting a genuinely-empty top-level section to be omitted too —
        # so a missing section is a warning, not a conformance error.
        findings.append(_finding("CORE-SECTIONS", SEVERITY_WARNING, f"required section '{section}' was not found (or is out of order)", file_label))

    # Human-only comment balance (SAFE-006).
    for issue in human_only.find_issues(text):
        findings.append(
            _finding(
                "SAFE-006",
                SEVERITY_ERROR,
                f"human-only comment block is malformed ({issue.kind})",
                file_label,
                issue.line,
            )
        )

    # BCP14 keyword casing on requirement statement lines only.
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not _REQUIREMENT_LINE_RE.match(line):
            continue
        for m in _MISCASED_KEYWORD_RE.finditer(line):
            findings.append(
                _finding(
                    "CORE-BCP14",
                    SEVERITY_WARNING,
                    f"normative keyword '{m.group(1)}' should be uppercase ('{m.group(1).upper()}')",
                    file_label,
                    lineno,
                    m.start() + 1,
                )
            )

    measurements = {
        "line_count": len(text.splitlines()),
        "estimated_token_count": _estimate_tokens(text),
    }

    return StructuralReport(
        doc=doc,
        effective_profile=effective_profile,
        declared_core_version=declared_core_version,
        declared_optional_version=declared_optional_version,
        declared_features=declared_features,
        core_version_resolved=core_version_resolved,
        optional_version_resolved=optional_version_resolved,
        findings=findings,
        measurements=measurements,
    )


def _estimate_tokens(text: str) -> int:
    # Lightweight whitespace/punctuation-based estimate; informational only
    # (INSP-005 permits an estimate).
    return len(re.findall(r"\S+", text))


def overall_result(report: StructuralReport) -> str:
    if report.declared_core_version is None or not report.core_version_resolved:
        return RESULT_INDETERMINATE
    if report.effective_profile == "optional" and report.optional_version_resolved is False:
        return RESULT_INDETERMINATE
    if any(f.severity == SEVERITY_ERROR for f in report.findings):
        return RESULT_NON_CONFORMING
    return RESULT_CONFORMING


def version_unresolved(report: StructuralReport) -> bool:
    """True when the declared exact standards version(s) could not be
    resolved — the trigger condition for the Version Alignment Process
    (SPEC.md section 4.14, PORT-006/007/008).
    """
    if report.declared_core_version is None or not report.core_version_resolved:
        return True
    if report.effective_profile == "optional" and report.optional_version_resolved is False:
        return True
    return False


def version_alignment_finding(report: StructuralReport, file_label: str) -> Finding | None:
    """PORT-006/007/008: when the exact declared standards version cannot be
    resolved, the operation must fail as indeterminate (PORT-007), and the
    *first suggested remediation* presented to the operator must be a
    proposed Specification Set version change (PORT-008) — never a silent
    substitution of a different resolved version (PORT-006). Returns a
    single finding carrying that remediation message, or None when the
    version is resolved.
    """
    if report.declared_core_version is None:
        return make_finding(
            "PORT-008",
            SEVERITY_ERROR,
            "No 'specmd' Core version is declared in this document's frontmatter, so no exact standards "
            "version can be resolved (PORT-006). Suggested first remediation: add "
            f"'specmd: \"{core_profile.CORE_VERSION}\"' (or whichever exact Core version this document "
            "actually conforms to) to the frontmatter as a Specification Set change, before any other "
            "workaround.",
            file_label,
            1,
        )
    if not report.core_version_resolved:
        return make_finding(
            "PORT-008",
            SEVERITY_ERROR,
            f"Declared Core version '{report.declared_core_version}' cannot be resolved in this build "
            f"(only Core {core_profile.CORE_VERSION} is available) (PORT-007). Suggested first remediation: "
            f"propose updating this document's declared 'specmd' version to '{core_profile.CORE_VERSION}' as "
            "a Specification Set change if that is an accurate reflection of intent, or supply/register the "
            f"exact Core {report.declared_core_version} standards document before re-running evaluation. Do "
            "not silently substitute a different resolved version (PORT-006).",
            file_label,
            1,
        )
    if (
        report.effective_profile == "optional"
        and report.optional_version_resolved is False
        and report.declared_optional_version
    ):
        return make_finding(
            "PORT-008",
            SEVERITY_ERROR,
            f"Declared Optional version '{report.declared_optional_version}' cannot be resolved in this "
            f"build (only Optional {core_profile.OPTIONAL_VERSION} is available) (PORT-007). Suggested first "
            f"remediation: propose updating this document's declared 'specmd_optional' version to "
            f"'{core_profile.OPTIONAL_VERSION}' as a Specification Set change if accurate, or supply/register "
            f"the exact Optional {report.declared_optional_version} standards document before re-running "
            "evaluation. Do not silently substitute a different resolved version (PORT-006).",
            file_label,
            1,
        )
    return None
