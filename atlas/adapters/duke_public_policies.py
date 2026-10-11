"""Extract published tab content embedded in ordinary Duke bulletin responses.

Nuxt's public payload contains the current page's published tabs. Only that
page's widgets are read; temporary content and unrelated cached objects are not.
"""

import json
from bs4 import BeautifulSoup
from atlas.adapters.vt_duke_minors import rule

GRADES_URL = "https://undergraduate.bulletins.duke.edu/policies-procedures/grades"
TRANSFER_URL = (
    "https://undergraduate.bulletins.duke.edu/policies-procedures/transfer-entrance-credit"
)
PRATT_URL = "https://undergraduate.bulletins.duke.edu/undergraduate-instruction/pratt-degree"


def text(node):
    return " ".join(node.get_text(" ", strip=True).split())


def tab(html, page_name, tab_name):
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NUXT_DATA__")
    if script is None:
        raise ValueError("Published Duke tab payload missing")
    values = json.loads(script.string)
    pages = [
        x
        for x in values
        if isinstance(x, dict)
        and {"published", "name", "widgets", "temporaryContent"} <= set(x)
        and values[x["name"]] == page_name
    ]
    if len(pages) != 1 or values[pages[0]["published"]] is not True:
        raise ValueError("Published Duke page identity changed")
    found = []
    for ref in values[pages[0]["widgets"]]:
        widget = values[ref]
        if values[widget["type"]] != "tabs":
            continue
        for entry in values[widget["data"]]:
            item = values[entry]
            if values[item["name"]] == tab_name:
                found.append(values[item["content"]])
    if len(found) != 1:
        raise ValueError("Published Duke tab identity changed: " + tab_name)
    result = BeautifulSoup(found[0], "html.parser")
    if not result.find(["h1", "h2"]) or text(result.find(["h1", "h2"])) != tab_name:
        raise ValueError("Duke tab heading changed")
    return result


def require(node, *phrases):
    value = text(node)
    if any(p not in value for p in phrases):
        raise ValueError("Duke policy changed: " + ", ".join(phrases))


def result(pid, source, items):
    return dict(
        id=pid,
        curriculum_status="partial",
        courses=[],
        requirements=[
            rule(pid + "-" + suffix, title, source, summary=summary)
            for suffix, title, summary in items
        ],
    )


def parse_grades(html, pid):
    body = tab(html, "C.3. Grading & Grade Requirements", "C.3.a. Grades")
    require(
        body,
        "no more than two courses passed with D grades",
        "Courses for which a D grade is earned, however, satisfy other requirements",
        "C- or better",
        "No other degree requirements (major, minor, or certificate, including prerequisites)",
        "unless by permission of the director of undergraduate studies",
    )
    return result(
        pid,
        "duke-bulletin-grading",
        [
            (
                "grade-policy",
                "D grades and credential requirements",
                "The bulletin treats D as a low pass that can satisfy other requirements, while limiting D-graded courses to two toward continuation and the 34-course-credit host degree total. This is a general policy, not an invented minimum AI-course grade.",
            ),
            (
                "su-policy",
                "S/U grading for program requirements",
                "A voluntarily S/U-graded course cannot satisfy major, minor or certificate requirements, including prerequisites, without the program DUS permission. S requires work equivalent to C- or better; U gives no credit. This exception requires individual approval, not automatic eligibility.",
            ),
        ],
    )


def parse_transfer(html, pid):
    title = "C.4. Credit for Courses Taken Elsewhere (Entrance & Transfer Credit)"
    entrance = tab(html, title, "C.4.a. Entrance Credit")
    require(
        entrance,
        "to the extent allowed by the individual departments",
        "B- or better",
        "was not used to meet high school diploma requirements",
    )
    incoming = tab(html, title, "C.4.b. Transfer Credit for College Students Transferring to Duke")
    require(
        incoming,
        "if approved by the relevant academic unit",
        "A minimum of half of any major, minor, or certificate must be completed at Duke",
    )
    post = tab(html, title, "C.4.c. Transfer Credit for Courses Taken After Matriculation at Duke")
    require(
        post,
        "no more than two courses",
        "limited to four",
        "preapproved by the relevant DUS",
        "C- or better",
        "P/F grading",
        "not accepted",
        "no instance",
        "more than ten courses",
        "University Registrar",
    )
    return result(
        pid,
        "duke-bulletin-transfer",
        [
            (
                "entrance-policy",
                "Entrance credit is subject to department acceptance",
                "AP, IPC and prematriculation college credit may meet departmental major/minor requirements only to the extent permitted by that department. Prematriculation coursework must meet the published conditions, including B- or better and exclusion of work used for the high-school diploma; acceptance is not inferred for any listed AI course.",
            ),
            (
                "incoming-transfer",
                "Incoming transfer approval and local coursework",
                "For students transferring into Duke, the academic unit must approve transfer courses toward the major/minor/certificate. At least half of each credential must be completed at Duke. This college/school-specific evaluation rule is separate from host-degree residency.",
            ),
            (
                "post-transfer",
                "Post-matriculation transfer approval",
                "Individually arranged transfer courses require advance approval from the subject DUS and appropriate dean, followed by completion and final official transcript review. Limits are two such courses for Trinity students and four for Pratt students; academic-dismissal transfers are limited to two within those totals.",
            ),
            (
                "away-transfer",
                "Study-away transfer limits and approval",
                "GEO-facilitated study away permits up to four credits per semester or eight per year, potentially two more for summer; combined study-away and individually arranged transfers cannot exceed ten courses. Pratt transfers may include at most two engineering courses. Relevant DUS approval, GEO arrangements and final transcript review are required; non-Duke summer programs require GEO approval.",
            ),
            (
                "transfer-grades",
                "Transfer grading and credit equivalence",
                "Post-matriculation transfer courses require C- or better; P/F or equivalent grades are ineligible. The Registrar determines credit equivalence; Duke course credits are not assumed equivalent to semester or quarter hours. Transfer grades do not enter the Duke record/GPA, and work beyond the transfer limit cannot replace an earlier transfer course.",
            ),
        ],
    )


