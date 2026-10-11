"""Invented small table rows exercise the official Case policy structure."""

import hashlib
import json
from pathlib import Path

import pytest

from atlas.adapters import case_degree_policies as p
from atlas.db import validate_program


def row(code="TEST 100", credit="3"):
    return f'<tr><td class="codecol"><a class="code" href="/synthetic">{code}</a></td><td>Synthetic course {code}</td><td class="hourscol">{credit}</td></tr>'


def fixture():
    intro = "2023-2024; at least 6 credit hours; minimum of 3 credit hours in each breadth area; Up to 9 credit hours; two Communication-Intensive courses; At least one semester; no more than one semester or two half-semesters; active military service; a single course may be used to satisfy all"
    html = (
        '<h1>Unified General Education Requirements</h1><div id="textcontainer"><p>'
        + intro
        + '</p><table class="tbl_breadthrequirement"><tr><td>Artificial Intelligence</td><td>STEM+N</td><td>A+H and SS+M</td></tr></table>'
    )
    for area in ["Arts & Humanities", "Social Sciences & Management"]:
        html += (
            "<h4>Courses offered by the following units will count as "
            + area
            + '</h4><ul><li>Synthetic subject (TEST)</li></ul><p>Extra approvals</p><ul><li><a class="code">EXTR 100</a></li><li>BARE 380 / ALT 380</li></ul>'
        )
    for i, name in enumerate(p.POOL_NAMES):
        html += (
            "<h4>Courses that satisfy "
            + name
            + '</h4><table class="sc_courselist">'
            + row("TEST " + str(100 + i), "0" if i == 6 else "3")
        )
        if i == 2:
            html += '<tr><td class="codecol"><a class="code" href="/a">BUND 101</a> &amp; <a class="code" href="/b">BUND 102</a></td><td>First synthetic<br/>and Second synthetic</td><td class="hourscol">4</td></tr>'
        if i == 12:
            html += '<tr><td colspan="2">A certified synthetic activity</td><td class="hourscol">0</td></tr>'
        html += "</table>"
    return html + "</div>"


def test_uger_options_sequences_and_zero_credit_wellness():
    data = p.parse_uger(fixture(), "test-case", "BA")
    assert len(data["courses"]) == 15
    assert (
        "BARE 380, ALT 380"
        in next(r for r in data["requirements"] if r["title"] == "Arts & Humanities eligibility")[
            "summary"
        ]
    )
    bundle = next(r for r in data["requirements"] if len(r["course_ids"]) == 2)
    assert bundle["kind"] == "all"
    assert all(c["credits"] is None for c in data["courses"] if c["code"].startswith("BUND"))
    assert next(c for c in data["courses"] if c["code"] == "TEST 106")["credits"] == 0
    assert any(
        r["summary"] == "A certified synthetic activity" and r["kind"] == "note"
        for r in data["requirements"]
    )
    assert (
        next(
            r
            for r in data["requirements"]
            if r["title"] == "Communication-Intensive approved options"
        )["count"]
        == 2
    )
    assert data["curriculum_status"] == "partial" and "curriculum_audit" not in data


def test_changes_are_read_and_pool_order_is_checked():
    result = p.parse_uger(fixture().replace("TEST 100", "TEST 999"), "test", "BS")
    assert any(c["code"] == "TEST 999" for c in result["courses"])
    with pytest.raises(ValueError, match="Wellness duration"):
        p.parse_uger(
            fixture().replace("Half-semester Wellness with", "Semester Wellness with"), "test", "BA"
        )
    with pytest.raises(ValueError, match="classification"):
        p.parse_uger(fixture().replace("STEM+N", "A+H"), "test", "BA")


