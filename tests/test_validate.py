import json

from specmd import exit_codes
from specmd.cli import main


def _run_json(capsys, argv):
    code = main(["--output-format", "json", *argv])
    out = capsys.readouterr().out
    return json.loads(out), code


def test_minimal_core_conforms(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["validate", str(d / "SPEC.md"), "--trace", "none"])
    assert envelope["results"]["specification_result"] == "conforming"
    assert code == exit_codes.SUCCESS


def test_optional_trace_pair_aligned(tmp_fixture, capsys):
    d = tmp_fixture("optional_trace")
    envelope, code = _run_json(capsys, ["validate", str(d / "SPEC.md"), "--trace", "auto"])
    assert envelope["results"]["specification_result"] == "conforming"
    assert envelope["results"]["trace"]["pair_result"] == "aligned"
    assert code == exit_codes.SUCCESS


def test_missing_frontmatter_is_indeterminate(tmp_fixture, capsys):
    # No frontmatter means the declared Core version cannot be resolved at
    # all (VAL-006/008), which is `indeterminate`, not `non_conforming` —
    # distinct from e.g. a wrong-but-present Core version declaration.
    d = tmp_fixture("broken")
    envelope, code = _run_json(capsys, ["validate", str(d / "missing_frontmatter.md"), "--trace", "none"])
    assert envelope["results"]["specification_result"] == "indeterminate"
    assert code == exit_codes.INPUT_ERROR
    assert any(f["rule_id"] == "CORE-FRONTMATTER" for f in envelope["findings"])


def test_missing_section_is_warning_not_error(tmp_fixture, capsys):
    # Core §2's "Empty subsections MAY be omitted" was read, by product
    # decision, as permitting a genuinely-missing top-level section too —
    # so this is a warning (still `conforming`), not a conformance error.
    d = tmp_fixture("broken")
    envelope, code = _run_json(capsys, ["validate", str(d / "missing_section.md"), "--trace", "none"])
    assert envelope["results"]["specification_result"] == "conforming"
    section_findings = [f for f in envelope["findings"] if f["rule_id"] == "CORE-SECTIONS"]
    assert section_findings
    assert all(f["severity"] == "warning" for f in section_findings)


def test_unclosed_human_only_is_error(tmp_fixture, capsys):
    d = tmp_fixture("broken")
    envelope, code = _run_json(capsys, ["validate", str(d / "unclosed_human_only.md"), "--trace", "none"])
    assert any(f["rule_id"] == "SAFE-006" for f in envelope["findings"])
    assert envelope["results"]["specification_result"] == "non_conforming"


def test_core_0_4_3_document_validates_conforming(tmp_fixture, capsys):
    # 0.4.3 was verified to be a pure editorial PATCH of 0.4.2 (diffed
    # directly against the authoritative texts) and is now a fully
    # first-class supported version, not merely tolerated.
    d = tmp_fixture("core_0_4_3")
    envelope, code = _run_json(capsys, ["validate", str(d / "SPEC.md"), "--trace", "none"])
    assert envelope["results"]["specification_result"] == "conforming"
    assert code == exit_codes.SUCCESS
    assert "0.4.3" in envelope["results"]["core_profile"]["versions_supported"]
    assert "0.4.2" in envelope["results"]["core_profile"]["versions_supported"]


def test_wrong_core_version_is_indeterminate(tmp_fixture, capsys):
    d = tmp_fixture("broken")
    envelope, code = _run_json(capsys, ["validate", str(d / "wrong_core_version.md"), "--trace", "none"])
    assert envelope["results"]["specification_result"] == "indeterminate"
    assert code == exit_codes.INPUT_ERROR


def test_unresolved_version_suggests_spec_change_first(tmp_fixture, capsys):
    # PORT-006/007/008 (SPEC.md 4.14): the first suggested remediation for an
    # unresolvable declared version must be a proposed spec change, not a
    # silent substitution of a different version.
    d = tmp_fixture("broken")
    envelope, code = _run_json(capsys, ["validate", str(d / "wrong_core_version.md"), "--trace", "none"])
    port008 = [f for f in envelope["findings"] if f["rule_id"] == "PORT-008"]
    assert len(port008) == 1
    assert "Specification Set change" in port008[0]["message"]
    assert "9.9.9" in port008[0]["message"]


def test_lowercase_keyword_is_warning_not_error(tmp_fixture, capsys):
    d = tmp_fixture("broken")
    envelope, code = _run_json(capsys, ["validate", str(d / "lowercase_keyword.md"), "--trace", "none"])
    bcp14 = [f for f in envelope["findings"] if f["rule_id"] == "CORE-BCP14"]
    assert len(bcp14) == 1
    assert bcp14[0]["severity"] == "warning"
    # A single warning must not by itself make the document non-conforming.
    assert envelope["results"]["specification_result"] == "conforming"


