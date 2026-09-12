"""SPEC.md Core 0.4.2/0.4.3 and Optional 0.4.2/0.4.3 structural profile.

VERSION NOTE: 0.4.3 was added after being diffed directly against 0.4.2's
authoritative text and confirmed to be a pure editorial PATCH release (no
normative behavioral difference — Core §12's own PATCH test). Both versions
resolve to the same structural profile below; SUPPORTED_CORE_VERSIONS and
SUPPORTED_OPTIONAL_VERSIONS list every version this build actually verified
this way, not just the latest.

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

# CORE_VERSION/OPTIONAL_VERSION are the *latest* version this build creates
# new documents with (init, trace create --enable-optional). For *resolving*
# an existing document's declared version, see SUPPORTED_CORE_VERSIONS below
# — 0.4.2 remains a first-class, fully resolvable version, not merely
# tolerated: 0.4.3 is a confirmed PATCH release (verified by diffing the
# authoritative texts directly — no normative behavioral difference,
# consistent with Core §12's own PATCH test), so a document declaring 0.4.2
# is exactly as conforming as one declaring 0.4.3, just older wording.
CORE_VERSION = "0.4.3"
OPTIONAL_VERSION = "0.4.3"
SUPPORTED_CORE_VERSIONS = ("0.4.2", "0.4.3")
SUPPORTED_OPTIONAL_VERSIONS = ("0.4.2", "0.4.3")

# 0.4.3's actual content change: it adds explicit text confirming this
# build's FLW-*/Behavioral-Flow-ID trace-coverage exclusion decision (see
# FLOW_ID_PREFIXES below) — "An ID alone does not make an element
# normative... TRACE coverage follows normative obligations, not every
# label in the document" (Core 0.4.3, after §7; near-identical text in
# Optional 0.4.3). That decision was reached independently, from the same
# System Model/Requirements structural evidence available in 0.4.2, and
# 0.4.3 confirms it explicitly rather than changing it.
CORE_SOURCE_URL = "https://github.com/SPECmd-app/SPEC.md/blob/main/docs/standard/0.4.3.md"
OPTIONAL_SOURCE_URL = "https://github.com/SPECmd-app/SPEC.md/blob/main/docs/standard/0.4.3-optional.md"

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
    f"reconciled against the authoritative SPEC.md Core standard ({CORE_SOURCE_URL}) and "
    f"Optional standard ({OPTIONAL_SOURCE_URL}); supports Core/Optional versions "
    f"{', '.join(SUPPORTED_CORE_VERSIONS)} (0.4.3 verified by direct diff against 0.4.2 as a "
    "pure editorial PATCH — no behavioral difference); one figure (the Core compactness "
    "target) remains unconfirmed by that text — see CORE_COMPACTNESS_PROVENANCE"
)

CORE_COMPACTNESS_PROVENANCE = (
    "the 250-line/2,500-token figures appear nowhere in the authoritative Core or Optional "
    "text, or on the standard's own site; they came from this tool's own governing spec "
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
