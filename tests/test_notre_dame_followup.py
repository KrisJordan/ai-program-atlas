import pytest
from atlas.adapters.notre_dame_followup import (
    parse_catalog,
    parse_college,
    inspect_additional_electives,
)


def catalog(n=6):
    def group(title, hours):
        return f'<tr class="areaheader"><td>{title}</td><td>{hours}</td></tr>'

    def row(code, title):
        return f'<tr><td><a class="code" href="/search/?P={code}">{code}</a></td><td>{title}</td><td></td></tr>'

    return (
        '<h1>AI Analytics in Business</h1><table class="sc_courselist">'
        + group("Core Courses", 6)
        + row("ITAO 30100", "Core Example")
        + group(f"AI &amp; Analytics Core Electives (choose {n} credits from ITAO):", 9)
        + row("ITAO 50850", "Elective Example")
        + "<tr><td>Total Hours</td><td>15</td></tr></table>"
    )


def test_catalog_keeps_source_pool_and_subrestriction_as_observations():
    x = parse_catalog(catalog(), "nd-test")
    y = parse_catalog(catalog(3), "nd-test")
    assert len(x["courses"]) == 2 and all(c["credits"] is None for c in x["courses"])
    assert all(r["kind"] == "note" for r in x["requirements"])
    assert x["requirements"][1]["credits"] == 9
    assert "3 credits from ITAO" in y["requirements"][1]["summary"]
    assert x["requirements"][1] != y["requirements"][1]
    assert "curriculum_audit" not in x
    with pytest.raises(ValueError):
        parse_catalog(catalog().replace("from ITAO", "from any subject"), "nd-test")


def test_empty_accordion_is_not_an_empty_approved_pool():
    h = '<div class="accordion"><button>Additional approved electives across Notre Dame</button><div class="accordion__content"></div></div>'
    x = inspect_additional_electives(h, "nd-test")
    assert x["course_ids"] == [] and x["kind"] == "note"
    with pytest.raises(ValueError, match="now present"):
        inspect_additional_electives(
            h.replace('content">', 'content">New approved course'), "nd-test"
        )
    with pytest.raises(ValueError, match="now present"):
        inspect_additional_electives(
            h.replace('content">', 'content"><a href="https://example.edu/list">List</a>'),
            "nd-test",
        )


def test_college_exception_stays_unresolved_and_permission_conditional():
    h = "<p>Pass-Fail. With permission from their academic advisor and approval of the assistant dean, juniors and seniors. Only non-business elective courses; other than the first course taken in a minor track; first six days; irrevocable.</p>"
    x = parse_college(h, "nd-test")
    assert "does not override" in x["requirements"][0]["summary"]
    with pytest.raises(ValueError, match="grading policy"):
        parse_college(h.replace("first six days", "first ten days"), "nd-test")
