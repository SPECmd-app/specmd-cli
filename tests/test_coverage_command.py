import json

from specmd import exit_codes
from specmd.cli import main


def _run_json(capsys, argv):
    code = main(["--output-format", "json", *argv])
    out = capsys.readouterr().out
    return json.loads(out), code


def test_test_reports_covered_and_uncovered(tmp_fixture, capsys):
    d = tmp_fixture("optional_trace")  # FIX-001 and INV-001, covered by ACC-001
    envelope, code = _run_json(capsys, ["test", str(d / "SPEC.md"), "--trace", "none"])
    assert code == exit_codes.SUCCESS
    assert "FIX-001" in envelope["results"]["covered_requirement_ids"]
    assert envelope["results"]["uncovered_requirement_ids"] == []


def test_test_flags_uncovered_requirement_and_unreferenced_acceptance(tmp_fixture, capsys):
    d = tmp_fixture("uncovered_requirement")
    envelope, code = _run_json(capsys, ["test", str(d / "SPEC.md"), "--trace", "none"])
    # Coverage gaps are reported as warnings (TEST-003), not conformance
    # errors, so the command still succeeds while surfacing them.
    assert code == exit_codes.SUCCESS
    assert envelope["results"]["uncovered_requirement_ids"] == ["FIX-001"]
    assert "FIX-002" in envelope["results"]["covered_requirement_ids"]
    assert envelope["results"]["unreferenced_acceptance_ids"] == ["ACC-002"]
    assert any(f["rule_id"] == "TEST-003" and f["severity"] == "warning" for f in envelope["findings"])


def test_test_run_integration_is_unavailable(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["test", str(d / "SPEC.md"), "--run-integration", "pytest"])
    assert code == exit_codes.CAPABILITY_UNAVAILABLE
    assert envelope["status"] == "failed"


def test_test_export_never_fabricates_structured_fields(tmp_fixture, capsys):
    d = tmp_fixture("optional_trace")
    out_path = d / "plan.json"
    envelope, code = _run_json(capsys, ["test", str(d / "SPEC.md"), "--trace", "none", "--export", str(out_path)])
    assert code == exit_codes.SUCCESS
    plan = json.loads(out_path.read_text())
    fix001 = next(p for p in plan if p["requirement_id"] == "FIX-001")
    assert fix001["covered"] is True
    assert fix001["preconditions"] is None
    assert fix001["actions"] is None
    assert fix001["expected_outcomes"] is None
    assert fix001["verification_method"] is None
    assert "not available" in fix001["export_note"]
