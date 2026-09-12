import json

from specmd import exit_codes
from specmd.cli import main


def _run_json(capsys, argv):
    code = main(["--output-format", "json", *argv])
    out = capsys.readouterr().out
    return json.loads(out), code


def test_blackbox_inventories_ids_and_sections(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["blackbox", str(d / "SPEC.md"), "--trace", "none"])
    assert code == exit_codes.SUCCESS
    assert "FIX-001" in envelope["results"]["requirement_ids"]
    comp = envelope["results"]["completeness"]
    assert comp["trace_coverage"]["available"] is False  # --trace none


def test_blackbox_never_writes_without_export(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    _run_json(capsys, ["blackbox", str(d / "SPEC.md"), "--trace", "none"])
    assert list(d.iterdir()) == [d / "SPEC.md"]


def test_blackbox_export_writes_json_report(tmp_fixture, capsys):
    d = tmp_fixture("optional_trace")
    out_path = d / "report.json"
    envelope, code = _run_json(capsys, ["blackbox", str(d / "SPEC.md"), "--trace", "auto", "--export", str(out_path)])
    assert code == exit_codes.SUCCESS
    assert out_path.exists()
    report = json.loads(out_path.read_text())
    assert "completeness" in report
    assert report["completeness"]["trace_coverage"]["available"] is True
    assert report["completeness"]["trace_coverage"]["pair_result"] == "aligned"


def test_blackbox_flags_unresolved_core_version(tmp_fixture, capsys):
    d = tmp_fixture("broken")
    envelope, code = _run_json(capsys, ["blackbox", str(d / "wrong_core_version.md"), "--trace", "none"])
    assert envelope["status"] == "indeterminate"
    assert code == exit_codes.INPUT_ERROR
    assert any(f["rule_id"] == "PORT-008" for f in envelope["findings"])
