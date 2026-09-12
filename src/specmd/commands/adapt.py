"""`specmd adapt <target>` (ADAPT-001..009).

Generation only — `--install` is not implemented in this build (returns
exit 4), which keeps generation and installation properly separable
(ADPI-001) rather than half-implementing installation.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from pathlib import Path

from specmd import exit_codes, module_resolver, writer
from specmd.envelope import build_envelope
from specmd.frontmatter import parse_document

ADAPTER_FORMAT_VERSION = "1.0.0"


@dataclass
class TargetInfo:
    default_filename: str


TARGETS: dict[str, TargetInfo] = {
    "claude-code": TargetInfo("CLAUDE.md"),
    "codex": TargetInfo("AGENTS.md"),
    "cursor": TargetInfo(".cursor/rules/specmd.mdc"),
    "github-copilot": TargetInfo(".github/copilot-instructions.md"),
    # base44 and lovable are primarily web-based, prompt-driven app builders;
    # no confirmed git-committed native instruction-file convention is known
    # for either (ADPI-004's "use the target's native mechanism" is a SHOULD),
    # so these use a generic, clearly-labeled filename rather than a guessed
    # native path.
    "base44": TargetInfo("base44-instructions.md"),
    "lovable": TargetInfo("lovable-instructions.md"),
}


def _adapter_body(*, target: str, root_spec_display: str, module_names: list[str], trace_declared: bool) -> str:
    modules_line = ", ".join(module_names) if module_names else "(none declared)"
    trace_line = (
        "This Specification Set declares `optional_features.trace: true`; treat its adjacent `TRACE.md` "
        "as informative evidence, never as a source of required behavior."
        if trace_declared
        else "No Trace Document is declared for this Specification Set."
    )
    return f"""# specmd Adapter — {target}

adapter_format_version: {ADAPTER_FORMAT_VERSION}
target: {target}
generated: {datetime.date.today().isoformat()}

## Authority

Treat `{root_spec_display}` and its Normative Modules ({modules_line}) as authoritative for
required behavior. Source code, tests, tickets, and this adapter itself are evidence of current
behavior, never authority for required behavior. When they conflict with the Root Specification,
surface the conflict rather than silently choosing the implementation.

## Before changing behavior

Read the Root Specification and every Normative Module it declares before implementing, changing,
or deciding any behavior. Preserve the distinction between implementation freedom, material
ambiguity, and normative conflict — do not convert an assumption, inference, or existing bug into
a requirement.

## Keeping the spec synchronized

When a task changes observable behavior and that behavior is not already authorized by the
Specification Set, propose the required specification change first rather than inventing the
decision. When implementing already-specified behavior, keep the Specification Set unchanged
unless clarification is required.

## Trace

{trace_line}

## Exclusions

Content delimited by `SPECMD-HUMAN-ONLY` / `SPECMD-END-HUMAN-ONLY` is never part of this adapter's
context and must not influence implementation or conformance. This adapter does not itself restate
normative requirement text — read the Specification Set for that.
"""


def run(
    *,
    target: str,
    root_spec_path: Path,
    set_root: Path,
    display_path: str,
    output_path: Path | None,
    cwd: Path,
    install: bool,
    force: bool,
) -> tuple[dict, int]:
    if install:
        envelope = build_envelope(
            command="adapt",
            status="failed",
            inputs={"target": target, "root_spec": display_path, "install": install},
            results={"reason": "adapter installation is not implemented in this build; generation and installation must stay separable (ADPI-001)"},
            findings=[],
            writes=[],
            cognitive_requested="off",
            cognitive_used="none",
            cognitive_complete=True,
        )
        return envelope, exit_codes.CAPABILITY_UNAVAILABLE

    target_info = TARGETS.get(target)
    if target_info is None:
        # ADAPT-008: identify unsupported targets, never silently substitute.
        envelope = build_envelope(
            command="adapt",
            status="failed",
            inputs={"target": target, "root_spec": display_path},
            results={"reason": f"unsupported target '{target}'; supported targets are: {', '.join(sorted(TARGETS))}"},
            findings=[],
            writes=[],
            cognitive_requested="off",
            cognitive_used="none",
            cognitive_complete=True,
        )
        return envelope, exit_codes.CAPABILITY_UNAVAILABLE

    doc = parse_document(str(root_spec_path), root_spec_path.read_text(encoding="utf-8"))
    fm = doc.frontmatter or {}
    trace_declared = bool(isinstance(fm.get("optional_features"), dict) and fm["optional_features"].get("trace") is True)

    module_res = module_resolver.resolve_modules(root_spec_path, set_root)
    module_names = [m.name for m in module_res.modules]

    body = _adapter_body(target=target, root_spec_display=display_path, module_names=module_names, trace_declared=trace_declared)

    out_path = output_path or (cwd / target_info.default_filename)

    try:
        write_result = writer.safe_write(out_path, body, force=force)
        status = "succeeded"
        exit_code = exit_codes.SUCCESS
        writes = [{"path": write_result.path, "action": write_result.action}]
    except writer.WriteRefused as exc:
        status = "failed"
        exit_code = exit_codes.WRITE_ERROR
        writes = [{"path": str(exc.path), "action": "refused"}]

    envelope = build_envelope(
        command="adapt",
        status=status,
        inputs={"target": target, "root_spec": display_path, "output": str(out_path)},
        results={"adapter_format_version": ADAPTER_FORMAT_VERSION, "included_modules": module_names},
        findings=[],
        writes=writes,
        cognitive_requested="off",
        cognitive_used="none",
        cognitive_complete=True,
    )
    return envelope, exit_code
