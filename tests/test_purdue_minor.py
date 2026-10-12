"""Synthetic markup tests. No downloaded university page is stored in the repository."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def adapter(slug):
    spec = importlib.util.spec_from_file_location(
        slug, ROOT / "atlas" / "adapters" / slug / "adapter.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bs_fixture():
    # Invented course titles, real structural patterns; deliberately small.
    return """<h1>Artificial Intelligence Degree Requirements - Fall 2026 to Present</h1>
    <table><caption>Core Requirements (7-8 credits)</caption>
    <tr><th>Course</th><th>Title</th><th>Credits</th></tr>
    <tr><td><a href="/cs">CS 17600</a></td><td>Example Computing</td><td>3</td></tr>
    <tr><td><a href="/ma1">MA 26100</a> or <a href="/ma2">MA 27101</a></td>
    <td>Example Mathematics or Example Honors</td><td>4/5</td></tr></table>
    <h3>CS Selective I (6 credits)</h3><p>Choose two:</p><ul>
    <li><a href="/a">CS 43900</a> - Example Visualization</li>
    <li><a href="/b">CS 47700</a> - Example Language OR</li>
    <li><a href="/c">CS 57700</a>* - Example Language</li></ul>
    <h3>CS Selective II (3 credits)</h3><p>Choose one:</p><ul>
    <li><a href="/d">CS 34800</a> - Example Systems</li></ul>
    <h3>Philosophy Selective (3 credits)</h3><p>Choose one:</p><ul>
    <li><a href="/e">PHIL 25501</a> - Example Philosophy</li></ul>
    <h3>Capstone Requirement for Artificial Intelligence CS Majors (Fall 2026 - present)</h3>
    <p>CS 37300, CS 38100, and CS 47100: C or better before capstone.</p><ul>
    <li><a href="/f">CS 47600</a> - Example Capstone Credit Hours: 3.00 or</li>
    <li>Pre-approved unpaid research Credits: 3.00 or</li>
    <li>Pre-approved honors project Credits: 3.00 or</li>
    <li>Pre-approved AI Forge project Credits: 3.00</li></ul>"""


def minor_fixture():
    return """<p>2026-2027 edition of the Undergraduate Bulletin</p>
    <h1>Artificial Intelligence Engineering, Minor</h1>
    <p>C or better; at least six credits must be unique.</p>
    <p>Entrance: (CMPSC 121 and DS 120) or CMPSC 131; CMPSC 122 or CMPSC 132.</p>
    <table class="tbl_programrequirements"><tr><td>Requirements for the Minor</td><td>18</td></tr></table>
    <table class="sc_courselist">
    <tr class="areaheader"><td>Prescribed Courses</td></tr>
    <tr><td><a class="code" href="/course1">A-I 305</a></td><td>Example Foundations</td><td class="hourscol">3</td></tr>
    <tr class="areaheader"><td>Additional Courses</td></tr>
    <tr><td><a class="code" href="/course2">CMPSC 448</a></td><td>Example ML</td><td class="hourscol">3</td></tr>
    <tr class="orclass"><td>or <a class="code" href="/course3">CMPSC 445</a></td><td colspan="2">Example Applied ML</td></tr>
    <tr class="areaheader"><td>Supporting Courses and Related Areas</td></tr>
    <tr><td>Department List electives; at least 3 at the 400-level</td><td class="hourscol">6</td></tr></table>"""


def test_bs_extracts_credit_alternatives_and_nested_nlp():
    data = adapter("purdue-ai-bs").parse(bs_fixture())
    courses = {c["code"]: c for c in data["courses"]}
    assert courses["MA 26100"]["credits"] == 4
    assert courses["MA 27101"]["credits"] == 5
    assert courses["CS 43900"]["credits"] is None  # group total is not individual evidence
    core = next(r for r in data["requirements"] if r["id"].endswith("-core"))
    assert core["credits"] is None  # never collapse a range
    assert core["course_ids"] == ["purdue-cs-17600"]
    nlp = next(r for r in data["requirements"] if r["id"].endswith("-nlp-alternative"))
    assert nlp["kind"] == "alternative" and nlp["count"] == 1
    assert nlp["parent_id"].endswith("-cs-selective-i")
    assert len([r for r in data["requirements"] if "capstone-route-" in r["id"]]) == 4
    assert data["catalog_year"] is None
    assert "last_verified" not in data


def test_bs_reads_changed_course_and_selection_count():
    data = adapter("purdue-ai-bs").parse(
        bs_fixture()
        .replace("Example Computing", "Changed Computing")
        .replace("Choose two:", "Choose three:")
    )
    assert data["courses"][0]["name"] == "Changed Computing"
    assert next(r for r in data["requirements"] if r["title"] == "CS Selective I")["count"] == 3


def test_bs_fails_closed_on_unknown_capstone_route():
    with pytest.raises(ValueError, match="Unrecognized capstone"):
        adapter("purdue-ai-bs").parse(
            bs_fixture().replace("AI Forge project", "unknown internship")
        )


def test_minor_keeps_or_row_as_choice_and_unknown_credits():
    data = adapter("penn-state-ai-engineering-minor").parse(minor_fixture())
    assert data["award_level"] == data["program_kind"] == "minor"
    choice = next(r for r in data["requirements"] if r["kind"] == "alternative")
    assert choice["count"] == 1 and len(choice["course_ids"]) == 2
    assert data["courses"][-1]["credits"] is None
    assert data["requirements"][0]["credits"] == 18
    assert data["catalog_year"] == "2026-2027"
    assert data["curriculum_status"] == "partial"


def test_minor_rejects_changed_conjunction():
    with pytest.raises(ValueError, match="conjunction"):
        adapter("penn-state-ai-engineering-minor").parse(
            minor_fixture().replace('class="orclass"', 'class="regular"')
        )


def test_ba_reads_award_and_catalog_url_without_inventing_curriculum():
    html = """<h1>Artificial Intelligence (Liberal Arts)</h1><h3>Quick Facts</h3>
    <ul><li>Degree: Bachelor of Arts</li><li>Location(s): West Lafayette</li></ul>
    <a href="https://catalog.purdue.edu/example">Explore Plan of Study</a>"""
    data = adapter("purdue-ai-ba").parse(html)
    assert data["award_level"] == "BA" and data["curriculum_status"] == "pending"
    assert data["courses"] == data["requirements"] == []
    assert data["links"][1]["url"] == "https://catalog.purdue.edu/example"
    with pytest.raises(ValueError, match="award/campus"):
        adapter("purdue-ai-ba").parse(html.replace("Bachelor of Arts", "Bachelor of Science"))


@pytest.mark.parametrize(
    "slug", ["purdue-ai-bs", "purdue-ai-ba", "penn-state-ai-engineering-minor"]
)
def test_title_alone_cannot_reverify_seed(slug):
    with pytest.raises(ValueError):
        adapter(slug).parse("<h1>Artificial Intelligence</h1>")


def test_curated_seed_references_and_unknowns():
    for slug in ["purdue-ai-bs", "purdue-ai-ba", "penn-state-ai-engineering-minor"]:
        data = json.loads((ROOT / "data" / "programs" / f"{slug}.json").read_text())
        source_ids = {s["id"] for s in data["sources"]}
        course_ids = {c["id"] for c in data["courses"]}
        requirement_ids = {r["id"] for r in data["requirements"]}
        assert data["first_offered"] is None
        assert data["verification_status"] == ("confirmed" if slug == "purdue-ai-ba" else "partial")
        assert len(course_ids) == len(data["courses"])
        for row in data["courses"] + data["requirements"] + data["outcomes"]:
            assert row["source_id"] in source_ids
        for req in data["requirements"]:
            assert set(req["course_ids"]) <= course_ids
            assert req["parent_id"] is None or req["parent_id"] in requirement_ids


def subject_fixture(credits=3, prerequisite="EXAMPLE 100 or EXAMPLE 200"):
    return f"""<h1>Electrical Engineering (EE)</h1><div class="courseblock">
    <div class="course_codetitle">EE 456: Example Neural Course</div>
    <div class="course_code"><span>EE</span><span>456</span></div>
    <div class="course_credits">{credits} Credits</div>
    <div class="courseblockextra">Enforced Prerequisite at Enrollment: {prerequisite}</div>
    <div class="courseblockdesc">Synthetic long description not copied into observation.</div></div>"""


def test_subject_metadata_reads_changed_credit_and_prerequisite():
    module = adapter("penn-state-ai-engineering-minor")
    course = module.parse_ee(subject_fixture(4, "EXAMPLE 300"))["courses"][0]
    assert course["credits"] == 4
    assert course["prerequisites"] == "EXAMPLE 300"
    assert course["description"] is None
    assert course["name"] == "Example Neural Course"
    assert "search/" not in course["url"]
    with pytest.raises(ValueError, match="blocks missing"):
        module.parse_ee(subject_fixture().replace("456", "457"))
    with pytest.raises(ValueError, match="credit format"):
        module.parse_ee(subject_fixture("1-4"))


def test_ba_department_extracts_totals_without_dividing_course_credits():
    html = """<h1>Artificial Intelligence</h1><h2>Plan of Study</h2>
    <p>The BA in AI degree requires 24 credit hours in philosophy, with an additional 15 credit hours in CS.</p>
    <ul><li>CS 10100: Example Digital</li><li>CS 17600: Example Python</li>
    <li>CS 18000: Example Programming</li><li>CS 18200: Example Foundations</li>
    <li>CS 24300: Example AI</li></ul>"""
    module = adapter("purdue-ai-ba")
    data = module.parse_department(html)
    assert data["curriculum_status"] == "partial"
    assert [r["credits"] for r in data["requirements"]] == [24, 15]
    assert all(c["credits"] is None for c in data["courses"])
    assert data["requirements"][0]["course_ids"] == []
    changed = module.parse_department(html.replace("24 credit", "27 credit"))
    assert changed["requirements"][0]["credits"] == 27
    with pytest.raises(ValueError, match="totals"):
        module.parse_department(html.replace("24 credit hours", "many credit hours"))


def test_college_core_observation_does_not_invent_choices_or_add_credits():
    html = """<h1>College of Science Core Curriculum Requirements</h1>
    <p>The core requires the completion of approved coursework and/or experiences.</p>
    <ul><li><a href="/math">Mathematics</a></li><li><a href="/writing">Written Communication</a></li></ul>"""
    data = adapter("purdue-ai-bs").parse_college_core(html)
    assert len(data["requirements"]) == 3
    assert all(r["credits"] is None and not r["course_ids"] for r in data["requirements"])
    assert all(r["parent_id"] == "purdue-ai-bs-college-core" for r in data["requirements"][1:])
    assert data["curriculum_status"] == "partial"
    assert "curriculum_audit" not in data


def test_reviewed_partial_audits_preserve_exact_gaps():
    from atlas.db import validate_program

    for slug in ["purdue-ai-bs", "purdue-ai-ba", "penn-state-ai-engineering-minor"]:
        data = json.loads((ROOT / "data" / "programs" / f"{slug}.json").read_text())
        validate_program(data)
        assert data["curriculum_status"] == "partial"
        assert data["curriculum_audit"]["unresolved_requirements"]
        assert data["curriculum_audit"]["scope"] == data["program_kind"]


def test_purdue_writing_pool_excludes_expired_titles_and_keeps_alias():
    html = """<div><h1>Approved courses in Technical Writing and Presenting</h1>
    <p>Approved courses in Technical Writing:</p>
    <p>ENGL 42400: Example Technical Title</p><p>ENGL 42400: Alternate Printed Title</p>
    <p>ENGL 42000: Expired Choice (approval effective through 2024 catalog terms ONLY)</p>
    <p>Approved courses in Technical Presentation:</p><p>PHYS 32300 Example Presentation</p>
    <p>Approved courses in Technical Writing and Technical Presentation:</p>
    <p>COM 21700: Example Combined (formerly COM 49100)</p>
    <p>BIOL 28900: Expired Choice (formerly BIOL 28700, approved Fall, 2007 - Spring, 2017)</p></div>"""
    m = adapter("purdue-ai-bs")
    result = m.parse_writing_courses(html)
    courses = {c["code"]: c for c in result["courses"]}
    assert set(courses) == {"ENGL 42400", "PHYS 32300", "COM 21700"}
    assert courses["ENGL 42400"]["name"] == "Example Technical Title / Alternate Printed Title"
    assert all(c["credits"] is None for c in courses.values())
    assert "ENGL 42000" in {
        c["code"]
        for c in m.parse_writing_courses(html.replace("through 2024", "through 2027"))["courses"]
    }
    assert "Changed Combined" in str(
        m.parse_writing_courses(html.replace("Example Combined", "Changed Combined"))
    )
    with pytest.raises(ValueError, match="pools incomplete"):
        m.parse_writing_courses(
            html.replace("PHYS 32300 Example Presentation", "No approved presentation")
        )


def test_great_issues_title_specific_pool_never_uses_level_as_credit():
    html = """<div><h1>Great Issues in Science</h1><table id="example"><thead><tr>
    <th>Subject</th><th>Number</th><th>Keyword/Title</th><th>UCORE</th><th>Semester</th><th>Level</th>
    </tr></thead><tbody><tr><td>HONR - Honors</td><td>39900</td><td>Example A*</td><td></td><td>Fall 2026</td><td>3</td></tr>
    <tr><td>HONR - Honors</td><td>39900</td><td>Example B*</td><td></td><td></td><td>3</td></tr></tbody></table></div>"""
    m = adapter("purdue-ai-bs")
    data = m.parse_great_issues(html)
    assert len({c["id"] for c in data["courses"]}) == 2
    assert {c["code"] for c in data["courses"]} == {"HONR 39900"}
    assert all(c["credits"] is None for c in data["courses"])
    assert (
        m.parse_great_issues(html.replace("Example B*", "Changed Topic*"))["courses"][1]["name"]
        == "Changed Topic"
    )
    with pytest.raises(ValueError, match="table changed"):
        m.parse_great_issues(html.replace("<th>Level</th>", "<th>Credits</th>"))


def test_general_education_actual_count_and_credit_change():
    html = "<div><h1>General Education Requirement</h1><p>Complete by completing three courses (9 credits) from the approved list.</p></div>"
    m = adapter("purdue-ai-bs")
    row = m.parse_general_education(html)["requirements"][0]
    assert (row["count"], row["credits"]) == (3, 9)
    row = m.parse_general_education(html.replace("three courses (9", "four courses (12"))[
        "requirements"
    ][0]
    assert (row["count"], row["credits"]) == (4, 12)


def test_language_options_fail_closed_on_removed_route():
    html = (
        "<div><h1>Fall 2023 and Forward Language and Culture Options</h1>"
        + "".join(
            f"<p><strong>Option {i}:</strong></p><ul><li>Example ({i}) course requirement.</li></ul>"
            for i in range(1, 6)
        )
        + "</div>"
    )
    m = adapter("purdue-ai-bs")
    result = m.parse_language_options(html)
    assert len(result["requirements"]) == 5
    assert "5" in result["requirements"][-1]["summary"]
    assert "curriculum_audit" not in result
    with pytest.raises(ValueError, match="routes changed"):
        m.parse_language_options(html.replace("Option 5:", "Option 6:"))


@pytest.mark.parametrize("slug", ["purdue-ai-ba", "purdue-ai-bs"])
def test_purdue_new_university_competency_is_cohort_rule_not_major_launch(slug):
    html = "<h1>Purdue’s AI competency graduation requirement begins in every undergraduate degree program</h1><p>August 19, 2026</p><p>Beginning with this fall’s incoming class</p><p>Courses range from one to four credit hours each.</p>"
    m = adapter(slug)
    result = m.parse_university_ai(html)
    assert "Fall 2026" in result["requirements"][0]["summary"]
    assert result["requirements"][0]["credits"] is None
    assert "first_offered" not in result
    with pytest.raises(ValueError, match="cohort/credit"):
        m.parse_university_ai(html.replace("Beginning with this fall’s incoming class", "Students"))


def test_purdue_reviewed_college_policies_and_partial_limits():
    bs = json.loads((ROOT / "data/programs/purdue-ai-bs.json").read_text())
    reqs = {r["id"]: r for r in bs["requirements"]}
    assert reqs["purdue-ai-bs-college-core-general-education"]["count"] == 3
    assert "one semester" in reqs["purdue-ai-bs-college-experience-approval"]["summary"]
    assert "not AI" in reqs["purdue-ai-bs-lab-sequence-chemistry"]["summary"]
    assert len(bs["courses"]) >= 96
    assert bs["curriculum_status"] == "partial"
    ba = json.loads((ROOT / "data/programs/purdue-ai-ba.json").read_text())
    reqs = {r["id"]: r for r in ba["requirements"]}
    assert reqs["purdue-ai-ba-area-c"]["credits"] == 9
    assert reqs["purdue-ai-ba-calculus"]["count"] == 1
    assert len(ba["courses"]) == 46  # current catalog, not the older overview
    assert ba["outcomes"][1]["statement_type"] == "career_pathway"
