import json

from specmd import exit_codes
from specmd.cli import main


def _run_json(capsys, argv):
    code = main(["--output-format", "json", *argv])
    out = capsys.readouterr().out
    return json.loads(out), code


def test_adapt_generates_claude_code_adapter(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    out_path = d / "CLAUDE.md"
    envelope, code = _run_json(capsys, ["adapt", "claude-code", str(d / "SPEC.md"), "--output", str(out_path)])
    assert code == exit_codes.SUCCESS
    assert out_path.exists()
    text = out_path.read_text()
    assert "Root Specification" in text
    assert "SPECMD-HUMAN-ONLY" in text
    # ADAPT-006: must not paste actual requirement text verbatim.
    assert "This fixture MUST remain minimal" not in text


def test_adapt_all_six_targets_succeed(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    for i, target in enumerate(["codex", "claude-code", "cursor", "github-copilot", "base44", "lovable"]):
        out_path = d / f"adapter_{i}.md"
        envelope, code = _run_json(capsys, ["adapt", target, str(d / "SPEC.md"), "--output", str(out_path)])
        assert code == exit_codes.SUCCESS, target
        assert out_path.exists()


def test_adapt_unsupported_target_rejected(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["adapt", "not-a-real-tool", str(d / "SPEC.md")])
    assert code == exit_codes.CAPABILITY_UNAVAILABLE
    assert envelope["status"] == "failed"
    assert "base44" in envelope["results"]["reason"]
    assert "lovable" in envelope["results"]["reason"]


def test_adapt_base44_and_lovable_default_filenames(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    for target, expected_name in (("base44", "base44-instructions.md"), ("lovable", "lovable-instructions.md")):
        envelope, code = _run_json(capsys, ["--cwd", str(d), "adapt", target, str(d / "SPEC.md")])
        assert code == exit_codes.SUCCESS
        assert (d / expected_name).exists()


def test_adapt_install_not_implemented(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["adapt", "claude-code", str(d / "SPEC.md"), "--install"])
    assert code == exit_codes.CAPABILITY_UNAVAILABLE


def test_adapt_never_modifies_root_spec(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    before = (d / "SPEC.md").read_text()
    _run_json(capsys, ["adapt", "claude-code", str(d / "SPEC.md"), "--output", str(d / "CLAUDE.md")])
    assert (d / "SPEC.md").read_text() == before


def test_adapt_refuses_overwrite_without_force(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    out_path = d / "CLAUDE.md"
    _run_json(capsys, ["adapt", "claude-code", str(d / "SPEC.md"), "--output", str(out_path)])
    envelope, code = _run_json(capsys, ["adapt", "claude-code", str(d / "SPEC.md"), "--output", str(out_path)])
    assert code == exit_codes.WRITE_ERROR
