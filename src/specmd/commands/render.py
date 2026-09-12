"""`specmd render` — HTML only (REND-001..008)."""

from __future__ import annotations

import html
import re
from pathlib import Path

from specmd import exit_codes, human_only, module_resolver, writer
from specmd.envelope import build_envelope
from specmd.frontmatter import parse_document

_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


class RenderUsageError(Exception):
    pass


def _markdown_to_html_fragment(text: str) -> str:
    """Minimal, dependency-free Markdown->HTML good enough to preserve
    headings, requirement-ID emphasis, links, code blocks, and tables
    (REND-002) without pulling in a Markdown rendering dependency.
    """
    out: list[str] = []
    lines = text.splitlines()
    i = 0
    in_table = False
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
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

        heading_m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", line)
        if heading_m:
            level = len(heading_m.group(1))
            out.append(f"<h{level}>{_inline(heading_m.group(2))}</h{level}>")
            i += 1
            continue

        if "|" in line and line.strip().startswith("|"):
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
            out.append("</table>")
            in_table = False

        if not line.strip():
            i += 1
            continue

        out.append(f"<p>{_inline(line)}</p>")
        i += 1

    if in_table:
        out.append("</table>")
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
        ".specmd-source-label{color:#666;font-size:.85em;border-top:2px solid #ccc;padding-top:.5rem;}</style>"
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
