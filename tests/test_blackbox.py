import json

from specmd import exit_codes
from specmd.cli import main


_VALID_HOST_AGENT_INPUT = {
    "interfaces": [
        {
            "interface": "Web Portal",
            "input_contract": ["subject", "body"],
            "output_contract": ["ticket id"],
            "supporting_requirement_ids": ["TICKET-001"],
            "gaps": [],
            "confidence": "medium",
        },
        {
            "interface": "Ticket Creation API",
            "input_contract": ["subject", "body"],
            "output_contract": ["ticket id"],
            "supporting_requirement_ids": ["TICKET-002"],
            "gaps": ["Authentication mechanism for API callers is not specified."],
            "confidence": "low",
        },
    ],
    "requirements_interface_cross_mapping": {"unmatched_requirements": [], "unmatched_interface_elements": []},
}


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


def test_blackbox_cognitive_defaults_to_auto_and_discloses_no_provider(tmp_fixture, capsys):
    # ICD-CLI section 7 line 234: blackbox's --cognitive default is `auto`,
    # not `off`. No Cognitive Provider is configured in this build, so this
    # must honestly report an incomplete cognitive result (ICD-COG-002/003)
    # and, since Host-Agent Mode is how the semantic checks actually get
    # satisfied here, include the bounded cognitive_package the calling
    # agent needs to answer with --cognitive-input.
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["blackbox", str(d / "SPEC.md"), "--trace", "none"])
    assert code == exit_codes.SUCCESS
    assert envelope["cognitive"]["requested"] == "auto"
    assert envelope["cognitive"]["used"] == "none"
    assert envelope["cognitive"]["complete"] is False
    disclosures = [f for f in envelope["findings"] if f["rule_id"] == "BBX-004"]
    assert len(disclosures) == 1
    assert disclosures[0]["severity"] == "information"
    assert disclosures[0]["evidence_type"] == "heuristic"
    comp = envelope["results"]["completeness"]["specification_completeness"]
    package = comp["cognitive_package"]
    assert "reconstruct" in package["analysis_goal"].lower()
    assert package["known_requirement_ids"] == envelope["results"]["requirement_ids"]
    assert package["known_interface_elements"] == comp["interface_elements"]
    assert "interfaces_and_external_contracts" in package["material"]
    assert "response_contract" in package
    assert "io_facilitation_drafts" not in comp
    assert "requirements_interface_cross_mapping" not in comp


def test_blackbox_cognitive_off_omits_disclosure_and_scaffold_keys(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["blackbox", str(d / "SPEC.md"), "--trace", "none", "--cognitive", "off"])
    assert code == exit_codes.SUCCESS
    assert envelope["cognitive"]["requested"] == "off"
    assert envelope["cognitive"]["used"] == "none"
    assert envelope["cognitive"]["complete"] is True
    assert not any(f["rule_id"] == "BBX-004" for f in envelope["findings"])
    comp = envelope["results"]["completeness"]["specification_completeness"]
    assert "io_facilitation_drafts" not in comp
    assert "requirements_interface_cross_mapping" not in comp


def test_blackbox_cognitive_required_without_provider_is_indeterminate(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(
        capsys, ["blackbox", str(d / "SPEC.md"), "--trace", "none", "--cognitive", "required"]
    )
    assert envelope["status"] == "indeterminate"
    assert code == exit_codes.CAPABILITY_UNAVAILABLE
    # Deterministic findings computed before negotiation must survive intact
    # (COG-009/PROV-009): the section inventory is still reported.
    assert "interface_section_inventory" in envelope["results"]


def test_blackbox_actor_operation_gap_detected(tmp_fixture, capsys):
    d = tmp_fixture("blackbox_actor_gap")
    envelope, code = _run_json(capsys, ["blackbox", str(d / "SPEC.md"), "--trace", "none", "--cognitive", "off"])
    assert code == exit_codes.SUCCESS
    coverage = envelope["results"]["completeness"]["specification_completeness"]["actor_operation_coverage"]
    assert coverage == {"Ticket Requester": True, "Support Agent": False}
    gap_findings = [
        f for f in envelope["findings"] if f["rule_id"] == "BBX-003" and "Support Agent" in f["message"]
    ]
    assert len(gap_findings) == 1
    # `information`, not `warning`: text matching alone cannot tell an actor
    # from a same-convention data entity, so the finding must not overclaim.
    assert gap_findings[0]["severity"] == "information"
    assert gap_findings[0]["evidence_type"] == "deterministic"


def test_blackbox_actor_operation_no_actors_is_not_a_false_positive(tmp_fixture, capsys):
    # minimal_core's System Model body is "TBD" (no bulleted actors), so the
    # check must report an empty coverage map rather than inventing a gap.
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["blackbox", str(d / "SPEC.md"), "--trace", "none", "--cognitive", "off"])
    assert code == exit_codes.SUCCESS
    comp = envelope["results"]["completeness"]["specification_completeness"]
    assert comp["actor_operation_coverage"] == {}
    assert not any(f["rule_id"] == "BBX-003" for f in envelope["findings"])


