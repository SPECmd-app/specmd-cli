"""Single-source command/capability registry, shared by `capabilities` and
`help` (ICD-HELP-002: help must be generated from/verified against the same
metadata capability discovery uses). Includes commands not implemented in
this build so both surfaces disclose them honestly as unavailable, rather
than silently omitting them.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OptionInfo:
    name: str
    default: str = ""
    description: str = ""


@dataclass
class CommandInfo:
    name: str  # e.g. "validate", "trace create"
    summary: str
    read_only: bool
    writes: bool
    network: bool
    executes_code: bool
    available: bool
    unavailable_reason: str = ""
    options: list[OptionInfo] = field(default_factory=list)
    exit_statuses: str = "0 success, 2 usage error, 3 input error, 5 write error"


COMMANDS: list[CommandInfo] = [
    CommandInfo(
        name="init",
        summary="Create the smallest useful starting SPEC.md.",
        read_only=False,
        writes=True,
        network=False,
        executes_code=False,
        available=True,
        options=[
            OptionInfo("--profile", "core", "core or optional"),
            OptionInfo("--feature", "", "repeatable, optional profile only"),
            OptionInfo("--force", "off", "authorize overwriting an existing destination"),
        ],
    ),
    CommandInfo(
        name="validate",
        summary="Structural conformance check plus Trace Pair validation.",
        read_only=True,
        writes=False,
        network=False,
        executes_code=False,
        available=True,
        options=[
            OptionInfo("--profile", "auto", "auto, core, or optional"),
            OptionInfo("--trace", "auto", "auto, none, or an explicit path"),
            OptionInfo("--cognitive", "off", "off, auto, or required (no provider configured in this build)"),
            OptionInfo("--strict", "off", "promote warnings to a non-successful result"),
        ],
    ),
    CommandInfo(
        name="inspect",
        summary="Read-only quality/measurement report.",
        read_only=True,
        writes=False,
        network=False,
        executes_code=False,
        available=True,
        options=[
            OptionInfo("--profile", "auto"),
            OptionInfo("--trace", "auto"),
            OptionInfo("--cognitive", "auto"),
        ],
    ),
    CommandInfo(
        name="render",
        summary="Render the Specification Set to HTML (PDF not implemented).",
        read_only=False,
        writes=True,
        network=False,
        executes_code=False,
        available=True,
        options=[
            OptionInfo("--render-format", "html", "html available; pdf returns exit 4"),
            OptionInfo("--output", "<input>.html"),
            OptionInfo("--include-human-only", "off", "editorial mode only"),
            OptionInfo("--force", "off"),
        ],
    ),
    CommandInfo(
        name="trace create",
        summary="Generate TRACE.md from the resolved Specification Set.",
        read_only=False,
        writes=True,
        network=False,
        executes_code=False,
        available=True,
        options=[
            OptionInfo("--output", "TRACE.md beside the Root Specification"),
            OptionInfo("--enable-optional", "off", "authorize adding optional_features.trace + version bump"),
            OptionInfo("--force", "off"),
        ],
    ),
    CommandInfo(
        name="trace update",
        summary="Reconcile an existing TRACE.md with the current Specification Set.",
        read_only=False,
        writes=True,
        network=False,
        executes_code=False,
        available=True,
        options=[OptionInfo("--trace", "TRACE.md beside the Root Specification"), OptionInfo("--force", "off")],
    ),
    CommandInfo(
        name="blackbox",
        summary="Read-only, outside-in Black-Box Contract analysis.",
        read_only=True,
        writes=False,
        network=False,
        executes_code=False,
        available=True,
        options=[OptionInfo("--trace", "auto"), OptionInfo("--export", "", "write a JSON report to this path")],
    ),
    CommandInfo(
        name="test",
        summary="Verification-coverage report; does not execute code by default.",
        read_only=True,
        writes=False,
        network=False,
        executes_code=False,
        available=True,
        options=[
            OptionInfo("--trace", "auto"),
            OptionInfo("--export", "", "write a JSON test plan to this path"),
            OptionInfo("--run-integration", "", "not implemented in this build; returns exit 4"),
        ],
    ),
    CommandInfo(
        name="adapt",
        summary="Generate a thin adapter for a supported External Tool (generation only).",
        read_only=False,
        writes=True,
        network=False,
        executes_code=False,
        available=True,
        options=[
            OptionInfo("<target>", "", "codex, claude-code, cursor, github-copilot, base44, or lovable"),
            OptionInfo("--output", "target's conventional default path"),
            OptionInfo("--install", "", "not implemented in this build; returns exit 4"),
            OptionInfo("--force", "off"),
        ],
    ),
    CommandInfo(
        name="standards list",
        summary="List bundled/local standards versions (no network in this build).",
        read_only=True,
        writes=False,
        network=False,
        executes_code=False,
        available=True,
    ),
    CommandInfo(
        name="standards show",
        summary="Display one bundled/local standards version's structural profile.",
        read_only=True,
        writes=False,
        network=False,
        executes_code=False,
        available=True,
    ),
    CommandInfo(
        name="standards verify",
        summary="Verify an explicit local Core/Optional document against bundled records.",
        read_only=True,
        writes=False,
        network=False,
        executes_code=False,
        available=True,
    ),
    CommandInfo(
        name="standards fetch",
        summary="Retrieve exact standards artifacts from a repository.",
        read_only=False,
        writes=True,
        network=True,
        executes_code=False,
        available=False,
        unavailable_reason=(
            "Not implemented in this build: no canonical standards repository is defined yet "
            "(SPEC.md Open Issue 1 is unresolved)."
        ),
    ),
    CommandInfo(
        name="capabilities",
        summary="Report tool version, supported standards, commands, and available integrations.",
        read_only=True,
        writes=False,
        network=False,
        executes_code=False,
        available=True,
    ),
    CommandInfo(
        name="help",
        summary="Self-contained command help; works offline with no Specification Set.",
        read_only=True,
        writes=False,
        network=False,
        executes_code=False,
        available=True,
        options=[OptionInfo("--search", "", "filter by substring"), OptionInfo("--all", "off", "include unavailable capabilities")],
    ),
    CommandInfo(
        name="cucumber export",
        summary="Derive reviewable Gherkin from explicit acceptance behavior.",
        read_only=True,
        writes=True,
        network=False,
        executes_code=False,
        available=False,
        unavailable_reason="Cucumber connector not implemented in this build.",
    ),
    CommandInfo(
        name="cucumber validate",
        summary="Check Gherkin syntax without executing scenario bodies.",
        read_only=True,
        writes=False,
        network=False,
        executes_code=False,
        available=False,
        unavailable_reason="Cucumber connector not implemented in this build.",
    ),
    CommandInfo(
        name="cucumber run",
        summary="Execute a configured external Cucumber runtime.",
        read_only=False,
        writes=True,
        network=False,
        executes_code=True,
        available=False,
        unavailable_reason="Cucumber connector not implemented in this build.",
    ),
    CommandInfo(
        name="cucumber import",
        summary="Normalize a Cucumber execution report; optionally update TRACE.md evidence.",
        read_only=True,
        writes=True,
        network=False,
        executes_code=False,
        available=False,
        unavailable_reason="Cucumber connector not implemented in this build.",
    ),
]


def find(name: str) -> CommandInfo | None:
    for cmd in COMMANDS:
        if cmd.name == name:
            return cmd
    return None
