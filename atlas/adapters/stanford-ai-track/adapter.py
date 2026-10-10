"""Observe the formal AI track in the Stanford undergraduate CS program."""

from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = "stanford-ai-track"
SOURCES = ("https://www.cs.stanford.edu/academics-overview/academics-bachelors-program",)


def parse(html: str) -> dict:
    return parse_identity(
        html,
        program_id=PROGRAM_ID,
        title="Artificial Intelligence (CS BS track)",
        award="concentration",
        kind="concentration",
        aliases=("Artificial Intelligence",),
    )


# These sources govern the AI track's relationship to the parent CS BS.
SHEETS_URL = "https://www.cs.stanford.edu/bs-program-sheets"
DEGREE_URL = "https://www.cs.stanford.edu/bs-degree-requirements"
SOURCES += (SHEETS_URL, DEGREE_URL)


def policy(suffix, title, summary, source_id):
    return {
        "id": PROGRAM_ID + "-" + suffix,
        "parent_id": None,
        "title": title,
        "kind": "note",
        "count": None,
        "credits": None,
        "credit_unit": "units",
        "category": "other",
        "source_id": source_id,
        "source_text": None,
        "summary": summary,
        "course_ids": [],
    }


def parse_sheets(html: str) -> dict:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    normalize = lambda node: " ".join(node.get_text(" ", strip=True).split())
    title = soup.find("h1")
    body = normalize(soup)
    if title is None or normalize(title) != "BS | Program Sheets":
        raise ValueError("Stanford program sheet heading missing")
    guards = [
        "Artificial Intelligence (AI)",
        "year they matriculated",
        "not allowed to mix requirements",
        "there is no double-counting",
        "letter grade except",
        "Spring 2019-20",
        "Autumn 2020-21 through Summer 2020-21",
        "at least one quarter prior",
        "approved program sheets",
        "meet all the requirements for one CS track",
        "petition for exceptions or deviations",
    ]
    if any(g not in body for g in guards):
        raise ValueError("Program sheet track policies changed")
    sid = PROGRAM_ID + "-program-sheets"
    rows = [
        policy(
            "sheet-year",
            "Program-sheet year selection",
            "Use a program sheet from the matriculation year or later; requirements from different sheets cannot be mixed.",
            sid,
        ),
        policy(
            "letter-grades",
            "Letter-grade requirement and historical exceptions",
            "Program-sheet courses require letter grades except Spring 2019–20 and Autumn 2020–21 through Summer 2020–21.",
            sid,
        ),
        policy(
            "category-overlap",
            "No category double-counting",
            "A program-sheet course may count under only one category; separate CS degree rules identify Writing in the Major exceptions unrelated to AI depth.",
            sid,
        ),
        policy(
            "approval",
            "Program-sheet approval",
            "Submit planned/completed courses with units for approval at least one quarter before expected graduation. Only approved sheets proceed to Engineering graduation review; special registration status also requires an approved sheet.",
            sid,
        ),
        policy(
            "track-change",
            "Track completion and changes",
            "The AI track belongs to the CS BS. Track changes are allowed, but one full CS track must be satisfied before applying to graduate; notify CS through its track-change form after the Axess request.",
            sid,
        ),
        policy(
            "petitions",
            "Exceptions and deviations",
            "Departures from the published program sheet require a petition for exceptions or deviations; approval is not assumed.",
            sid,
        ),
    ]
    return {"id": PROGRAM_ID, "curriculum_status": "partial", "requirements": rows}


def parse_degree_policies(html: str) -> dict:
    import re

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    body = " ".join(soup.get_text(" ", strip=True).split())
    title = soup.find("h1")
    if title is None or title.get_text(" ", strip=True) != "BS | Degree Requirements":
        raise ValueError("Stanford CS degree policy heading missing")
    gpa = re.search(
        r"minimum (\d+\.\d+) GPA across all Engineering Fundamentals, CS Core, Depth, and Senior Project courses combined",
        body,
    )
    if (
        gpa is None
        or "Depth section has strict minimum requirements for both the number of courses and units"
        not in body
    ):
        raise ValueError("Depth/GPA policy changed")
    sid = PROGRAM_ID + "-degree-policies"
    return {
        "id": PROGRAM_ID,
        "requirements": [
            policy(
                "gpa",
                "Combined CS program GPA",
                f"The parent CS program requires at least {gpa[1]} GPA across Engineering Fundamentals, CS Core, Depth and Senior Project combined; this is not a separately stated AI-track GPA.",
                sid,
            ),
            policy(
                "depth-minima",
                "Depth course and unit minima",
                "Both the depth course-count minimum and unit minimum must be met; the selected program sheet supplies the applicable values and choices.",
                sid,
            ),
        ],
    }


