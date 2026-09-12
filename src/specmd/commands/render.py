"""`specmd render` — HTML only (REND-001..008)."""

from __future__ import annotations

import html
import re
from pathlib import Path

from specmd import core_profile, exit_codes, human_only, module_resolver, writer
from specmd.envelope import build_envelope
from specmd.frontmatter import parse_document

_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
_ORDERED_RE = re.compile(r"^\s*\d+\.\s+(.*)$")
_BLOCKQUOTE_RE = re.compile(r"^>\s?(.*)$")

HUMAN_ONLY_CSS = (
    ".specmd-human-only{border:2px solid #c0392b;background:#fdecea;"
    "padding:.25rem 1rem;margin:1rem 0;border-radius:4px;}"
    ".specmd-human-only-label{color:#c0392b;font-weight:bold;font-size:.75em;"
    "text-transform:uppercase;letter-spacing:.05em;margin:.5rem 0 0 0;}"
)


class RenderUsageError(Exception):
    pass


def _markdown_to_html_fragment(text: str) -> str:
    """Minimal, dependency-free Markdown->HTML good enough to preserve
    headings, requirement-ID emphasis, links, code blocks, tables, bulleted/
    numbered lists, and blockquotes (REND-002) without pulling in a Markdown
    rendering dependency. No nested-list support — a flat list per block is
    what SPEC.md documents in practice use.

    Only reached with human-only markers still present when the caller kept
    them in (--include-human-only); the default path already strips them
    before this function ever sees the text. When present, a block is
    wrapped and clearly labeled (ICD-CLI 8.4: "--include-human-only is
    permitted only for a clearly labeled editorial rendering") rather than
    left as raw delimiter text in a bare <p>.
    """
    out: list[str] = []
    lines = text.splitlines()
    i = 0
    in_table = False
    in_human_only = False
    # Exactly one of these is active at a time; each holds the open tag name.
    open_block: str | None = None  # "ul" | "ol" | "blockquote" | None

    def close_block():
        nonlocal open_block
        if open_block is not None:
            out.append(f"</{open_block}>")
            open_block = None

    def close_table():
        nonlocal in_table
        if in_table:
            out.append("</table>")
            in_table = False

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            close_block()
            close_table()
            fence_lines = [line]
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                fence_lines.append(lines[i])
                i += 1
            if i < len(lines):
                fence_lines.append(lines[i])
                i += 1
            code = "\n".join(fence_lines[1:-1])
            out.append(f"<pre><code>{html.escape(code)}</code></pre>")
            continue

        if core_profile.HUMAN_ONLY_START in line and not in_human_only:
            close_block()
            close_table()
            in_human_only = True
            out.append(
                '<div class="specmd-human-only">'
                '<p class="specmd-human-only-label">Human-only comment — not part of the normative specification</p>'
            )
            i += 1
            continue

        if core_profile.HUMAN_ONLY_END in line and in_human_only:
            close_block()
            close_table()
            in_human_only = False
            out.append("</div>")
            i += 1
            continue

        heading_m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", line)
        if heading_m:
            close_block()
            close_table()
            level = len(heading_m.group(1))
            out.append(f"<h{level}>{_inline(heading_m.group(2))}</h{level}>")
            i += 1
            continue

        if "|" in line and line.strip().startswith("|"):
            close_block()
            if not in_table:
                out.append("<table>")
                in_table = True
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c) for c in cells):
                # Markdown header/body divider row (e.g. |---|---|) — not rendered.
                i += 1
                continue
            row = "".join(f"<td>{_inline(c)}</td>" for c in cells)
            out.append(f"<tr>{row}</tr>")
            i += 1
            continue
        elif in_table:
            close_table()

        bullet_m = _BULLET_RE.match(line)
        ordered_m = None if bullet_m else _ORDERED_RE.match(line)
        quote_m = None if (bullet_m or ordered_m) else _BLOCKQUOTE_RE.match(line)

        if bullet_m:
            if open_block != "ul":
                close_block()
                out.append("<ul>")
                open_block = "ul"
            out.append(f"<li>{_inline(bullet_m.group(1))}</li>")
            i += 1
            continue

        if ordered_m:
            if open_block != "ol":
                close_block()
                out.append("<ol>")
                open_block = "ol"
            out.append(f"<li>{_inline(ordered_m.group(1))}</li>")
            i += 1
            continue

        if quote_m:
            if open_block != "blockquote":
                close_block()
                out.append("<blockquote>")
                open_block = "blockquote"
            out.append(f"<p>{_inline(quote_m.group(1))}</p>")
            i += 1
            continue

        close_block()

        if not line.strip():
            i += 1
            continue

        out.append(f"<p>{_inline(line)}</p>")
        i += 1

    close_block()
    close_table()
    if in_human_only:
        # Malformed/unclosed block (SAFE-006 catches this at validate-time);
        # close it here too so rendering never emits unbalanced HTML.
        out.append("</div>")
    return "\n".join(out)


