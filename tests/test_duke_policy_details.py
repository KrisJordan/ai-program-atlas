import pytest
from atlas.adapters.duke_substitution_details import parse
from atlas.requirements import validate_requirements


def fixture():
    def row(code, choices):
        return (
            "<tr><td>"
            + code
            + "</td><td>Pratt ECE students are still required; cannot count for any other requirement; permission number; Dukehub does not recognize.</td><td>"
            + choices
            + "</td></tr>"
        )

    def ul(*items):
        return "<ul>" + "".join("<li>" + i + "</li>" for i in items) + "</ul>"

    options = ul(
        "COMPSCI 231D",
        "COMPSCI 232/MATH 242",
        "BME 244 AND BME 271/ECE 280",
        "BME 271/ECE 280 AND one of these:" + ul("STA 240L", "MATH 230/STA 230"),
        "MATH 371 AND one of these:" + ul("MATH 305", "PHYSICS 264"),
        "Statistics:"
        + ul("STA 210L AND STA 332", "STA 221L AND (STA 332 or STA 360L or STA 402L or STA 602L)"),
        "EGR 224 AND one of these:" + ul("MATH/EGR 238L", "STA 340"),
    )
    return (
        "<main><h1>CS Course Substitutions Guide</h1><p>MUST REQUEST approval. No online courses. once you have approval; can only be used once. STA 360L has been re-numbered to STA 402L.</p><h2>Substitutions for CS Majors</h2><table>"
        + row("COMPSCI 201", "none allowed")
        + row("COMPSCI 210D", ul("COMPSCI 250D"))
        + row("COMPSCI 230", options)
        + row("COMPSCI 270L", ul("(MATH 216 or MATH 218) AND (MATH 202 or MATH 222)"))
        + row("COMPSCI 330", ul("COMPSCI 532"))
        + row("Stats requirement for CompSci BS", ul("BME 244", "PSY 204L and PSY 205L"))
        + "</table></main>"
    )


def test_conditional_pairs_preserve_conjunctions_and_crosslistings():
    x = parse(fixture(), "duke-test", "source", "https://cs.duke.edu/example")
    validate_requirements(x)
    rows = {r["id"]: r for r in x["requirements"]}
    assert x["program_kind"] == "concentration"
    assert rows["duke-ai-guide-options"]["kind"] == "note"
    assert rows["duke-ai-guide-230"]["kind"] == "alternative"
    assert rows["duke-ai-guide-230-3-choice"]["count"] == 1
    assert (
        rows["duke-ai-guide-230-3-anchor"]["parent_id"]
        == rows["duke-ai-guide-230-3-choice"]["parent_id"]
    )
    assert len(rows["duke-ai-guide-bs-statistics-1"]["course_ids"]) == 2
    assert any(c["code"] == "MATH 238L / EGR 238L" for c in x["courses"])
    assert not any(c["code"] == "STA 360L" for c in x["courses"])
    assert all(c["name"] is None for c in x["courses"])
    assert "curriculum_audit" not in x and "last_verified" not in x


def test_observes_changed_choices_and_rejects_missing_scope():
    x = parse(
        fixture().replace("PHYSICS 264", "PHYSICS 265"),
        "duke-test",
        "s",
        "https://cs.duke.edu/example",
    )
    assert any(c["code"] == "PHYSICS 265" for c in x["courses"])
    assert not any(c["code"] == "PHYSICS 264" for c in x["courses"])
    with pytest.raises(ValueError, match="approval/scope"):
        parse(
            fixture().replace("No online courses", "Online courses allowed"),
            "duke-test",
            "s",
            "https://cs.duke.edu/example",
        )
    with pytest.raises(ValueError, match="row inventory"):
        parse(
            fixture().replace("COMPSCI 330", "COMPSCI 331"),
            "duke-test",
            "s",
            "https://cs.duke.edu/example",
        )


def payload(page_name, tabs, published=True):
    import json

    values = []

    def ref(value):
        values.append(value)
        return len(values) - 1

    entries = []
    for name, body in tabs.items():
        entries.append(ref({"name": ref(name), "content": ref("<h1>" + name + "</h1>" + body)}))
    widget = ref({"type": ref("tabs"), "data": ref(entries)})
    ref(
        {
            "name": ref(page_name),
            "published": ref(published),
            "temporaryContent": ref("<h1>Private draft</h1>"),
            "widgets": ref([widget]),
        }
    )
    return '<script id="__NUXT_DATA__" type="application/json">' + json.dumps(values) + "</script>"


def test_published_tab_scope_and_changed_grading_policy():
    from atlas.adapters.duke_public_policies import parse_grades, tab

    name = "C.3.a. Grades"
    body = "<p>no more than two courses passed with D grades. Courses for which a D grade is earned, however, satisfy other requirements. C- or better. No other degree requirements (major, minor, or certificate, including prerequisites) unless by permission of the director of undergraduate studies.</p>"
    html = payload("C.3. Grading & Grade Requirements", {name: body})
    data = parse_grades(html, "duke-test")
    assert len(data["requirements"]) == 2 and data["courses"] == []
    assert all(r["source_id"] == "duke-bulletin-grading" for r in data["requirements"])
    assert "curriculum_audit" not in data
    with pytest.raises(ValueError, match="policy changed"):
        parse_grades(html.replace("two courses", "three courses"), "duke-test")
    with pytest.raises(ValueError, match="page identity"):
        parse_grades(payload("C.3. Grading & Grade Requirements", {name: body}, False), "duke-test")
    with pytest.raises(ValueError, match="tab identity"):
        tab(html, "C.3. Grading & Grade Requirements", "Private draft")


def test_transfer_source_scopes_incoming_and_post_matriculation_rules():
    from atlas.adapters.duke_public_policies import parse_transfer

    page = "C.4. Credit for Courses Taken Elsewhere (Entrance & Transfer Credit)"
    html = payload(
        page,
        {
            "C.4.a. Entrance Credit": "<p>to the extent allowed by the individual departments; B- or better; was not used to meet high school diploma requirements</p>",
            "C.4.b. Transfer Credit for College Students Transferring to Duke": "<p>if approved by the relevant academic unit. A minimum of half of any major, minor, or certificate must be completed at Duke.</p>",
            "C.4.c. Transfer Credit for Courses Taken After Matriculation at Duke": "<p>no more than two courses; limited to four; preapproved by the relevant DUS; C- or better; P/F grading not accepted; no instance more than ten courses; University Registrar</p>",
        },
    )
    data = parse_transfer(html, "duke-test")
    assert len(data["requirements"]) == 5
    assert any("Trinity students and four for Pratt" in r["summary"] for r in data["requirements"])
    with pytest.raises(ValueError, match="policy changed"):
        parse_transfer(html.replace("C- or better", "D or better"), "duke-test")


def test_apps_linked_pool_does_not_import_bs_degree_requirements():
    from atlas.adapters.duke_public_policies import parse_apps_linked_pool
    from test_concentrations_2026 import duke_fixture

    x = parse_apps_linked_pool(duke_fixture(), "duke-apps", "s", "https://cs.duke.edu/example")
    assert len(x["requirements"]) == 1 and x["requirements"][0]["kind"] == "note"
    assert "applicability unresolved" in x["requirements"][0]["title"]
    assert not any(c["code"] == "COMPSCI 201" for c in x["courses"])
    assert all(c["id"] in x["requirements"][0]["course_ids"] for c in x["courses"])