def parse_pratt(html, pid):
    title = "B.4. Pratt School Degree Requirements"
    body = tab(html, title, "B.4.e. Majors, Minors & Certificates")
    require(
        body,
        "Machine Learning & Artificial Intelligence minor",
        "minimum of five technical courses",
        "At least three of the minor courses must be upper-level courses",
        "at most one upper-level elective",
        "No more than one semester of independent study",
        "may not declare any additional majors or minors",
    )
    residency = tab(html, title, "B.4.b. Residence Requirement for Pratt")
    require(residency, "At least 17.0 course credits", "final two semesters", "approved in advance")
    return result(
        pid,
        "duke-pratt-minor-policies",
        [
            (
                "pratt-engineering-minor",
                "Pratt engineering-minor framework",
                "The ML/AI minor is open to engineering and non-engineering students. Engineering minors require at least five technical courses, including at least three upper-level courses. Introductory courses qualify only if they have substantial technical prerequisite content not otherwise covered by the primary major. At most one semester of independent study supervised in the offering unit may count.",
            ),
            (
                "pratt-overlap",
                "Pratt overlap rule — compare program-specific restrictions",
                "The bulletin excludes primary-major courses and substantially equivalent content, but permits at most one topically relevant upper-level elective cross-listed with the primary major. For an area without its own primary major it repeats the major-course exclusion. The ML/AI departmental major(s) no-overlap rule is stricter; no blanket overlap exception is granted by this record.",
            ),
            (
                "pratt-context",
                "Pratt host-degree and declaration context",
                "Pratt students change academic plans through DukeHub; seniors in their final two semesters contact the designated office. Approved IDEAS majors cannot add majors or minors. Pratt host-degree residency requires 17 Duke course credits including the final two semesters, with an approved last-two-course exception after more than four full Duke semesters; these host-degree credits are not additional minor requirements.",
            ),
        ],
    )


TRINITY_SU_URL = "https://trinity.duke.edu/undergraduate/academic-policies/unsatisfactory-satisfactory-grading-option"
TRINITY_TRANSFER_URL = "https://trinity.duke.edu/undergraduate/academic-policies/transfer-credit"


def parse_trinity_su(html, pid):
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("main") or soup
    require(
        body,
        "Courses: Satisfactory / Unsatisfactory Grading Option",
        "relevant major, minor, or certificate program",
        "500 or higher require permission from the instructor",
        "CANNOT SWITCH BACK",
        "only one course credit per semester",
    )
    return result(
        pid,
        "duke-trinity-su",
        [
            (
                "trinity-su-context",
                "Trinity S/U approvals and course eligibility",
                "For Trinity students, the program must permit S/U credit toward its requirements. A course must permit voluntary S/U; courses numbered 500 or higher additionally require instructor permission. Only one voluntary S/U course credit per semester or summer term may be requested, by the withdrawal deadline; the change cannot be reversed. This is not automatic permission for any AI course.",
            )
        ],
    )


def parse_trinity_transfer(html, pid):
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("main") or soup
    require(
        body,
        "Transfer Credit",
        "Departments determine if a transfer course will count",
        "NOT be enrolled at Duke and another institution at the same time",
        "at least four weeks",
        "at least 17 class meetings",
        "D-, D, or D+",
        "third-party",
    )
    return result(
        pid,
        "duke-trinity-transfer",
        [
            (
                "trinity-transfer-context",
                "Trinity individually arranged transfer-course conditions",
                "In addition to department acceptance and prior Dean/DUS approval, individually arranged transfer courses cannot coincide with Duke enrollment, including online Duke courses. Community/junior college work after Duke matriculation is ineligible. Summer courses require at least four weeks and 17 class meetings. A course previously passed at Duke with D-/D/D+ cannot receive replacement transfer credit. Overseas institutional accreditation must be confirmed; third-party transcript arrangements are ineligible. These conditions apply to Trinity students and do not import its general-education curriculum into this credential.",
            )
        ],
    )


def parse_apps_linked_pool(html, pid, source, url):
    from atlas.adapters.concentrations_2026 import parse_duke_concentration

    data = parse_duke_concentration(html, pid, source, url)
    ids = next(r["course_ids"] for r in data["requirements"] if r["id"] == "duke-ai-group-6")
    out = result(
        pid,
        source,
        [
            (
                "linked-public-electives",
                "Public concentration-elective candidates — applicability unresolved",
                "The minor links to this concentration pool. These are the publicly listed concentration candidates including its ML-core options; the source labels the revised concentration for Fall 2026 entrants and points to Stellic for the comprehensive pool. Minor cohort applicability needs clarification. No BS-specific elective count, distribution or exclusion is imposed as a minor requirement.",
            )
        ],
    )
    out["courses"] = [c for c in data["courses"] if c["id"] in ids]
    out["requirements"][0]["course_ids"] = ids
    return out
