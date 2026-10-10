import importlib.util
import json
from pathlib import Path

import pytest
from test_five_degree_curricula import delaware_fixture, drexel_fixture
from test_indiana_ai_curriculum import fixture as indiana_fixture

from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = {
    "uc-merced-ai-bs": "<h1>Artificial Intelligence, B.S.</h1>",
    "uc-merced-cse-ai-emphasis": "<h1>Majors, Minors &amp; Programs</h1><ul><li><a>Computer Science and Engineering, B.S.</a><ul><li>Artificial Intelligence Emphasis</li></ul></li></ul>",
    "indiana-cs-ai-specialization": "<h1>Bachelor of Science in Computer Science</h1><h3>Choose a CS specialization</h3><p>Select an area.</p><ul><li>Artificial Intelligence - Study intelligent systems.</li></ul>",
    "wpi-ai-bs": "<h1>Bachelor’s Degree in Artificial Intelligence</h1><p>Bachelor of Science</p>",
    "wpi-business-analytics-applied-ai-bs": "<h1>Bachelor’s Degree in Business Analytics &amp; Applied AI</h1><p>Bachelor of Science</p>",
    "wpi-ai-advanced-methods-concentration": "<h1>Bachelor’s Degree in Artificial Intelligence</h1><p>Bachelor of Science</p><h2>Customize Your Path</h2><p>Choose one of the following concentrations</p><ul><li>Advanced AI Methods and Technologies*</li><li>Robotics</li></ul>",
    "drexel-ai-ml-bs": "<h1>Artificial Intelligence &amp; Machine Learning</h1><p>Degree Awarded: Bachelor of Science (BS)</p>",
    "delaware-ai-engineering-major": "<h1>Explore 150+ majors</h1><h2>All Majors</h2><ul><li><a>Artificial Intelligence Engineering</a></li></ul>",
    "marquette-applied-ai-business-major": "<h1>Applied Artificial Intelligence in Business Major</h1><p>The major requires an additional primary major within the College of Business Administration.</p>",
}


FIXTURES["indiana-cs-ai-specialization"] = indiana_fixture()
FIXTURES["drexel-ai-ml-bs"] = drexel_fixture()
FIXTURES["delaware-ai-engineering-major"] = delaware_fixture()


def load(pid):
    spec = importlib.util.spec_from_file_location(pid, ROOT / "atlas/adapters" / pid / "adapter.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize(
    "pid", [p for p in FIXTURES if not p.startswith("wpi-") and not p.startswith("marquette-")]
)
def test_discovery_observes_identity_without_claiming_curriculum_or_freshness(pid):
    mod = load(pid)
    observed = mod.parse("<main>" + FIXTURES[pid] + "</main>")
    seed = json.loads((ROOT / "data/programs" / (pid + ".json")).read_text())
    validate_program(seed)
    if pid in {"drexel-ai-ml-bs", "delaware-ai-engineering-major"}:
        assert observed["curriculum_status"] == "partial"
        assert observed["courses"] and observed["requirements"]
        assert "last_verified" not in observed and "curriculum_audit" not in observed
        assert seed["curriculum_status"] == "partial"
    elif pid == "indiana-cs-ai-specialization":
        assert observed["courses"] and observed["requirements"]
        assert not {"curriculum_status", "curriculum_audit", "last_verified"} & observed.keys()
        assert seed["curriculum_status"] == "complete"
    else:
        assert observed == {k: seed[k] for k in ("id", "title", "award_level", "program_kind")}
        assert seed["curriculum_status"] == "pending"
        assert not seed["courses"]
    with pytest.raises(ValueError):
        mod.parse("<nav>" + FIXTURES[pid] + "</nav><main><h1>Unrelated</h1></main>")


@pytest.mark.parametrize(
    "pid,old,new",
    [
        (
            "uc-merced-cse-ai-emphasis",
            "Artificial Intelligence Emphasis",
            "Software Engineering Emphasis",
        ),
        ("indiana-cs-ai-specialization", "Artificial Intelligence Specialization", "Student clubs"),
        (
            "wpi-ai-advanced-methods-concentration",
            "Choose one of the following concentrations",
            "Related careers",
        ),
        ("marquette-applied-ai-business-major", "additional primary major", "research project"),
        ("delaware-ai-engineering-major", "Artificial Intelligence Engineering BS", "Artificial Intelligence Engineering MS"),
        ("drexel-ai-ml-bs", "Bachelor of Science (BS)", "Master of Science"),
    ],
)
def test_changed_credential_context_requires_review(pid, old, new):
    with pytest.raises(ValueError):
        load(pid).parse("<main>" + FIXTURES[pid].replace(old, new) + "</main>")


def test_merced_emphasis_cannot_borrow_unrelated_parent_degree():
    html = "<h1>Majors</h1><ul><li><a>Computer Science and Engineering, B.S.</a></li><li><a>Other degree</a><ul><li>Artificial Intelligence Emphasis</li></ul></li></ul>"
    with pytest.raises(ValueError):
        load("uc-merced-cse-ai-emphasis").parse(html)
