import importlib.util
from pathlib import Path

import pytest


def load(slug):
    path = Path(__file__).parents[1] / "atlas" / "adapters" / slug / "adapter.py"
    spec = importlib.util.spec_from_file_location(slug, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_denison_observes_changed_course_not_seed():
    adapter = load("denison-mlai-minor")
    html = """<h1>Requirements for the minor in Machine Learning and Artificial Intelligence</h1>
    <p>The following courses are required to complete the minor:</p>
    <table><tr><td>ML/CS 240</td><td>Introduction to Machine Learning</td></tr>
    <tr><td>ML 499</td><td>Newly Observed Course</td></tr></table>"""
    result = adapter.parse(html)
    assert len(result["courses"]) == 2
    assert result["courses"][1]["code"] == "ML 499"
    assert len(result["requirements"][0]["course_ids"]) == 2
    assert "last_verified" not in result
    with pytest.raises(ValueError):
        adapter.parse("<p>Machine Learning is a research interest.</p>")


def test_furman_rejects_missing_award_and_password_page():
    adapter = load("furman-ai-bs")
    html = '<article><a href="/academics/majors-minors-programs/artificial-intelligence-major/">Artificial Intelligence Major</a><span>Bachelor of Science</span><span>Undergraduate Majors</span></article>'
    result = adapter.parse(html)
    assert result["award_level"] == "BS"
    assert result["status"] == "unknown"
    assert not result["courses"]
    with pytest.raises(ValueError):
        adapter.parse(html.replace("Bachelor of Science", "Master of Science"))
    with pytest.raises(ValueError):
        adapter.parse("<p>This content is password-protected.</p>")
