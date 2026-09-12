"""Requirement/invariant/acceptance identifier extraction from a Specification
Set (used by trace create/update, TRACEGEN-004/005).

No authoritative Core 0.4.2 text defines one required markup convention for
requirement IDs, and real specifications use more than one legitimate style:

- inline-bold, as this tool's own SPEC.md uses it: `- **CLI-001:** text`;
- heading-based, as e.g. a Judo Club Website example spec uses it:
  `### FUN-001 — Required Pages`.

This extractor recognizes both. Acceptance IDs are recognized in the
inline-bold-with-reference-list style: `**ACC-001 — INIT-001/002/003/010:**`,
where the text after the em dash references the requirement/invariant IDs it
covers. This is a best-effort regex extraction (TRACEGEN-005 is a SHOULD),
not a full Markdown/requirements parser, and a document using neither
convention will simply yield no extracted IDs rather than a guess.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from specmd.code_fences import strip_code_fences

_REQUIREMENT_RE = re.compile(r"\*\*([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+):\*\*")
_HEADING_REQUIREMENT_RE = re.compile(r"^#{1,6}\s+([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+)\b", re.MULTILINE)
_ACCEPTANCE_RE = re.compile(r"\*\*([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+)\s+—\s+([^:*]+):\*\*")
_REF_ID_RE = re.compile(r"^([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*)-(\d+)$")


@dataclass
class AcceptanceEntry:
    id: str
    references: list[str] = field(default_factory=list)


def extract_requirement_ids(text: str) -> list[str]:
    fenced_stripped = strip_code_fences(text)
    ids: list[str] = []
    for pattern in (_REQUIREMENT_RE, _HEADING_REQUIREMENT_RE):
        for m in pattern.finditer(fenced_stripped):
            candidate = m.group(1)
            if candidate not in ids:
                ids.append(candidate)
    return ids


def _expand_reference_group(group: str) -> list[str]:
    group = group.strip()
    parts = group.split("/")
    first = _REF_ID_RE.match(parts[0].strip())
    if not first:
        return []
    prefix = first.group(1)
    out = [f"{prefix}-{first.group(2)}"]
    for part in parts[1:]:
        part = part.strip()
        if part.isdigit():
            out.append(f"{prefix}-{part}")
        elif _REF_ID_RE.match(part):
            out.append(part)
    return out


def extract_acceptance_entries(text: str) -> list[AcceptanceEntry]:
    text = strip_code_fences(text)
    entries: list[AcceptanceEntry] = []
    seen: set[str] = set()
    for m in _ACCEPTANCE_RE.finditer(text):
        acc_id, ref_blob = m.group(1), m.group(2)
        if acc_id in seen:
            continue
        seen.add(acc_id)
        refs: list[str] = []
        for group in ref_blob.split(","):
            refs.extend(_expand_reference_group(group))
        entries.append(AcceptanceEntry(id=acc_id, references=refs))
    return entries