SOURCE_PARSERS = {SHEETS_URL: parse_sheets, DEGREE_URL: parse_degree_policies}


# Separate, officially published spreadsheet linked by the Engineering directory.
# This is not the denied PDF endpoint.
TRACK_SHEET_URL = "https://docs.google.com/spreadsheets/d/1sMzTwXUGyi5F-D7G5ULs5u831t3jSSLN/edit?ouid=104021965496155781544&rtpof=true&sd=true&usp=sharing"
BULLETIN_URL = "https://bulletin.stanford.edu/programs/CS-BS"
SOURCES += (TRACK_SHEET_URL, BULLETIN_URL)


def course_id(code):
    import re

    return "stanford-" + re.sub(r"[^a-z0-9]+", "-", code.lower()).strip("-")


def track_req(
    suffix,
    title,
    kind="note",
    codes=(),
    parent=None,
    count=None,
    credits=None,
    summary="",
    source="track-sheet",
):
    row = policy(suffix, title, summary, PROGRAM_ID + "-" + source)
    row.update(
        kind=kind,
        parent_id=PROGRAM_ID + "-" + parent if parent else None,
        course_ids=[course_id(c) for c in codes],
        count=count,
        credits=credits,
        category="ai_ml",
    )
    return row


def parse_code_list(value, department="CS"):
    """Read shorthand source lists without turning unit annotations into courses."""
    import re

    value = value.replace("Stats", "STATS")
    extra = ["PHIL 151"] if "(or PHIL 151)" in value else []
    value = value.replace("(or PHIL 151)", "")
    value = re.sub(r"\([^)]*\)", "", value)
    codes = []
    for match in re.finditer(
        r"(?:(CS|STATS|ENGR|EE|MS&E|PHIL|PSYCH|APPPHYS|CEE|CME|DATASCI)\s*)?(\d{2,3}[A-Z]*)\b",
        value,
    ):
        department = match[1] or department
        code = department + " " + match[2]
        if code not in codes:
            codes.append(code)
    return list(dict.fromkeys(codes + extra))


