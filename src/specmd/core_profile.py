"""Reconstructed SPEC.md Core 0.4.2 / Optional 0.4.2 structural profile.

IMPORTANT PROVENANCE NOTE: the specmd Specification Set this tool implements
(SPEC.md, formerly SPECMD_TOOL_SPEC.md) describes specmd's *own* required
behavior — it declares that it conforms to Core 0.4.2 / Optional 0.4.2, but
the package that shipped it did not include the Core/Optional standard
documents themselves. No authoritative Core 0.4.2 text was available to this
build.

The structural rules below were reconstructed from the only evidence
available: the shape SPEC.md itself uses (its own frontmatter fields, its
own eight numbered top-level sections, the human-only delimiter syntax it
defines in its Context and Definitions section, and its BCP14 keyword
usage). This is a single exemplar, not the authoritative standard text, and
this profile may diverge from the real Core 0.4.2 / Optional 0.4.2 rules in
ways this build cannot detect (exact frontmatter typing rules, exact
keyword-usage checks beyond presence/casing, section-numbering flexibility,
etc.).

This is intentionally isolated in one module so the real Core/Optional
documents can replace this reconstruction later without changing the rest
of the validate/inspect/init engine. Every result that depends on this
profile must say so explicitly (see PROFILE_PROVENANCE below).
"""

from __future__ import annotations

CORE_VERSION = "0.4.2"
OPTIONAL_VERSION = "0.4.2"

# The trace-format version (`specmd_trace` frontmatter field) is likewise
# not defined by any authoritative document provided to this build. Reused
# from the one exemplar TRACE.md shipped in the reviewed package, same
# provenance caveat as the rest of this module.
TRACE_FORMAT_VERSION = "0.4.0"

PROFILE_PROVENANCE = (
    "reconstructed from SPEC.md's own structural usage; not the "
    "authoritative SPEC.md Core/Optional 0.4.2 standard text, which was "
    "not provided to this build"
)

CORE_ONLY_REQUIRED_FRONTMATTER = ("specmd", "spec_version", "status", "name", "last_updated")
OPTIONAL_ADDITIONAL_REQUIRED_FRONTMATTER = ("specmd_optional", "optional_features")

# Required section sequence, in order. Matched case-sensitively against the
# heading text following any leading numeral/period (e.g. "1. Overview and
# Scope" or "Overview and Scope" both match "Overview and Scope").
LEADING_SECTION = "Specification Contract"
REQUIRED_SECTIONS = (
    "Overview and Scope",
    "Context and Definitions",
    "System Model",
    "Requirements",
    "Interfaces and External Contracts",
    "Constraints and Non-Goals",
    "Verification and Acceptance",
    "Notes and Rationale",
)

# Feature names observed in SPEC.md's own optional_features declaration —
# the only evidence available for what the real Optional 0.4.2 standard
# defines. Same provenance caveat as the rest of this module.
RECOGNIZED_OPTIONAL_FEATURES = frozenset(
    {
        "requirement_metadata",
        "advanced_modularization",
        "diagrams",
        "composed_verification",
        "human_only_processing",
        "trace",
    }
)

HUMAN_ONLY_START = "SPECMD-HUMAN-ONLY"
HUMAN_ONLY_END = "SPECMD-END-HUMAN-ONLY"

BCP14_KEYWORDS = ("MUST NOT", "MUST", "SHOULD NOT", "SHOULD", "MAY")

# Core compactness target (INV-003/004, INSP-005/006/007): applies only when
# the analyzed document identifies itself AS SPEC.md Core (i.e. it IS the
# Core standard artifact), never to a project/design specification that
# merely declares a `specmd` version. No document this tool processes in
# the MVP is the Core standard itself, so this target is carried here only
# for completeness and is not expected to trigger.
CORE_COMPACTNESS_MAX_LINES = 250
CORE_COMPACTNESS_MAX_TOKENS = 2500
