import json

from specmd import exit_codes
from specmd.cli import main


def _run_json(capsys, argv):
    code = main(["--output-format", "json", *argv])
    out = capsys.readouterr().out
    return json.loads(out), code


def test_render_html_creates_output(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    out_html = d / "out.html"
    envelope, code = _run_json(capsys, ["render", str(d / "SPEC.md"), "--output", str(out_html)])
    assert code == exit_codes.SUCCESS
    assert out_html.exists()
    text = out_html.read_text()
    assert "<h1>" in text or "<h2>" in text
    assert "Requirements" in text
    assert "FIX-001" in text


def test_render_pdf_unavailable(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["render", str(d / "SPEC.md"), "--render-format", "pdf"])
    assert code == exit_codes.CAPABILITY_UNAVAILABLE


def test_render_excludes_human_only_by_default(tmp_fixture, capsys):
    d = tmp_fixture("human_only_wellformed")
    out_html = d / "out.html"
    _run_json(capsys, ["render", str(d / "SPEC.md"), "--output", str(out_html)])
    assert "EDITORS-ONLY-SECRET-MARKER" not in out_html.read_text()


def test_render_includes_human_only_when_requested(tmp_fixture, capsys):
    d = tmp_fixture("human_only_wellformed")
    out_html = d / "out.html"
    _run_json(capsys, ["render", str(d / "SPEC.md"), "--output", str(out_html), "--include-human-only"])
    assert "EDITORS-ONLY-SECRET-MARKER" in out_html.read_text()


def test_render_preserves_fenced_human_only_syntax_example(tmp_fixture, capsys):
    # A documentation example that merely illustrates the human-only comment
    # syntax inside a fenced code block is not itself human-only content and
    # must survive default rendering (regression for the fence-unaware
    # stripping bug found via the Judo Club example document).
    d = tmp_fixture("fenced_human_only_example")
    out_html = d / "out.html"
    _run_json(capsys, ["render", str(d / "SPEC.md"), "--output", str(out_html)])
    text = out_html.read_text()
    assert "SPECMD-HUMAN-ONLY" in text
    assert "Human drafting or review note." in text


def test_render_reports_no_overwrite_without_force(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    out_html = d / "out.html"
    _run_json(capsys, ["render", str(d / "SPEC.md"), "--output", str(out_html)])
    envelope, code = _run_json(capsys, ["render", str(d / "SPEC.md"), "--output", str(out_html)])
    assert code == exit_codes.WRITE_ERROR
    assert envelope["writes"][0]["action"] == "refused"
