"""YAML frontmatter extraction and ATX heading scan for a SPEC.md-like
Markdown document.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import yaml

_FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


@dataclass
class ParsedDocument:
    path: str
    text: str
    frontmatter: dict | None
    frontmatter_error: str | None
    body: str
    body_offset_lines: int  # number of lines consumed by the frontmatter block
    headings: list[tuple[int, str, int]]  # (level, text, line_number)


def parse_document(path: str, text: str) -> ParsedDocument:
    match = _FRONTMATTER_RE.match(text)
    frontmatter: dict | None = None
    frontmatter_error: str | None = None
    body = text
    body_offset_lines = 0

    if not match:
        frontmatter_error = "no YAML frontmatter block found at start of document"
    else:
        raw = match.group(1)
        body = text[match.end():]
        body_offset_lines = text[: match.end()].count("\n")
        try:
            loaded = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            frontmatter_error = f"frontmatter is not valid YAML: {exc}"
        else:
            if loaded is None:
                frontmatter = {}
            elif isinstance(loaded, dict):
                frontmatter = loaded
            else:
                frontmatter_error = "frontmatter must be a YAML mapping"

    headings: list[tuple[int, str, int]] = []
    for idx, line in enumerate(body.splitlines(), start=1):
        m = _HEADING_RE.match(line)
        if m:
            headings.append((len(m.group(1)), m.group(2).strip(), idx + body_offset_lines))

    return ParsedDocument(
        path=path,
        text=text,
        frontmatter=frontmatter,
        frontmatter_error=frontmatter_error,
        body=body,
        body_offset_lines=body_offset_lines,
        headings=headings,
    )


def strip_leading_numeral(heading_text: str) -> str:
    """"1. Overview and Scope" -> "Overview and Scope"; "1.5 Foo" -> "Foo"."""
    return re.sub(r"^\d+(\.\d+)*\.?\s+", "", heading_text).strip()