def parse_track_sheet(html):
    import re

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="waffle")
    if table is None:
        raise ValueError("Stanford published spreadsheet table missing")
    rows = [
        " ".join(td.get_text(" ", strip=True).split())
        for tr in table.find_all("tr")
        for td in tr.find_all("td", recursive=False)
    ]
    body = " ".join(rows)
    edition = re.search(r"Artificial Intelligence Track (20\d\d-20\d\d) Program Sheet", body)
    depth = re.search(
        r"Depth; Track and Electives \((\d+) units and (seven|\d+) courses minimum\)", body
    )
    if edition is None or depth is None:
        raise ValueError("AI track edition or depth minima missing")

    def find(prefix):
        matches = [r for r in rows if r.startswith(prefix)]
        if len(matches) != 1:
            raise ValueError("Missing/ambiguous track sheet row: " + prefix)
        return matches[0]

    b = find("Track Requirement B :")
    c = find("Track Requirement C :")
    e = find("Track Electives :")
    general = find("General CS Electives :")
    guards = [
        "Two courses, each from a different area",
        "One additional course from the Track Requirement B list",
        "At least three add'l courses",
        "329 (any suffix, with advisor approval)",
        "247 (any suffix)",
        "248 (any suffix)",
        "348 (any suffix)",
        "Students may replace one track elective",
        "Eligible Humanities Electives",
        "provided they were a matriculated student that year",
        "There is no double counting",
        "CS Core, Depth and Senior Project must be approved by the Computer Science office",
        "195 (max 4 units)",
        "293 (for 3+ units)",
        "Core (15 units minimum)",
        "AI Track Core, Depth, and Senior Project (43 units minimum)",
        "At least 3 units of 191",
        "no later than one month prior to the last quarter",
        "initialed/dated by SSO",
    ]
    if any(g not in body for g in guards):
        raise ValueError("AI track choice or policy structure changed")
    areas = re.findall(r"Area [IV]+\)\s*([^:;]*?):?\s*(CS\s+[^;]+)", b)
    if len(areas) != 4:
        raise ValueError("Expected four Track B areas")
    b_pools = [(name.strip(), parse_code_list(codes)) for name, codes in areas]
    c_codes = parse_code_list(c.split("from the following:", 1)[1])
    # A suffix family is an open source-defined option, not a course named CS 329.
    c_codes = [code for code in c_codes if code != "CS 329"]
    e_codes = parse_code_list(e.split("or the following:", 1)[1])
    general_codes = [
        code
        for code in parse_code_list(general.split(":", 1)[1])
        if code not in {"CS 247", "CS 248", "CS 348"}
    ]
    b_codes = list(dict.fromkeys(code for _, pool in b_pools for code in pool))
    electives = list(dict.fromkeys(b_codes + c_codes + e_codes + general_codes))
    codes = list(dict.fromkeys(["CS 221"] + electives))
    courses = [
        {
            "id": course_id(code),
            "code": code,
            "name": None,
            "description": None,
            "prerequisites": None,
            "credits": None,
            "credit_unit": "units",
            "category": "ai_ml" if code in b_codes + c_codes else "electives",
            "source_id": PROGRAM_ID + "-track-sheet",
            "url": TRACK_SHEET_URL,
            "public_site": None,
            "syllabus": None,
        }
        for code in codes
    ]
    requirements = [
        track_req(
            "depth",
            "AI depth: course and unit minima",
            "all",
            count=7 if depth[2] == "seven" else int(depth[2]),
            credits=int(depth[1]),
            summary="Both minima apply to distinct depth courses; satisfy A, B, C and the elective requirement.",
        ),
        track_req("track-a", "Track A", "all", ["CS 221"], "depth"),
        track_req(
            "track-b",
            "Track B: select two different areas",
            "choose_courses",
            parent="depth",
            count=2,
            summary="One course from each of two different areas.",
        ),
    ]
    for i, (name, pool) in enumerate(b_pools):
        requirements.append(
            track_req(
                "track-b-area-" + str(i + 1), name, "choose_courses", pool, "track-b", count=1
            )
        )
    requirements += [
        track_req(
            "track-c",
            "Track C: one additional course",
            "choose_courses",
            b_codes + c_codes,
            "depth",
            count=1,
            summary="Choose one additional B or C course, or an advisor-approved CS 329 suffix course. Do not reuse a course counted elsewhere.",
        ),
        track_req(
            "track-c-suffix",
            "Advisor-approved CS 329 option",
            parent="track-c",
            summary="CS 329 with any suffix requires advisor approval.",
        ),
        track_req(
            "track-electives",
            "At least three additional track electives",
            "choose_courses",
            electives,
            "depth",
            count=3,
            summary=f"Use B, C, general CS or named additional electives. Up to one eligible humanities course may replace one elective. Extra electives may be needed to reach {depth[1]} depth units.",
        ),
        track_req(
            "general-pool",
            "General CS elective pool",
            codes=general_codes,
            parent="track-electives",
            summary="This is an optional pool, not a separately required set. CS 157 or PHIL 151 is one alternative; do not count both as two options.",
        ),
        track_req(
            "general-suffixes",
            "General elective suffix families",
            parent="track-electives",
            summary="Any suffix of CS 247, CS 248 or CS 348 is allowed by the program sheet; these are course families rather than invented individual course records.",
        ),
        track_req(
            "prior-year-electives",
            "Prior-year elective eligibility",
            parent="track-electives",
            summary="A prior-year General CS elective is eligible only if the student was matriculated in that year.",
        ),
        track_req(
            "elective-units",
            "Special elective unit constraints",
            parent="track-electives",
            summary="CS 195 contributes at most four units; CS 293 must be taken for at least three units.",
        ),
        track_req(
            "humanities-substitution",
            "Humanities substitution limit",
            parent="track-electives",
            summary="At most one track elective may come from the Bulletin's eligible humanities pool.",
        ),
        track_req(
            "parent-boundary",
            "Parent CS core and senior project boundary",
            summary=f"The AI sheet places {depth[1]} depth units within 43 combined CS Core/Depth/Senior Project units: core is 15 minimum, senior project at least 3. The host degree has additional requirements outside this concentration inventory.",
        ),
        track_req(
            "depth-transfer",
            "Departmental transfer approval",
            summary="Transfer coursework in CS Core, Depth and Senior Project requires Computer Science office approval.",
        ),
        track_req(
            "sheet-deadline",
            "Current-sheet approval deadline",
            summary="The final sheet is due no later than one month before the last quarter of senior year; obtain the departmental representative signature and petition/initial/date changes.",
        ),
    ]
    return {
        "id": PROGRAM_ID,
        "catalog_year": edition[1],
        "curriculum_status": "partial",
        "courses": courses,
        "requirements": requirements,
    }


