"""`specmd standards list|show|verify` — local-only in this build.

`fetch` is not implemented (would require a canonical standards repository,
which SPEC.md Open Issue 1 leaves unresolved) and is not wired into the CLI
at all, rather than half-implemented.
"""

from __future__ import annotations

from pathlib import Path

from specmd import core_profile, exit_codes
from specmd.envelope import build_envelope
from specmd.frontmatter import parse_document

_SUPPORTED = {
    "core": core_profile.SUPPORTED_CORE_VERSIONS,
    "optional": core_profile.SUPPORTED_OPTIONAL_VERSIONS,
}
_LATEST = {
    "core": core_profile.CORE_VERSION,
    "optional": core_profile.OPTIONAL_VERSION,
}


def list_() -> tuple[dict, int]:
    versions = []
    for kind in ("core", "optional"):
        for v in _SUPPORTED[kind]:
            versions.append(
                {
                    "kind": kind,
                    "version": v,
                    "source": "bundled_local",
                    "channel": "stable",
                    "latest": v == _LATEST[kind],
                }
            )
    results = {"versions": versions, "note": core_profile.PROFILE_PROVENANCE}
    envelope = build_envelope(
        command="standards_list",
        status="succeeded",
        inputs={},
        results=results,
        findings=[],
        writes=[],
        cognitive_requested="off",
        cognitive_used="none",
        cognitive_complete=True,
    )
    return envelope, exit_codes.SUCCESS


def show(kind: str, version: str) -> tuple[dict, int]:
    if kind not in _SUPPORTED:
        envelope = build_envelope(
            command="standards_show",
            status="failed",
            inputs={"kind": kind, "version": version},
            results={"reason": f"unknown standards kind '{kind}'; expected 'core' or 'optional'"},
            findings=[],
            writes=[],
            cognitive_requested="off",
            cognitive_used="none",
            cognitive_complete=True,
        )
        return envelope, exit_codes.USAGE_ERROR

    resolved_version = _LATEST[kind] if version == "latest" else version
    # SRC-013: `latest` must resolve to and be reported as an exact version,
    # never left as the literal word "latest".
    if resolved_version not in _SUPPORTED[kind]:
        supported = ", ".join(_SUPPORTED[kind])
        envelope = build_envelope(
            command="standards_show",
            status="failed",
            inputs={"kind": kind, "version": version},
            results={"reason": f"exact {kind} version '{version}' is not available; only {supported} are bundled in this build"},
            findings=[],
            writes=[],
            cognitive_requested="off",
            cognitive_used="none",
            cognitive_complete=True,
        )
        return envelope, exit_codes.CAPABILITY_UNAVAILABLE

    if kind == "core":
        profile = {
            "required_frontmatter_core_only": list(core_profile.CORE_ONLY_REQUIRED_FRONTMATTER),
            "required_sections": [core_profile.LEADING_SECTION, *core_profile.REQUIRED_SECTIONS],
            "human_only_delimiters": [core_profile.HUMAN_ONLY_START, core_profile.HUMAN_ONLY_END],
            "bcp14_keywords": list(core_profile.BCP14_KEYWORDS),
        }
    else:
        profile = {
            "required_frontmatter_additional": list(core_profile.OPTIONAL_ADDITIONAL_REQUIRED_FRONTMATTER),
            "recognized_features": sorted(core_profile.RECOGNIZED_OPTIONAL_FEATURES),
        }

    results = {
        "kind": kind,
        "resolved_version": resolved_version,
        "is_latest": resolved_version == _LATEST[kind],
        "source": "bundled_local",
        "provenance": core_profile.PROFILE_PROVENANCE,
        "profile": profile,
    }
    envelope = build_envelope(
        command="standards_show",
        status="succeeded",
        inputs={"kind": kind, "version": version},
        results=results,
        findings=[],
        writes=[],
        cognitive_requested="off",
        cognitive_used="none",
        cognitive_complete=True,
    )
    return envelope, exit_codes.SUCCESS


def verify(core_document: Path | None, optional_document: Path | None) -> tuple[dict, int]:
    checks = []
    all_ok = True
    for label, path, field in (("core", core_document, "specmd"), ("optional", optional_document, "specmd_optional")):
        if path is None:
            continue
        if not path.exists():
            checks.append({"kind": label, "path": str(path), "ok": False, "reason": "file does not exist"})
            all_ok = False
            continue
        doc = parse_document(str(path), path.read_text(encoding="utf-8"))
        if doc.frontmatter_error:
            checks.append({"kind": label, "path": str(path), "ok": False, "reason": doc.frontmatter_error})
            all_ok = False
            continue
        declared = (doc.frontmatter or {}).get(field)
        matches_bundled = declared in _SUPPORTED[label]
        checks.append(
            {
                "kind": label,
                "path": str(path),
                "ok": matches_bundled,
                "declared_version": declared,
                "bundled_versions": list(_SUPPORTED[label]),
                "reason": None if matches_bundled else f"declared '{declared}' is not among bundled versions {list(_SUPPORTED[label])}",
            }
        )
        all_ok = all_ok and matches_bundled

    if not checks:
        results = {"checks": [], "reason": "no --core-document or --optional-document supplied"}
        status = "failed"
        exit_code = exit_codes.USAGE_ERROR
    else:
        results = {"checks": checks}
        status = "succeeded" if all_ok else "findings"
        exit_code = exit_codes.SUCCESS if all_ok else exit_codes.FINDINGS

    envelope = build_envelope(
        command="standards_verify",
        status=status,
        inputs={
            "core_document": str(core_document) if core_document else None,
            "optional_document": str(optional_document) if optional_document else None,
        },
        results=results,
        findings=[],
        writes=[],
        cognitive_requested="off",
        cognitive_used="none",
        cognitive_complete=True,
    )
    return envelope, exit_code
