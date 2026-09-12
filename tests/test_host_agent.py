import json

import pytest

from specmd import host_agent


def test_load_cognitive_input_passes_through_dict():
    assert host_agent.load_cognitive_input({"interfaces": []}) == {"interfaces": []}


def test_load_cognitive_input_reads_stdin_marker():
    assert host_agent.load_cognitive_input("-", stdin_text='{"interfaces": []}') == {"interfaces": []}


def test_load_cognitive_input_reads_file(tmp_path):
    p = tmp_path / "in.json"
    p.write_text(json.dumps({"interfaces": []}))
    assert host_agent.load_cognitive_input(str(p)) == {"interfaces": []}


def test_load_cognitive_input_missing_file_raises():
    with pytest.raises(host_agent.HostAgentInputError):
        host_agent.load_cognitive_input("/nonexistent/path.json")


def test_load_cognitive_input_malformed_json_raises(tmp_path):
    p = tmp_path / "in.json"
    p.write_text("{not json")
    with pytest.raises(host_agent.HostAgentInputError):
        host_agent.load_cognitive_input(str(p))


def test_load_cognitive_input_non_object_json_raises(tmp_path):
    p = tmp_path / "in.json"
    p.write_text("[1, 2, 3]")
    with pytest.raises(host_agent.HostAgentInputError):
        host_agent.load_cognitive_input(str(p))


def test_validate_and_merge_missing_interface_key_raises():
    with pytest.raises(host_agent.HostAgentInputError):
        host_agent.validate_and_merge(
            {"interfaces": [{"gaps": []}]}, known_requirement_ids=[], known_interface_elements=[]
        )


def test_validate_and_merge_wrong_type_for_gaps_raises():
    with pytest.raises(host_agent.HostAgentInputError):
        host_agent.validate_and_merge(
            {"interfaces": [{"interface": "X", "gaps": "not a list"}]},
            known_requirement_ids=[],
            known_interface_elements=[],
        )


def test_validate_and_merge_drops_unrecognized_requirement_citation_without_failing():
    result = host_agent.validate_and_merge(
        {"interfaces": [{"interface": "X", "supporting_requirement_ids": ["REAL-001", "FAKE-999"]}]},
        known_requirement_ids=["REAL-001"],
        known_interface_elements=["X"],
    )
    assert result.interfaces["X"]["supporting_requirement_ids"] == ["REAL-001"]
    assert len(result.rejected_citations) == 1
    assert "FAKE-999" in result.rejected_citations[0]


def test_validate_and_merge_covered_interface_elements_tracks_names():
    result = host_agent.validate_and_merge(
        {"interfaces": [{"interface": "A"}, {"interface": "B"}]},
        known_requirement_ids=[],
        known_interface_elements=["A", "B", "C"],
    )
    assert result.covered_interface_elements == {"A", "B"}
    assert not ({"A", "B", "C"} <= result.covered_interface_elements)


def test_validate_and_merge_cross_mapping_filters_unrecognized_requirements():
    result = host_agent.validate_and_merge(
        {"requirements_interface_cross_mapping": {"unmatched_requirements": ["REAL-001", "FAKE-999"]}},
        known_requirement_ids=["REAL-001"],
        known_interface_elements=[],
    )
    assert result.cross_mapping["unmatched_requirements"] == ["REAL-001"]
    assert any("FAKE-999" in note for note in result.rejected_citations)