def parse_bulletin(html):
    """Read rendered Bulletin regions; unresolved SSR numeric IDs fail closed."""
    import re

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    def region(label):
        for item in soup.find_all(attrs={"role": "region"}):
            heading = soup.find(id=item.get("aria-labelledby"))
            if heading and " ".join(heading.get_text(" ", strip=True).split()) == label:
                return item
        raise ValueError("Bulletin region missing: " + label)

    human = region("Optional Humanities Elective Courses")
    body = " ".join(human.get_text(" ", strip=True).split())
    if "up to one course" not in body or "Cross-listed versions" not in body:
        raise ValueError("Humanities substitution policy changed")
    courses = {}
    # Lowest matching button/span contains one displayed course, not a whole pool.
    for node in human.find_all(["button", "span"]):
        if node.find(["button", "span"]):
            continue
        match = re.fullmatch(
            r"([A-Z&]+)\s*(\d+[A-Z]*):\s*(.+)", " ".join(node.get_text(" ", strip=True).split())
        )
        if not match:
            continue
        code = match[1] + " " + match[2]
        courses[code] = {
            "id": course_id(code),
            "code": code,
            "name": match[3],
            "description": None,
            "prerequisites": None,
            "credits": None,
            "credit_unit": "units",
            "category": "human_context",
            "source_id": PROGRAM_ID + "-bulletin",
            "url": BULLETIN_URL,
            "public_site": None,
            "syllabus": None,
        }
    if not courses:
        raise ValueError("Bulletin course names/codes unresolved; rendered review required")
    row = track_req(
        "humanities-pool",
        "Eligible humanities elective pool",
        codes=list(courses),
        parent="track-electives",
        source="bulletin",
        summary="Optional replacement pool, capped at one track elective; cross-listed versions are acceptable.",
    )
    return {"id": PROGRAM_ID, "courses": list(courses.values()), "requirements": [row]}


SOURCE_PARSERS.update({TRACK_SHEET_URL: parse_track_sheet, BULLETIN_URL: parse_bulletin})

POLICIES_URL = "https://bulletin.stanford.edu/programs/CS-BS/program-policies-uow1t"
TRANSFER_URL = (
    "https://www.cs.stanford.edu/bs-degree-requirements-petitions-deviations-and-transfer-credits"
)
SOURCES += (POLICIES_URL, TRANSFER_URL)


def parse_bulletin_policies(html):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    body = " ".join(soup.get_text(" ", strip=True).split())
    if not all(
        x in body
        for x in [
            "CS-BS - Computer Science (BS)",
            "Grading Policies",
            "D- or better",
            "unless approved exceptions apply",
        ]
    ):
        raise ValueError("Bulletin grade policy changed")
    return {
        "id": PROGRAM_ID,
        "requirements": [
            track_req(
                "passing-grade",
                "Course passing grade",
                source="bulletin-policies",
                summary="Program-sheet courses require D− or better and letter grading, except approved exceptions.",
            )
        ],
    }


def parse_transfer(html):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    body = " ".join(soup.get_text(" ", strip=True).split())
    if not all(
        x in body
        for x in [
            "BS | Petitions, Deviations, & Transfer Credits",
            "second page of the program sheet require approval from the CS department",
            "course-to-course equivalency request form",
            "syllabus",
            "textbook list",
            "does NOT guarantee",
            "at least one quarter before",
        ]
    ):
        raise ValueError("CS transfer/petition requirements changed")
    return {
        "id": PROGRAM_ID,
        "requirements": [
            track_req(
                "transfer-process",
                "Depth transfer and deviation review",
                source="transfer",
                summary="Depth transfer needs CS approval via the course-equivalency form, identifying the Stanford equivalent, external course, timing, units, syllabus and textbook list. Deviations require committee review; petition at least one quarter before applying to graduate, with no approval guarantee.",
            )
        ],
    }


SOURCE_PARSERS.update({POLICIES_URL: parse_bulletin_policies, TRANSFER_URL: parse_transfer})
