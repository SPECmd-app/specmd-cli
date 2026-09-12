"""Shared fenced-code-block handling.

Multiple deterministic checks (Normative Module resolution, requirement-ID
extraction, human-only comment detection) must not mistake a *documentation
example* inside a fenced code block for the real thing. This module gives
them one shared, tested way to do that instead of each re-implementing it
slightly differently.
"""

from __future__ import annotations

import re

_FENCE_LINE_RE = re.compile(r"^\s*```")
_CODE_FENCE_BLOCK_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)


def strip_code_fences(text: str) -> str:
    """Blank out the content of fenced code blocks (keeping the same number
    of lines, so line numbers elsewhere stay accurate) for scans that should
    ignore illustrative examples, such as heading or link detection.
    """
    return _CODE_FENCE_BLOCK_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def iter_lines_with_fence_state(text: str):
    """Yield (line_number, line, in_fence) for every line of text. in_fence
    is True for lines strictly between a pair of ``` fence markers — the
    fence marker lines themselves are reported with in_fence=False, since
    they never contain the content callers are scanning for.
    """
    in_fence = False
    for idx, line in enumerate(text.splitlines(), start=1):
        if _FENCE_LINE_RE.match(line):
            in_fence = not in_fence
            yield idx, line, False
            continue
        yield idx, line, in_fence