def _inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    return text


def run(
    *,
    root_spec_path: Path,
    set_root: Path,
    display_path: str,
    output_path: Path,
    render_format: str,
    include_human_only: bool,
    force: bool,
) -> tuple[dict, int]:
    if render_format != "html":
        # REND-005: PDF is a SHOULD and is not implemented in this build.
        envelope = build_envelope(
            command="render",
            status="failed",
            inputs={"root_spec": display_path, "render_format": render_format},
            results={},
            findings=[],
            writes=[],
            cognitive_requested="off",
            cognitive_used="none",
            cognitive_complete=True,
        )
        return envelope, exit_codes.CAPABILITY_UNAVAILABLE

    module_res = module_resolver.resolve_modules(root_spec_path, set_root)
    all_files = [root_spec_path] + module_res.modules

    sections = []
    for path in all_files:
        text = path.read_text(encoding="utf-8")
        doc = parse_document(str(path), text)
        body = doc.body
        if not include_human_only:
            body = human_only.strip_human_only(body)
        fm = doc.frontmatter or {}
        heading = "Root Specification" if path == root_spec_path else "Normative Module"
        sections.append(
            f'<section data-source="{html.escape(str(path.name))}">'
            f"<p class=\"specmd-source-label\">{heading}: {html.escape(path.name)} "
            f"(specmd {html.escape(str(fm.get('specmd', '?')))}"
            + (f", specmd_optional {html.escape(str(fm.get('specmd_optional')))}" if fm.get("specmd_optional") else "")
            + f", spec_version {html.escape(str(fm.get('spec_version', '?')))})</p>"
            + _markdown_to_html_fragment(body)
            + "</section>"
        )

    root_fm = (parse_document(str(root_spec_path), root_spec_path.read_text(encoding="utf-8")).frontmatter) or {}
    title = html.escape(str(root_fm.get("name", root_spec_path.name)))
    doc_html = (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        f"<title>{title}</title>"
        "<style>body{font-family:sans-serif;max-width:60rem;margin:2rem auto;padding:0 1rem;}"
        "table{border-collapse:collapse;}td,th{border:1px solid #ccc;padding:.25rem .5rem;}"
        ".specmd-source-label{color:#666;font-size:.85em;border-top:2px solid #ccc;padding-top:.5rem;}"
        f"{HUMAN_ONLY_CSS}</style>"
        "</head><body>"
        + "".join(sections)
        + "</body></html>"
    )

    try:
        write_result = writer.safe_write(output_path, doc_html, force=force)
        status = "succeeded"
        exit_code = exit_codes.SUCCESS
        writes = [{"path": write_result.path, "action": write_result.action}]
    except writer.WriteRefused as exc:
        status = "failed"
        exit_code = exit_codes.WRITE_ERROR
        writes = [{"path": str(exc.path), "action": "refused"}]

    envelope = build_envelope(
        command="render",
        status=status,
        inputs={"root_spec": display_path, "render_format": render_format, "output": str(output_path)},
        results={"included_modules": [str(m) for m in module_res.modules]},
        findings=[],
        writes=writes,
        cognitive_requested="off",
        cognitive_used="none",
        cognitive_complete=True,
    )
    return envelope, exit_code