def test_module_resolution_backtick_path_convention(tmp_fixture, capsys):
    # SPEC.md Optional 0.4.2 §10's own illustrated convention: a bare
    # backtick-quoted path, not a Markdown link.
    d = tmp_fixture("backtick_module_link")
    envelope, code = _run_json(capsys, ["validate", str(d / "SPEC.md"), "--trace", "none"])
    assert str(d / "module_a.md") in envelope["results"]["evaluated_files"]
    assert not any(f["rule_id"] == "VAL-005" for f in envelope["findings"])


def test_unrecognized_optional_feature_is_informational_not_warning(tmp_fixture, capsys):
    # Optional 0.4.2 §44 frames optional_features as an open set; an
    # unlisted name is not a defect.
    d = tmp_fixture("optional_trace")
    spec_path = d / "SPEC.md"
    text = spec_path.read_text().replace("  trace: true", "  trace: true\n  some_future_feature: true")
    spec_path.write_text(text)
    envelope, code = _run_json(capsys, ["validate", str(spec_path), "--trace", "none"])
    feature_findings = [f for f in envelope["findings"] if f["rule_id"] == "CORE-VAL-017"]
    assert len(feature_findings) == 1
    assert feature_findings[0]["severity"] == "information"
    assert envelope["results"]["specification_result"] == "conforming"


def test_module_resolution_valid(tmp_fixture, capsys):
    d = tmp_fixture("modules_valid")
    envelope, code = _run_json(capsys, ["validate", str(d / "SPEC.md"), "--trace", "none"])
    assert str(d / "module_a.md") in envelope["results"]["evaluated_files"]
    assert envelope["results"]["specification_result"] == "conforming"


def test_module_resolution_escape_rejected(tmp_fixture, capsys):
    d = tmp_fixture("modules_escape")
    envelope, code = _run_json(capsys, ["validate", str(d / "SPEC.md"), "--trace", "none"])
    assert any(f["rule_id"] == "VAL-011" for f in envelope["findings"])
    assert envelope["results"]["specification_result"] == "non_conforming"


def test_module_resolution_cycle_detected(tmp_fixture, capsys):
    d = tmp_fixture("modules_cycle")
    envelope, code = _run_json(capsys, ["validate", str(d / "SPEC.md"), "--trace", "none"])
    assert any(f["rule_id"] == "VAL-010" for f in envelope["findings"])
    assert envelope["results"]["specification_result"] == "non_conforming"


def test_missing_default_input_fails_without_guessing(tmp_path, capsys):
    code = main(["--output-format", "json", "--cwd", str(tmp_path), "validate"])
    assert code == exit_codes.INPUT_ERROR


def test_prose_mention_of_id_does_not_count_as_trace_coverage(tmp_fixture, capsys):
    # Regression: an ID string appearing in ordinary prose (e.g. explaining
    # that it still needs mapping) must not satisfy TRACE-007 coverage —
    # only a genuine table-row mapping counts.
    d = tmp_fixture("trace_prose_mention_only")
    envelope, code = _run_json(capsys, ["validate", str(d / "SPEC.md"), "--trace", "auto"])
    assert "FIX-001" in envelope["results"]["trace"]["missing_requirement_ids"]
    assert envelope["results"]["trace"]["pair_result"] == "misaligned"


def test_fenced_human_only_example_does_not_trigger_safe_006(tmp_fixture, capsys):
    d = tmp_fixture("fenced_human_only_example")
    envelope, code = _run_json(capsys, ["validate", str(d / "SPEC.md"), "--trace", "none"])
    assert not any(f["rule_id"] == "SAFE-006" for f in envelope["findings"])
    assert envelope["results"]["specification_result"] == "conforming"


def test_status_and_exit_code_consistent_under_cognitive_required(tmp_fixture, capsys):
    # Regression: JSON `status` must match the process exit code (ICD-EXIT-001)
    # even when cognitive mode 'required' is unavailable.
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["validate", str(d / "SPEC.md"), "--trace", "none", "--cognitive", "required"])
    assert envelope["status"] == "indeterminate"
    assert code == exit_codes.CAPABILITY_UNAVAILABLE


def test_explicit_custom_filename_processed_normally(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    custom = d / "spec_web.md"
    (d / "SPEC.md").rename(custom)
    envelope, code = _run_json(capsys, ["validate", str(custom), "--trace", "none"])
    assert envelope["results"]["specification_result"] == "conforming"
