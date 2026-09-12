import json

from specmd import exit_codes
from specmd.cli import main


def _run_json(capsys, argv):
    code = main(["--output-format", "json", *argv])
    out = capsys.readouterr().out
    return json.loads(out), code


def test_init_creates_minimal_core_doc(tmp_path, capsys):
    out = tmp_path / "SPEC.md"
    envelope, code = _run_json(capsys, ["init", str(out)])
    assert code == exit_codes.SUCCESS
    assert out.exists()
    text = out.read_text()
    assert "0.4.2" in text
    assert "specmd_optional" not in text
    assert "optional_features" not in text


def test_init_refuses_overwrite_without_force(tmp_path, capsys):
    out = tmp_path / "SPEC.md"
    _run_json(capsys, ["init", str(out)])
    envelope, code = _run_json(capsys, ["init", str(out)])
    assert code == exit_codes.WRITE_ERROR
    assert envelope["writes"][0]["action"] == "refused"


def test_init_optional_profile_requires_feature(tmp_path, capsys):
    out = tmp_path / "SPEC.md"
    code = main(["--output-format", "json", "init", str(out), "--profile", "optional"])
    assert code == exit_codes.USAGE_ERROR
    capsys.readouterr()


def test_init_optional_profile_with_feature(tmp_path, capsys):
    out = tmp_path / "SPEC.md"
    envelope, code = _run_json(capsys, ["init", str(out), "--profile", "optional", "--feature", "trace"])
    assert code == exit_codes.SUCCESS
    text = out.read_text()
    assert "specmd_optional" in text
    assert "trace: true" in text


def test_init_generated_doc_validates_conforming(tmp_path, capsys):
    out = tmp_path / "SPEC.md"
    _run_json(capsys, ["init", str(out)])
    envelope, code = _run_json(capsys, ["validate", str(out), "--trace", "none"])
    assert envelope["results"]["specification_result"] == "conforming"