def test_blackbox_actor_operation_ignores_unbolded_prose_and_id_bullets(tmp_fixture, capsys):
    # Regression: found by checking this feature against a real example
    # document (SPECmd-app/spec-md-examples, internal-it-ticketing-system,
    # commit 5751f95). Its System Model mixes plain-prose actor sentences
    # ("- A Requester belongs to...") with ID-prefixed invariant bullets
    # ("- INV-001: Every Ticket MUST..."). An earlier version of the actor
    # regex treated any ":"/"-"/"—" anywhere in a bullet as a name delimiter,
    # which swallowed the entire prose sentence up to a colon buried deep in
    # it, and separately mistook the hyphen inside "INV-001" for a
    # name/description delimiter, extracting "INV" as a bogus actor. Only
    # bold-labeled bullets ("- **Name**: ...") are a precise enough signal to
    # trust deterministically.
    d = tmp_fixture("blackbox_prose_and_id_bullets")
    envelope, code = _run_json(capsys, ["blackbox", str(d / "SPEC.md"), "--trace", "none", "--cognitive", "off"])
    assert code == exit_codes.SUCCESS
    coverage = envelope["results"]["completeness"]["specification_completeness"]["actor_operation_coverage"]
    assert coverage == {"Ticket": True}
    assert not any(name.startswith("INV") or "Requester belongs" in name for name in coverage)


def test_blackbox_interface_elements_from_headings(tmp_fixture, capsys):
    d = tmp_fixture("blackbox_host_agent")
    envelope, code = _run_json(capsys, ["blackbox", str(d / "SPEC.md"), "--trace", "none", "--cognitive", "off"])
    assert code == exit_codes.SUCCESS
    comp = envelope["results"]["completeness"]["specification_completeness"]
    assert comp["interface_elements"] == ["Web Portal", "Ticket Creation API"]


def test_blackbox_interface_elements_empty_when_no_subheadings(tmp_fixture, capsys):
    d = tmp_fixture("minimal_core")
    envelope, code = _run_json(capsys, ["blackbox", str(d / "SPEC.md"), "--trace", "none", "--cognitive", "off"])
    assert code == exit_codes.SUCCESS
    comp = envelope["results"]["completeness"]["specification_completeness"]
    assert comp["interface_elements"] == []


def test_blackbox_interface_elements_ignores_nested_subsections_of_one_interface(tmp_fixture, capsys):
    # Regression: found by checking this feature against a real example
    # document (SPECmd-app/SPEC.md's Judo Club walkthrough,
    # examples/judo-club-specmd-0.4.3.md at commit f92d30c). Its single
    # "Contact Communication Interface" is broken down into
    # "Purpose"/"Data Authority"/"Supported Operation"/etc. sub-subsections.
    # An earlier version collected headings at any depth under Interfaces
    # and External Contracts, reporting those breakdown headings as five
    # more bogus "interfaces" alongside the one real one. Only immediate
    # children (level == section level + 1) are collected now.
    d = tmp_fixture("blackbox_nested_interface_subsections")
    envelope, code = _run_json(capsys, ["blackbox", str(d / "SPEC.md"), "--trace", "none", "--cognitive", "off"])
    assert code == exit_codes.SUCCESS
    comp = envelope["results"]["completeness"]["specification_completeness"]
    assert comp["interface_elements"] == ["Contact Communication Interface"]


