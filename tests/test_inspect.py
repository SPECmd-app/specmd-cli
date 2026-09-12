import json

from specmd.cli import main


def _run_json(capsys, argv):
    code = main(["--output-format", "json", *argv])
    out = capsys.readouterr().out
    return json.loads(out), code


def test_inspect_reports_measurements_and_incomplete_cognitive(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["inspect", str(d / "SPEC.md"), "--trace", "none"])
    assert envelope["results"]["measurements"]["line_count"] > 0
    assert envelope["cognitive"]["complete"] is False
    assert envelope["cognitive"]["used"] == "none"
    assert any(f["rule_id"] == "INSP-008" for f in envelope["findings"])


def test_inspect_cognitive_off_is_complete(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["inspect", str(d / "SPEC.md"), "--trace", "none", "--cognitive", "off"])
    assert envelope["cognitive"]["complete"] is True


def test_inspect_no_compactness_warning_for_non_core_design(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["inspect", str(d / "SPEC.md"), "--trace", "none"])
    assert "compactness_target_lines" not in envelope["results"]["measurements"]


def test_status_and_exit_code_consistent_under_cognitive_required(tmp_fixture, capsys):
    from specmd import exit_codes

    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["inspect", str(d / "SPEC.md"), "--trace", "none", "--cognitive", "required"])
    assert envelope["status"] == "indeterminate"
    assert code == exit_codes.CAPABILITY_UNAVAILABLE


def test_unresolved_core_version_is_indeterminate_not_findings(tmp_fixture, capsys):
    # Regression: inspect() previously reported "findings"/exit 1 for an
    # unresolvable Core version, inconsistent with validate()'s "indeterminate"
    # /exit 3 for the identical root cause (ICD-EXIT-001).
    from specmd import exit_codes

    d = tmp_fixture("broken")
    envelope, code = _run_json(capsys, ["inspect", str(d / "wrong_core_version.md"), "--trace", "none"])
    assert envelope["status"] == "indeterminate"
    assert code == exit_codes.INPUT_ERROR
    assert any(f["rule_id"] == "PORT-008" for f in envelope["findings"])