@pytest.mark.parametrize("award", ["BA", "BS"])
def test_reviewed_degrees_validate_and_separate_school_rules(award):
    pid = "case-western-reserve-university-artificial-intelligence-" + award.lower() + "-degree"
    data = json.loads((Path("data/programs") / (pid + ".json")).read_text())
    validate_program(data)
    assert data["curriculum_status"] == ("partial" if award == "BA" else "complete")
    assert bool(data["curriculum_audit"]["unresolved_requirements"]) == (award == "BA")
    rule = next(
        r
        for r in data["requirements"]
        if r["title"] == ("BA school requirements" if award == "BA" else "AI BS degree minimum")
    )
    assert rule["credits"] == (120 if award == "BA" else 123)
    assert ("90 in arts" in rule["summary"]) == (award == "BA")
    assert any("CSDS 395A" == c["code"] for c in data["courses"])


@pytest.mark.parametrize("url,parser", [(p.DEGREE_URL, p.parse_degree), (p.UGER_URL, p.parse_uger)])
def test_optional_ignored_source_cache(url, parser):
    path = Path(".cache/http") / (hashlib.sha256(url.encode()).hexdigest() + ".body")
    if not path.exists():
        pytest.skip("Optional ignored research cache unavailable")
    for award in ["BA", "BS"]:
        data = parser(path.read_text(), "case-" + award.lower(), award)
        assert data["requirements"] and "curriculum_audit" not in data
        if url == p.UGER_URL:
            assert len(data["courses"]) == 692


def test_degree_numbers_are_parsed_with_award_scope():
    html = """<h1>Bachelor's Degree Requirements</h1><div id="textcontainer">
    <p>At least half the requirements for the major. Major requirements include related work.
    Complete with a cumulative grade point average of no less than 2.000.
    Earn a minimum of 60 credit hours, of which at least 15 must be earned after the student has earned a total of 105 credit hours.
    Students may choose to update their requirements. Study beyond 10 years needs review.</p>
    <p>Candidates for the Bachelor of Science in Artificial Intelligence degree must complete a minimum of 123 credit hours.</p>
    <p>Candidates for the Bachelor of Arts (BA) degree: 120 credit hours; 90 credit hours; 30 credit hours; 300- or 400-level; 2.000. Concurrent students are exempted from six hours.</p>
    <h3>Bachelor of Science with majors</h3><p>Unrelated school rule.</p></div>"""
    bs = p.parse_degree(html, "test", "BS")
    assert bs["requirements"][-1]["credits"] == 123
    changed = p.parse_degree(html.replace("minimum of 123", "minimum of 124"), "test", "BS")
    assert changed["requirements"][-1]["credits"] == 124
    assert p.parse_degree(html, "test", "BA")["requirements"][-1]["credits"] == 120
    with pytest.raises(ValueError, match="BA school"):
        p.parse_degree(html.replace("90 credit hours", "89 credit hours"), "test", "BA")


@pytest.mark.parametrize('award', ['BA', 'BS'])
def test_required_communication_choices_are_not_hidden_under_note(award):
    pid='case-western-reserve-university-artificial-intelligence-'+award.lower()+'-degree'
    data=json.loads((Path('data/programs')/(pid+'.json')).read_text())
    rules={r['id']:r for r in data['requirements']}
    for title,count in [('Academic Inquiry Seminar approved options',1),('Communication-Intensive approved options',2),('Disciplinary Communication approved options',1),('Capstone Project approved options',1)]:
        choice=next(r for r in rules.values() if r['title']==title)
        assert choice['kind']=='choose_courses' and choice['count']==count
        ancestor=rules[choice['parent_id']]
        while True:
            assert ancestor['kind']=='all'
            if not ancestor['parent_id']:break
            ancestor=rules[ancestor['parent_id']]
    policy=next(r for r in rules.values() if r['title']=='Inquiry seminar placement and transfer')
    assert 'Some students for whom English is a second language enter AIQS 120 directly' in policy['summary']
    observed=p.parse_uger(fixture(),pid,award)
    assert next(r for r in observed['requirements'] if r['title']=='Communication sequence and Experience Portfolio')['kind']=='all'
