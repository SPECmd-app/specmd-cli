"""Normative Specification Modules link resolution (VAL-010/011, SPEC.md
section 5.6): parses relative module declarations out of a "Normative
Specification Modules" section, resolves them relative to the referencing
document, and detects cycles, duplicates, and paths escaping the
Specification Set root.

Recognizes two declaration syntaxes, both confirmed against the
authoritative SPEC.md Optional 0.4.2 standard (§10 "Advanced Specification
Set Organization"): a real Markdown link (`- [text](path)`, the convention
this tool's own SPEC.md uses) and the standard's own illustrated bare
backtick-quoted path (`` - `spec/identity.md` `` — no link syntax at all).
A resolver that only understood the first form would silently miss modules
declared the standard's own documented way.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from specmd.code_fences import strip_code_fences

# Tolerate an optional leading numeral prefix on the heading (e.g.
# "### 1.5 Normative Specification Modules"), matching how section headings
# are numbered elsewhere in SPEC.md.
_SECTION_HEADING_RE = re.compile(r"^#{1,6}\s+(?:\d+(?:\.\d+)*\.?\s+)?Normative Specification Modules\s*$", re.MULTILINE)
_NEXT_HEADING_RE = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)
_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
# Optional §10's own convention: a bullet list item that is nothing but a
# backtick-quoted path. Required to look path-like (ends in a file
# extension) to avoid matching unrelated inline-code bullets.
_BACKTICK_PATH_RE = re.compile(r"^\s*-\s+`([^`\s]+\.[A-Za-z0-9]+)`\s*$", re.MULTILINE)


@dataclass
class ModuleResolution:
    root_path: Path
    set_root: Path
    modules: list[Path] = field(default_factory=list)
    duplicates: list[Path] = field(default_factory=list)
    escaped: list[str] = field(default_factory=list)
    cycles: list[str] = field(default_factory=list)
    unreadable: list[tuple[Path, str]] = field(default_factory=list)


def extract_declared_links(body_text: str) -> list[str]:
    body_text = strip_code_fences(body_text)
    heading_match = _SECTION_HEADING_RE.search(body_text)
    if not heading_match:
        return []
    rest = body_text[heading_match.end():]
    next_heading = _NEXT_HEADING_RE.search(rest)
    section_text = rest[: next_heading.start()] if next_heading else rest
    links: list[str] = []
    for m in _LINK_RE.finditer(section_text):
        links.append(m.group(1))
    for m in _BACKTICK_PATH_RE.finditer(section_text):
        candidate = m.group(1)
        if candidate not in links:
            links.append(candidate)
    return links


def resolve_modules(root_path: Path, set_root: Path, allow_external: bool = False) -> ModuleResolution:
    """Resolve the transitive closure of Normative Modules starting from
    root_path. set_root is the Specification Set root directory that module
    paths must not escape unless allow_external is set (VAL-011).
    """
    result = ModuleResolution(root_path=root_path, set_root=set_root)
    seen: set[Path] = set()
    stack: list[Path] = [root_path]
    visiting_chain: list[Path] = []

    def visit(path: Path, chain: list[Path]):
        if path in chain:
            cycle_desc = " -> ".join(str(p) for p in (*chain, path))
            result.cycles.append(cycle_desc)
            return
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            result.unreadable.append((path, str(exc)))
            return

        for link in extract_declared_links(text):
            if link.startswith(("http://", "https://", "#")):
                continue
            candidate = (path.parent / link).resolve()
            if not allow_external:
                try:
                    candidate.relative_to(set_root)
                except ValueError:
                    result.escaped.append(link)
                    continue
            if candidate in seen and candidate != path:
                if candidate not in result.duplicates:
                    result.duplicates.append(candidate)
            else:
                seen.add(candidate)
                if candidate != root_path:
                    result.modules.append(candidate)
            visit(candidate, [*chain, path])

    visit(root_path, visiting_chain)
    return result
