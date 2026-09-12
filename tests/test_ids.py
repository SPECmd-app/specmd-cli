from specmd.ids import extract_requirement_ids


def test_inline_bold_convention_extracted():
    text = "- **CLI-001:** something must happen.\n- **INV-002:** an invariant.\n"
    assert extract_requirement_ids(text) == ["CLI-001", "INV-002"]


def test_heading_style_convention_extracted():
    text = "### FUN-001 — Required Pages\n\nBody text.\n\n#### LANG-003 — Equivalent Destination\n\nMore text.\n"
    assert extract_requirement_ids(text) == ["FUN-001", "LANG-003"]


def test_heading_style_ids_via_fixture(tmp_fixture):
    d = tmp_fixture("heading_style_ids")
    text = (d / "SPEC.md").read_text()
    ids = extract_requirement_ids(text)
    assert "FUN-001" in ids
    assert "FUN-002" in ids


def test_ids_inside_code_fence_are_ignored():
    text = (
        "Example of the convention:\n\n"
        "```markdown\n"
        "### FUN-999 — Not A Real Requirement\n"
        "```\n\n"
        "- **CLI-001:** a real requirement.\n"
    )
    ids = extract_requirement_ids(text)
    assert "FUN-999" not in ids
    assert "CLI-001" in ids