def test_blackbox_cognitive_package_excludes_human_only_content(tmp_fixture, capsys):
    d = tmp_fixture("blackbox_host_agent")
    envelope, code = _run_json(capsys, ["blackbox", str(d / "SPEC.md"), "--trace", "none"])
    assert code == exit_codes.SUCCESS
    package = envelope["results"]["completeness"]["specification_completeness"]["cognitive_package"]
    assert "Editorial note" not in package["material"]["interfaces_and_external_contracts"]
    assert package["known_interface_elements"] == ["Web Portal", "Ticket Creation API"]
    assert package["known_requirement_ids"] == ["TICKET-001", "TICKET-002"]
    assert package["context_omitted"]


def test_blackbox_host_agent_input_produces_findings_with_provenance(tmp_fixture, capsys, tmp_path):
    d = tmp_fixture("blackbox_host_agent")
    input_path = tmp_path / "findings.json"
    input_path.write_text(json.dumps(_VALID_HOST_AGENT_INPUT))

    envelope, code = _run_json(
        capsys,
        ["blackbox", str(d / "SPEC.md"), "--trace", "none", "--cognitive", "auto", "--cognitive-input", str(input_path)],
    )
    assert code == exit_codes.SUCCESS
    assert envelope["cognitive"]["used"] == "host-agent"
    assert envelope["cognitive"]["complete"] is True

    comp = envelope["results"]["completeness"]["specification_completeness"]
    assert "cognitive_package" not in comp
    assert set(comp["io_facilitation_drafts"]) == {"Web Portal", "Ticket Creation API"}
    assert comp["io_facilitation_drafts"]["Ticket Creation API"]["supporting_requirement_ids"] == ["TICKET-002"]

    gap_findings = [f for f in envelope["findings"] if f["rule_id"] == "BBX-003" and "Authentication mechanism" in f["message"]]
    assert len(gap_findings) == 1
    assert gap_findings[0]["reviewers"] == ["host-agent"]
    assert gap_findings[0]["evidence_type"] == "heuristic"


def test_blackbox_host_agent_input_rejects_hallucinated_requirement_citation(tmp_fixture, capsys, tmp_path):
    d = tmp_fixture("blackbox_host_agent")
    payload = json.loads(json.dumps(_VALID_HOST_AGENT_INPUT))
    payload["interfaces"][0]["supporting_requirement_ids"] = ["TICKET-999"]  # does not exist
    input_path = tmp_path / "findings.json"
    input_path.write_text(json.dumps(payload))

    envelope, code = _run_json(
        capsys,
        ["blackbox", str(d / "SPEC.md"), "--trace", "none", "--cognitive", "auto", "--cognitive-input", str(input_path)],
    )
    assert code == exit_codes.SUCCESS
    comp = envelope["results"]["completeness"]["specification_completeness"]
    # The bad citation is dropped, but the rest of that interface's entry survives.
    assert comp["io_facilitation_drafts"]["Web Portal"]["supporting_requirement_ids"] == []

    rejection_findings = [f for f in envelope["findings"] if f["rule_id"] == "BBX-004" and "TICKET-999" in f["message"]]
    assert len(rejection_findings) == 1
    assert rejection_findings[0]["severity"] == "warning"
    assert rejection_findings[0]["reviewers"] == ["host-agent"]


def test_blackbox_cognitive_input_with_cognitive_off_is_usage_error(tmp_fixture, capsys, tmp_path):
    d = tmp_fixture("blackbox_host_agent")
    input_path = tmp_path / "findings.json"
    input_path.write_text(json.dumps(_VALID_HOST_AGENT_INPUT))

    code = main(
        [
            "--output-format", "json", "blackbox", str(d / "SPEC.md"),
            "--trace", "none", "--cognitive", "off", "--cognitive-input", str(input_path),
        ]
    )
    assert code == exit_codes.USAGE_ERROR


def test_blackbox_host_agent_input_malformed_json_is_usage_error(tmp_fixture, capsys, tmp_path):
    d = tmp_fixture("blackbox_host_agent")
    input_path = tmp_path / "findings.json"
    input_path.write_text("{not valid json")

    code = main(
        [
            "--output-format", "json", "blackbox", str(d / "SPEC.md"),
            "--trace", "none", "--cognitive", "auto", "--cognitive-input", str(input_path),
        ]
    )
    assert code == exit_codes.USAGE_ERROR
