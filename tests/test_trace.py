import json

from specmd import exit_codes
from specmd.cli import main


def _run_json(capsys, argv):
    code = main(["--output-format", "json", *argv])
    out = capsys.readouterr().out
    return json.loads(out), code


def test_trace_create_refuses_without_enable_optional(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")  # Core-only, trace not declared
    envelope, code = _run_json(capsys, ["trace", "create", str(d / "SPEC.md"), "--output", str(d / "TRACE.md")])
    assert code == exit_codes.WRITE_ERROR
    assert not (d / "TRACE.md").exists()
    assert "specmd_optional" not in (d / "SPEC.md").read_text()  # root spec left unchanged


def test_trace_create_with_enable_optional(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    spec_before = (d / "SPEC.md").read_text()
    envelope, code = _run_json(
        capsys, ["trace", "create", str(d / "SPEC.md"), "--output", str(d / "TRACE.md"), "--enable-optional"]
    )
    assert code == exit_codes.SUCCESS
    assert (d / "TRACE.md").exists()
    spec_after = (d / "SPEC.md").read_text()
    assert spec_after != spec_before
    assert "specmd_optional" in spec_after
    assert "trace: true" in spec_after
    assert "FIX-001" in (d / "TRACE.md").read_text()
    assert envelope["results"]["pair_result"] == "aligned"


def test_trace_create_on_already_declared_fixture(tmp_fixture, capsys):
    d = tmp_fixture("optional_trace")
    (d / "TRACE.md").unlink()
    envelope, code = _run_json(capsys, ["trace", "create", str(d / "SPEC.md"), "--output", str(d / "TRACE.md")])
    assert code == exit_codes.SUCCESS
    assert envelope["results"]["pair_result"] == "aligned"
    assert "FIX-001" in (d / "TRACE.md").read_text()
    assert "INV-001" in (d / "TRACE.md").read_text()


def test_trace_update_is_idempotent_on_aligned_pair(tmp_fixture, capsys):
    d = tmp_fixture("optional_trace")
    before = (d / "TRACE.md").read_text()
    envelope, code = _run_json(capsys, ["trace", "update", str(d / "SPEC.md"), "--trace", str(d / "TRACE.md")])
    assert code == exit_codes.SUCCESS
    assert envelope["results"]["new_requirement_ids"] == []
    assert envelope["results"]["removed_ids_flagged"] == []
    assert (d / "TRACE.md").read_text() == before


def test_trace_update_adds_new_requirement_and_preserves_manual_content(tmp_fixture, capsys):
    d = tmp_fixture("optional_trace")
    spec_path = d / "SPEC.md"
    text = spec_path.read_text()
    text = text.replace(
        "- **INV-001:** This fixture invariant MUST hold.",
        "- **INV-001:** This fixture invariant MUST hold.\n- **FIX-002:** A brand-new requirement not yet in TRACE.md.",
    )
    spec_path.write_text(text)

    # Mark a manual implementation reference in the existing TRACE.md to
    # prove it survives the update.
    trace_path = d / "TRACE.md"
    trace_text = trace_path.read_text().replace("| FIX-001 | TBD | Planned |", "| FIX-001 | src/fixture.py | Manually verified |")
    trace_path.write_text(trace_text)

    envelope, code = _run_json(capsys, ["trace", "update", str(spec_path), "--trace", str(trace_path)])
    assert code == exit_codes.SUCCESS
    assert "FIX-002" in envelope["results"]["new_requirement_ids"]
    after = trace_path.read_text()
    assert "src/fixture.py" in after  # manual content preserved
    assert "Manually verified" in after
    assert "FIX-002" in after


def test_trace_create_refuses_on_unresolved_core_version(tmp_fixture, capsys):
    d = tmp_fixture("broken")
    envelope, code = _run_json(
        capsys, ["trace", "create", str(d / "wrong_core_version.md"), "--output", str(d / "TRACE.md"), "--enable-optional"]
    )
    assert code == exit_codes.INPUT_ERROR
    assert envelope["status"] == "indeterminate"
    assert not (d / "TRACE.md").exists()
    assert any(f["rule_id"] == "PORT-008" for f in envelope["findings"])


def test_trace_update_refuses_on_unresolved_core_version(tmp_fixture, capsys):
    d = tmp_fixture("broken")
    before = (d / "wrong_core_version.md").read_text()
    envelope, code = _run_json(capsys, ["trace", "update", str(d / "wrong_core_version.md"), "--trace", str(d / "TRACE.md")])
    assert code == exit_codes.INPUT_ERROR
    assert envelope["status"] == "indeterminate"
    assert (d / "wrong_core_version.md").read_text() == before  # unchanged


def test_trace_update_missing_trace_file_fails(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["trace", "update", str(d / "SPEC.md"), "--trace", str(d / "TRACE.md")])
    assert code == exit_codes.INPUT_ERROR
