import pytest
from atlas.adapters.penn_state_minor_followup import parse_directory, parse_faq


def test_psu_directory_requires_minor_identity_and_actual_bulletin_destination():
    h = '<h4>Artificial Intelligence Engineering Minor</h4><p>Joint minor <a href="https://bulletins.psu.edu/undergraduate/colleges/engineering/artificial-intelligence-engineering-minor">Learn more</a></p>'
    x = parse_directory(h)
    assert x["courses"] == [] and x["requirements"][0]["kind"] == "note"
    with pytest.raises(ValueError, match="destination changed"):
        parse_directory(h.replace('engineering-minor">', 'engineering-bs">'))


def test_psu_major_handbook_reference_does_not_supply_minor_list():
    h = '<p id="department">Question</p><p>handbook for each major</p><ul><li><a href="../artificial-intelligence-engineering-bs.aspx">AIE</a></li></ul><p id="prerequisites">Question</p><p>strictly enforced; course substitution</p><p id="override">Question</p><p>LionPATH; assigned advisor</p>'
    x = parse_faq(h)
    assert x["courses"] == [] and len(x["requirements"]) == 2
    assert "No major-to-minor equivalence" in x["requirements"][0]["summary"]
    assert "does not itself waive" in x["requirements"][1]["summary"]
    assert "curriculum_audit" not in x
    with pytest.raises(ValueError, match="destination changed"):
        parse_faq(h.replace("engineering-bs.aspx", "engineering-minor-list.aspx"))


def test_villanova_new_modal_content_requires_inventory_review():
    from test_villanova_curriculum import fixture, load, PIDS

    mod = load(PIDS[2])
    html = fixture(PIDS[2])
    x = mod.parse(html)
    assert x["curriculum_status"] == "partial"
    with pytest.raises(ValueError, match="now contains content"):
        mod.parse(
            html.replace(
                "<span>Total Credits</span>",
                '<span>Total Credits</span><a href="https://example.edu/list">New list</a>',
            )
        )
    with pytest.raises(ValueError, match="missing or duplicated"):
        mod.parse(html.replace('class="modal-title"', 'class="unrelated"'))
