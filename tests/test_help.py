import json

from specmd import exit_codes
from specmd.cli import main


def _run_json(capsys, argv):
    code = main(["--output-format", "json", *argv])
    out = capsys.readouterr().out
    return json.loads(out), code


def test_help_root_lists_available_commands(capsys):
    envelope, code = _run_json(capsys, ["help"])
    assert code == exit_codes.SUCCESS
    names = {t["name"] for t in envelope["results"]["topics"]}
    assert "validate" in names
    assert "cucumber run" not in names  # unavailable, excluded without --all


def test_help_all_includes_unavailable(capsys):
    envelope, code = _run_json(capsys, ["help", "--all"])
    names = {t["name"] for t in envelope["results"]["topics"]}
    assert "cucumber run" in names


def test_help_topic_detail(capsys):
    envelope, code = _run_json(capsys, ["help", "validate"])
    assert code == exit_codes.SUCCESS
    topic = envelope["results"]["topic"]
    assert topic["name"] == "validate"
    assert any(o["name"] == "--trace" for o in topic["options"])


def test_help_unknown_topic_is_usage_error(capsys):
    envelope, code = _run_json(capsys, ["help", "not-a-real-command"])
    assert code == exit_codes.USAGE_ERROR
    assert envelope["results"]["unknown_topic"] == "not-a-real-command"
    assert envelope["results"]["suggestions"]


def test_help_search_filters(capsys):
    envelope, code = _run_json(capsys, ["help", "--search", "trace"])
    names = {t["name"] for t in envelope["results"]["topics"]}
    assert "trace create" in names
    assert "init" not in names


def test_help_never_touches_specification_set(tmp_path, capsys):
    # No SPEC.md anywhere near cwd; help must still work fully.
    code = main(["--output-format", "json", "--cwd", str(tmp_path), "help"])
    envelope = json.loads(capsys.readouterr().out)
    assert code == exit_codes.SUCCESS
