from copy import deepcopy

from atlas.curriculum_profile import requirement_profile


def course(cid, category="other", credits=None, unit="unknown"):
    return {"id": cid, "category": category, "credits": credits, "credit_unit": unit}


def group(gid, kind="all", ids=(), parent=None, **kwargs):
    return {"id": gid, "kind": kind, "course_ids": list(ids), "parent_id": parent,
            "title": gid, "source_id": "source", **kwargs}


def test_large_elective_menu_does_not_dominate_required_profile():
    p = {"courses": [course("ai", "ai_ml"), course("gap")]
         + [course(f"e{i}") for i in range(1000)],
         "requirements": [group("core", ids=["ai", "gap"]),
                          group("menu", "choose_courses", [f"e{i}" for i in range(1000)],
                                count=2)]}
    r = requirement_profile(p)
    assert r["required"]["count"] == 2
    assert r["required"]["categories"]["ai_ml"] == 1
    assert r["required"]["categories"]["other"] == 1
    assert r["options"]["count"] == 1000
    assert r["choices"][0]["count"] == 2
    assert r["choices"][0]["context"] == "required"


def test_nested_alternative_bundles_never_select_a_path():
    p = {"courses": [course(c) for c in "abcd"], "requirements": [
        group("routes", "alternative"),
        group("first", ids=["a", "b"], parent="routes"),
        group("second", ids=["a", "c"], parent="routes"),
        group("nested", "choose_courses", ["d"], "second", count=1),
    ]}
    r = requirement_profile(p)
    assert r["required"]["count"] == 0
    assert r["options"]["count"] == 4
    assert r["overlap_count"] == 1
    assert r["choices"][0]["count"] is None  # Never fabricate a choose-one quantity.
    assert r["choices"][1]["context"] == "conditional"


def test_overlap_and_mixed_units_preserve_separate_load_rules():
    p = {"courses": [course("a", "ai_ml", 3, "semester_hours"),
                     course("b", "systems", None), course("c", "mathematics", 6,
                                                          "quarter_hours")],
         "requirements": [group("fixed", ids=["a"]),
                          group("pool1", "choose_courses", ["a", "b"], count=1),
                          group("pool2", "choose_credits", ["b", "c"], credits=6,
                                credit_unit="quarter_hours")]}
    original = deepcopy(p)
    r = requirement_profile(p)
    assert p == original
    assert (r["required"]["count"], r["options"]["count"],
            r["unresolved"]["count"]) == (1, 2, 0)
    assert r["overlap_count"] == 2
    assert [(c["count"], c["credits"], c["credit_unit"]) for c in r["choices"]] == [
        (1, None, "unknown"), (None, 6, "quarter_hours")]
    assert "credits" not in r["required"]


def test_note_ancestry_unbound_and_separate_fixed_occurrence():
    p = {"courses": [course(c) for c in "abcde"], "requirements": [
        group("ambiguous", "note", ["a"]),
        group("context", ids=["b"], parent="ambiguous"),
        group("menu", "choose_courses", ["c"], "ambiguous", count=1),
        group("fixed", ids=["b"]), group("choice", "alternative", ["d"]),
    ]}
    r = requirement_profile(p)
    assert [r[k]["count"] for k in ("required", "options", "unresolved")] == [1, 1, 3]
    assert r["choices"][0]["context"] == "unresolved"
    assert r["unresolved_group_count"] == 3


def test_observed_pool_equal_to_selection_count_still_not_promoted():
    r = requirement_profile({"courses": [course("a")], "requirements": [
        group("partial-open-pool", "choose_courses", ["a"], count=1)]})
    assert r["required"]["count"] == 0
    assert r["options"]["count"] == 1


def test_unknown_category_is_visible_and_no_graph_is_not_zero_curriculum():
    r = requirement_profile({"courses": [course("a", "unmapped")], "requirements": []})
    assert r["required"]["count"] == 0
    assert r["unresolved"]["categories"]["other"] == 1
    assert r["unresolved"]["count"] == 1
