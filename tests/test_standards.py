import json

from specmd import exit_codes
from specmd.cli import main


def _run_json(capsys, argv):
    code = main(["--output-format", "json", *argv])
    out = capsys.readouterr().out
    return json.loads(out), code


def test_standards_list_reports_bundled_versions(capsys):
    envelope, code = _run_json(capsys, ["standards", "list"])
    assert code == exit_codes.SUCCESS
    versions = envelope["results"]["versions"]
    by_version = {(v["kind"], v["version"]): v for v in versions}
    assert by_version[("core", "0.4.2")]["latest"] is False
    assert by_version[("core", "0.4.3")]["latest"] is True
    assert by_version[("optional", "0.4.2")]["source"] == "bundled_local"
    assert by_version[("optional", "0.4.3")]["channel"] == "stable"


def test_standards_show_latest_resolves_to_exact_version(capsys):
    envelope, code = _run_json(capsys, ["standards", "show", "core", "latest"])
    assert code == exit_codes.SUCCESS
    assert envelope["results"]["resolved_version"] == "0.4.3"
    assert envelope["inputs"]["version"] == "latest"  # what was requested is still recorded


def test_standards_show_older_supported_version_still_works(capsys):
    envelope, code = _run_json(capsys, ["standards", "show", "core", "0.4.2"])
    assert code == exit_codes.SUCCESS
    assert envelope["results"]["resolved_version"] == "0.4.2"
    assert envelope["results"]["is_latest"] is False


def test_standards_show_unavailable_version_no_fallback(capsys):
    envelope, code = _run_json(capsys, ["standards", "show", "core", "0.4.1"])
    assert code == exit_codes.CAPABILITY_UNAVAILABLE
    assert envelope["status"] == "failed"


def test_standards_verify_local_file_matches(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["standards", "verify", "--core-document", str(d / "SPEC.md")])
    assert code == exit_codes.SUCCESS
    assert envelope["results"]["checks"][0]["ok"] is True


def test_standards_verify_mismatched_version(tmp_fixture, capsys):
    d = tmp_fixture("broken")
    envelope, code = _run_json(capsys, ["standards", "verify", "--core-document", str(d / "wrong_core_version.md")])
    assert code == exit_codes.FINDINGS
    assert envelope["results"]["checks"][0]["ok"] is False


def test_standards_verify_requires_at_least_one_document(capsys):
    envelope, code = _run_json(capsys, ["standards", "verify"])
    assert code == exit_codes.USAGE_ERROR


def test_standards_verify_no_network_by_construction(tmp_fixture, capsys):
    # There is no network code path in standards.py at all in this build;
    # this test exists as a documented, explicit regression guard for that
    # property rather than a live network assertion.
    import specmd.commands.standards as standards_module
    import inspect as pyinspect

    source = pyinspect.getsource(standards_module)
    assert "requests" not in source
    assert "urllib" not in source
    assert "http://" not in source
    assert "https://" not in source
