"""Cognitive mode negotiation — Deterministic-Only Mode only (no Cognitive
Provider or Reviewer Agent is implemented in this MVP). See
SPECMD_AGENT_INTEGRATIONS.md COG-002/003/009 and SPECMD_CLI_ICD.md
section 7 / ICD-COG-001..003.
"""

from __future__ import annotations

from dataclasses import dataclass

from specmd import exit_codes

OFF = "off"
AUTO = "auto"
REQUIRED = "required"

VALID_MODES = (OFF, AUTO, REQUIRED)


@dataclass
class CognitiveResult:
    requested: str
    used: str  # always "none" in this build — no provider exists
    complete: bool
    exit_override: int | None = None
    message: str | None = None


def negotiate(requested: str) -> CognitiveResult:
    """No Cognitive Provider is configured in this build (Deterministic-Only
    Mode is the only supported mode). Report that truthfully rather than
    silently proceeding as if semantic analysis had run.
    """
    if requested == OFF:
        # COG-002: structural validation must support Deterministic-Only
        # Mode; nothing was requested, so nothing is owed.
        return CognitiveResult(requested=OFF, used="none", complete=True)

    if requested == AUTO:
        # ICD-COG table: auto uses an available configured mode, otherwise
        # completes deterministic work and reports the omission (COG-003).
        return CognitiveResult(
            requested=AUTO,
            used="none",
            complete=False,
            message=(
                "No Cognitive Provider is configured in this build; semantic "
                "ambiguity, contradiction, completeness, and portability "
                "analysis was not performed. Deterministic results only."
            ),
        )

    if requested == REQUIRED:
        # COG-009 / ICD-COG table: required-but-unavailable must preserve
        # deterministic results and return exit status 4 for the affected
        # semantic result.
        return CognitiveResult(
            requested=REQUIRED,
            used="none",
            complete=False,
            exit_override=exit_codes.CAPABILITY_UNAVAILABLE,
            message=(
                "Cognitive mode 'required' was requested but no Cognitive "
                "Provider is configured in this build. Deterministic results "
                "are preserved; the semantic result is indeterminate."
            ),
        )

    raise ValueError(f"unknown cognitive mode: {requested!r}")
