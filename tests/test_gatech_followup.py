import pytest
from atlas.adapters.gatech_minor_followup import (
    parse_computing,
    parse_neuroscience,
    parse_program_neuroscience,
)


def test_eligibility_scopes_other_minor_rules_and_detects_changed_year():
    h = "<h4>Policies and Eligibility:</h4><ul><li>good academic standing; CS 1301 or CS 1315 or CS 1371; CS 1331; “B” or higher; Computational Media; Mathematics and Computing; 2021-2022 and later may not select any CS minor; unless accepted</li></ul><p>no longer a minimum remaining credit hour requirement</p>"
    x = parse_computing(h, "gt-test")
    assert len(x["requirements"]) == 3 and not x["courses"]
    assert "curriculum_audit" not in x
    with pytest.raises(ValueError):
        parse_computing(h.replace("2021-2022", "2022-2023"), "gt-test")


def test_neuroscience_crosscheck_observes_amount_without_resolving_minor():
    h = "<p>NEUR 3803. Special Topics in Neuroscience. 3 Credit Hours. NEUR 4740. Neuroethics. 3 Credit Hours.</p>"
    x = parse_neuroscience(h, "gt-test")
    y = parse_neuroscience(h.replace("3 Credit", "4 Credit"), "gt-test")
    assert x["courses"] == [] and x["requirements"][0]["kind"] == "note"
    assert "4 catalog credit hours" in y["requirements"][0]["summary"]
    assert x["requirements"] != y["requirements"]
    with pytest.raises(ValueError):
        parse_neuroscience(h.replace("Neuroethics", "Other"), "gt-test")
    with pytest.raises(ValueError):
        parse_program_neuroscience("<p>Unrelated catalog</p>", "gt-test")
