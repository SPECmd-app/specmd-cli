"""SPECMD-HUMAN-ONLY / SPECMD-END-HUMAN-ONLY handling (INV-006, SAFE-006)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from specmd.code_fences import iter_lines_with_fence_state
from specmd.core_profile import HUMAN_ONLY_END, HUMAN_ONLY_START

_FENCE_LINE_RE = re.compile(r"^\s*```")


@dataclass
class HumanOnlyIssue:
    kind: str  # "unclosed_start" | "unmatched_end"
    line: int


def find_issues(text: str) -> list[HumanOnlyIssue]:
    """Detect malformed/unclosed human-only comment blocks (SAFE-006).

    Markers inside a fenced code block (e.g. a documentation example
    illustrating the human-only syntax itself) are inert — they are not
    real directives and must not be reported as malformed.
    """
    issues: list[HumanOnlyIssue] = []
    depth = 0
    open_line = None
    for idx, line, in_fence in iter_lines_with_fence_state(text):
        if in_fence:
            continue
        if HUMAN_ONLY_START in line:
            if depth == 0:
                open_line = idx
            depth += 1
        if HUMAN_ONLY_END in line:
            if depth == 0:
                issues.append(HumanOnlyIssue(kind="unmatched_end", line=idx))
            else:
                depth -= 1
    if depth > 0 and open_line is not None:
        issues.append(HumanOnlyIssue(kind="unclosed_start", line=open_line))
    return issues


def strip_human_only(text: str) -> str:
    """Remove every well-formed human-only block. Malformed blocks are left
    for the caller to have already reported via find_issues(); this function
    only handles the well-formed case safely (best-effort strip up to the
    last matching end marker).

    Assumes each delimiter appears on its own line, which is the block-comment
    style used throughout SPEC.md; delimiters embedded mid-line are not
    supported by this MVP implementation. Lines inside a fenced code block are
    always preserved verbatim — a documentation example that merely shows the
    human-only syntax is not itself human-only content (INV-006 excludes real
    editorial notes, not illustrations of the mechanism).
    """
    out: list[str] = []
    depth = 0
    in_fence = False
    for line in text.splitlines(keepends=True):
        if _FENCE_LINE_RE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        starts = line.count(HUMAN_ONLY_START)
        ends = line.count(HUMAN_ONLY_END)
        if depth == 0 and starts == 0:
            out.append(line)
            continue
        # Line participates in a human-only block boundary; drop it and any
        # fully-enclosed lines.
        depth += starts
        depth -= ends
        if depth < 0:
            depth = 0
    return "".join(out)
