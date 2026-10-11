"""Current registrar source observations must not silently resolve catalog conflicts."""

import importlib
import json
from pathlib import Path

import pytest

from atlas.adapters import wpi_policy_followup as p
from atlas.db import validate_program


def test_registrar_table_reads_dates_and_excludes_graduate_table():
    html = """<main><h1>Graduation</h1><table><tr><th>Completion of Degree Requirements</th><th>Application Deadline</th><th>Degree Conferral Date</th></tr><tr><td>Fall Semester</td><td>October 4th</td><td>December</td></tr><tr><td>Spring Semester</td><td>October 4th</td><td>May</td></tr><tr><td>Summer Semester</td><td>July 15th</td><td>August</td></tr></table><table><tr><td>Graduate deadline example</td></tr></table></main>"""
    data = p.parse_graduation(html, "test")
    assert len(data["requirements"]) == 3
    assert (
        "October 7th"
        in p.parse_graduation(html.replace("October 4th", "October 7th"), "test")["requirements"][
            0
        ]["summary"]
    )
    assert data["curriculum_status"] == "partial"
    with pytest.raises(ValueError, match="three"):
        p.parse_graduation(
            html.replace("<tr><td>Summer Semester</td><td>July 15th</td><td>August</td></tr>", ""),
            "test",
        )


def test_bsms_scope_and_no_invented_course_count():
    html = """<h2>BS/MS in Business</h2><p>MBA program is not part of this option. Financial Technology (FinTech) program is not part of it. Accept only graduate credits to double count. Applications reviewed after students completed C-term of their sophomore year. Students enroll once they have been accepted into the graduate program.</p><h2>Other program</h2><p>Different rules</p>"""
    data = p.parse_business_bsms(html, "test")
    assert "no universal" in data["requirements"][0]["summary"]
    assert data["requirements"][0]["count"] is None
    with pytest.raises(ValueError, match="eligibility"):
        p.parse_business_bsms(
            html.replace("only graduate credits", "undergraduate credits"), "test"
        )


@pytest.mark.parametrize(
    "pid,count", [("wpi-ai-bs", 141), ("wpi-business-analytics-applied-ai-bs", 91)]
)
def test_wpi_records_keep_unresolved_conflicts(pid, count):
    data = json.loads((Path("data/programs") / (pid + ".json")).read_text())
    validate_program(data)
    assert len(data["requirements"]) == count
    assert data["curriculum_status"] == "partial"
    unresolved = " ".join(data["curriculum_audit"]["unresolved_requirements"])
    assert "HUA" in unresolved and "October 4" in unresolved
    module = importlib.import_module("atlas.adapters." + pid + ".adapter")
    assert p.GRADUATION_URL in module.SOURCE_PARSERS
