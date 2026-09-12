"""SPEC.md Core 0.4.2 / Optional 0.4.2 structural profile.

RECONCILIATION NOTE: this profile was originally *reconstructed* from a
single exemplar (this tool's own SPEC.md), because the package that shipped
this project's Specification Set did not include the authoritative
Core/Optional standard text. That gap has since been closed: the real
standard was located, published at
https://github.com/SPECmd-app/SPEC.md (docs/standard/0.4.2.md and
0.4.2-optional.md), and this module has been reconciled against that text.

Differences found and fixed during reconciliation:
- "Specification Contract" is a SHOULD (Core §1: "A SPEC.md SHOULD begin
  with..."), not a MUST — its absence is a warning, not an error.
- The eight Core-structure sections (Core §2) are followed immediately by
  "Empty subsections MAY be omitted." Read literally, a genuinely-empty
  top-level section MAY be omitted too — by explicit product decision, a
  missing required section is now a warning, not a conformance error, so a
  document that legitimately omits an inapplicable section can still be
  `conforming`.
- Optional §44 explicitly frames `optional_features` as a "Suggested...
  Example," not a closed enum, and its own example includes `ears` and
  `tasks` (which this build's original reconstruction lacked) while lacking
  `human_only_processing` (which this build's original reconstruction
  invented from its own SPEC.md's usage). The feature set is open per the
  standard: an unlisted feature name is not itself a defect, so this is now
  reported as informational, not a warning.
- The `250 lines` / `2,500 tokens` Core compactness figures do not appear
  anywhere in the authoritative Core or Optional text, or on the standard's
  own site — they came from this *tool's* own governing spec prose, not
  from the Core standard itself. Kept (still plausibly accurate) but
  explicitly flagged as unconfirmed by the authoritative source, distinct
  from the rest of this now-reconciled module.

Everything else in the original reconstruction (frontmatter field names,
the eight section titles, the human-only delimiter syntax, the BCP14
keyword set, and the "Normative Specification Modules" heading text) was
checked directly against the authoritative text and confirmed correct.

Every result that depends on this profile continues to cite its source (see
PROFILE_PROVENANCE / CORE_SOURCE_URL / OPTIONAL_SOURCE_URL below) so a
reader can verify the claim rather than take it on faith.
"""

from __future__ import annotations

CORE_VERSION = "0.4.2"
OPTIONAL_VERSION = "0.4.2"

CORE_SOURCE_URL = "https://github.com/SPECmd-app/SPEC.md/blob/main/docs/standard/0.4.2.md"
OPTIONAL_SOURCE_URL = "https://github.com/SPECmd-app/SPEC.md/blob/main/docs/standard/0.4.2-optional.md"

# The trace-format version (`specmd_trace` frontmatter field) and the
# TRACE.md binding contract (traces_file/traces_spec exact-version pairing,
# TRACE-001..017) are this *tool's* own elaboration, not defined by the
# authoritative Optional standard — Optional §28 describes TRACE.md only as
# a simple, frontmatter-free 4-column table. Optional §0 permits adding more
# structure than Core/Optional require ("Optional conventions MUST NOT
# weaken, replace, or silently reinterpret Core requirements" — adding
# rigor is not weakening), so this remains this tool's legitimate design
# choice, just not something reconciliation could confirm or refute against
# the standard itself.
TRACE_FORMAT_VERSION = "0.4.0"

PROFILE_PROVENANCE = (
    f"reconciled against the authoritative SPEC.md Core {CORE_VERSION} standard "
    f"({CORE_SOURCE_URL}) and Optional {OPTIONAL_VERSION} standard ({OPTIONAL_SOURCE_URL}); "
    "one figure (the Core compactness target) remains unconfirmed by that text — see "
    "CORE_COMPACTNESS_PROVENANCE"
)

CORE_COMPACTNESS_PROVENANCE = (
    "the 250-line/2,500-token figures appear nowhere in the authoritative Core or Optional "
    "0.4.2 text, or on the standard's own site; they came from this tool's own governing spec "
    "prose and remain unconfirmed against the authoritative standard"
)

CORE_ONLY_REQUIRED_FRONTMATTER = ("specmd", "spec_version", "status", "name", "last_updated")
OPTIONAL_ADDITIONAL_REQUIRED_FRONTMATTER = ("specmd_optional", "optional_features")

# Required section sequence, in order (Core §2). Matched case-sensitively
# against the heading text following any leading numeral/period (e.g. "1.
# Overview and Scope" or "Overview and Scope" both match "Overview and
# Scope"). Confirmed against the authoritative text.
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

# Flow identifiers (e.g. `FLW-001`) are a distinct category from requirement
# IDs, not a subset of them, per the authoritative standard itself: Core
# §5 "System Model" lists "behavioral flows" separately from §6
# "Requirements" (where stable IDs are recommended, with example prefixes
# FUN/DATA/AUTH/SEC/INT — none flow-shaped), and Optional Appendix C's
# example trace chain treats "Flow" as its own layer between Requirement
# and Design/Task/Implementation/Verification, not something folded into
# requirement-ID trace coverage. TRACE-007 ("every current normative
# requirement ID and invariant ID") therefore does not apply to these —
# excluded here, not merely undetected, so the exclusion is explicit and
# auditable rather than accidental. See ids.extract_flow_ids.
FLOW_ID_PREFIXES = frozenset({"FLW"})

# Optional §44's own illustrative example plus this tool's own legitimate
# usage (optional_features is confirmed OPEN/extensible per the standard,
# not a closed enum — see the module docstring). This set exists only to
# say which feature names this *build* has any dedicated structural
# handling for; a name outside it is not a defect.
RECOGNIZED_OPTIONAL_FEATURES = frozenset(
    {
        "requirement_metadata",
        "ears",
        "advanced_modularization",
        "diagrams",
        "composed_verification",
        "tasks",
        "trace",
        "human_only_processing",
    }
)

HUMAN_ONLY_START = "SPECMD-HUMAN-ONLY"
HUMAN_ONLY_END = "SPECMD-END-HUMAN-ONLY"

BCP14_KEYWORDS = ("MUST NOT", "MUST", "SHOULD NOT", "SHOULD", "MAY")

# Core compactness target — see CORE_COMPACTNESS_PROVENANCE above. Applies
# only when the analyzed document identifies itself AS SPEC.md Core (i.e.
# it IS the Core standard artifact), never to a project/design
# specification that merely declares a `specmd` version.
CORE_COMPACTNESS_MAX_LINES = 250
CORE_COMPACTNESS_MAX_TOKENS = 2500
