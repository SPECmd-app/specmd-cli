import json

from specmd.cli import main


def test_capabilities_reports_commands_and_versions(capsys):
    code = main(["--output-format", "json", "capabilities"])
    envelope = json.loads(capsys.readouterr().out)
    assert code == 0
    assert envelope["status"] == "succeeded"
    r = envelope["results"]
    assert r["core_versions_supported"] == ["0.4.2", "0.4.3"]
    assert r["latest_core_version"] == "0.4.3"
    names = {c["name"] for c in r["commands"]}
    assert {"init", "validate", "blackbox", "test", "adapt", "capabilities", "help"} <= names
    unavailable = {c["name"]: c for c in r["commands"] if not c["available"]}
    assert "standards fetch" in unavailable
    assert unavailable["standards fetch"]["unavailable_reason"]


def test_capabilities_requires_no_specification_set(tmp_path, capsys):
    # No SPEC.md anywhere near cwd — capabilities must still work.
    code = main(["--output-format", "json", "--cwd", str(tmp_path), "capabilities"])
    envelope = json.loads(capsys.readouterr().out)
    assert code == 0
    assert envelope["status"] == "succeeded"
