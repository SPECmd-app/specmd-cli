import json

import pytest

from specmd import exit_codes
from specmd.cli import main


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "specmd" in out


def test_help_flag(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "usage: specmd" in out


def test_unknown_command_is_usage_error(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["frobnicate"])
    assert exc.value.code == 2


def test_unknown_option_is_usage_error(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    with pytest.raises(SystemExit) as exc:
        main(["validate", str(d / "SPEC.md"), "--not-a-real-option"])
    assert exc.value.code == 2


def test_json_envelope_shape(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    main(["--output-format", "json", "validate", str(d / "SPEC.md"), "--trace", "none"])
    out = capsys.readouterr().out
    envelope = json.loads(out)
    for key in ("schema_version", "tool_version", "command", "status", "inputs", "results", "findings", "writes", "cognitive"):
        assert key in envelope
    assert envelope["schema_version"] == "1.1.0"
    for f in envelope["findings"]:
        for key in ("rule_id", "severity", "evidence_type", "message", "reviewers", "file", "line", "column"):
            assert key in f
        assert f["severity"] in ("error", "warning", "information")
        assert f["evidence_type"] in ("deterministic", "heuristic")


def test_text_output_does_not_crash(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    code = main(["validate", str(d / "SPEC.md"), "--trace", "none"])
    out = capsys.readouterr().out
    assert "specmd validate" in out
    assert code == exit_codes.SUCCESS


def test_quiet_suppresses_status_line(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    main(["--quiet", "validate", str(d / "SPEC.md"), "--trace", "none"])
    out = capsys.readouterr().out
    assert "specmd validate" not in out
