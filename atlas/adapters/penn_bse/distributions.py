"""Penn's explicit college category rules, distinct from AI program acceptance."""

import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import content, require_phrases
from atlas.adapters.cmu_bs.common import slug, text
from .common import req, penn_course

PID = "penn-bse-ai"
URL = "https://academics.engineering.upenn.edu/ugrad/student-handbook/"
SID = PID + "-canonical-handbook"
ABROAD = (
    "https://academics.engineering.upenn.edu/ugrad/student-handbook/academic-policies/study-abroad/"
)


def section(root, n, title):
    node = root.find(id="faq_" + str(n))
    if node is None or title not in text(node):
        raise ValueError("Handbook classification missing: " + title)
    return node


def own_text(li):
    copy = BeautifulSoup(str(li), "html.parser").li
    for child in copy.find_all(["ul", "ol"]):
        child.decompose()
    return text(copy)


def parse_distributions(html):
    root = content(html, "Student Handbook")
    courses = {}
    rules = []

    def note(key, title, summary, ids=(), parent=None, category="other"):
        r = req(
            PID,
            "college-" + key,
            title,
            SID,
            kind="note",
            summary=summary,
            course_ids=list(ids),
            parent=parent,
            category=category,
        )
        rules.append(r)
        return r

    def guarded(n, title, key, markers, summary):
        node = section(root, n, title)
        require_phrases(node, markers)
        note(key, title, summary)
        return node

    def pool(prefix, values, category="human_context"):
        refs = []
        for number in re.findall(r"(?<!\d)\d{4}(?!\d)", values):
            c = penn_course(prefix + " " + number, None, SID, URL, category)
            courses[c["id"]] = c
            refs.append(c["id"])
        return refs

    ns = guarded(
        39,
        "Natural Science Courses",
        "natural-science-policy",
        [
            "Freshman Seminar courses can not be used",
            "Any course above 2000 pending approval by faculty committee",
            "Only CIS Majors",
            "CHEM 1012 or CHEM 1151, but not both",
        ],
        "Natural-science category membership is subject to the program worksheet and the subject rules below. Freshman seminars do not qualify. An AI natural-science slot does not require a lab; this category inventory does not add a lab or create an extra course requirement. CIS 3980 is restricted to CIS majors in the source; ARIN applicability is not inferred.",
    )
    ul = ns.find("ul")
    entries = ul.find_all("li", recursive=False) if ul else []
    if len(entries) != 17:
        raise ValueError("Natural-science subject inventory changed")
    # Each subject's finite/open rule is a short factual classification, not an
    # all-courses graduation requirement. Preserve nested exceptions separately.
    for i, li in enumerate(entries):
        label = li.find("strong")
        if label is None:
            raise ValueError("Natural-science subject label missing")
        label = text(label).rstrip(":")
        value = own_text(li)[len(text(li.find("strong"))) :].lstrip(": ")
        note(
            "natural-science-" + slug(label),
            label + " — natural-science category",
            label + ": " + value,
            category="other",
        )
        for j, child in enumerate(li.find_all("ul")):
            for k, item in enumerate(child.find_all("li", recursive=False)):
                value = text(item).removeprefix("Note: ").strip()
                # These are factual credit/eligibility exceptions, not descriptions.
                note(
                    "natural-science-" + slug(label) + f"-exception-{j}-{k}",
                    label + " — exception",
                    value,
                    category="other",
                )
    math = guarded(
        36,
        "Mathematics Courses",
        "math-acceptance",
        [
            "Each department decides which math courses it accepts",
            "Freshman Seminars may not be used",
            "MATH 2400 (discontinued as of Fall 2026)",
        ],
        "College mathematics classification alone does not establish acceptance by the AI major; consult its department. Honors substitutions need department review. Freshman seminars are excluded. The listed duplicate-content groups permit credit for only one course in each group.",
    )
    lists = math.find_all("ul")
    if len(lists) < 2:
        raise ValueError("Math category or mutual-exclusion lists missing")
    for index, li in enumerate(lists[0].find_all("li", recursive=False)):
        note(
            "math-category-" + str(index),
            "Mathematics category rule",
            own_text(li),
            category="mathematics",
        )
    for index, li in enumerate(lists[1].find_all("li", recursive=False)):
        note(
            "math-exclusive-" + str(index),
            "Mutually exclusive mathematics credits",
            "Credit for at most one course from this group: " + text(li),
            category="mathematics",
        )
    free = guarded(
        28,
        "Free Electives",
        "free-elective-scope",
        [
            "unless it is in the No Credit list",
            "may not use courses on this list toward their degree",
        ],
        "University undergraduate courses may satisfy free electives except the explicit no-credit exclusions below. Exclusion is degreewide, not merely exclusion from the free-elective slot. Legacy numbers remain as printed; no conversion to current numbering is inferred.",
    )
    listing = free.find("ul")
    if listing is None:
        raise ValueError("No-credit list missing")
    for index, li in enumerate(listing.find_all("li", recursive=False)):
        note("no-credit-" + str(index), "Degree no-credit exclusion or exception", text(li))
    eng = guarded(
        25,
        "Engineering Courses",
        "engineering-category",
        [
            "all undergraduate and 5000-level graduate courses",
            "2960",
            "2970",
            "2980",
            "EAS courses below 0800",
            "CIS 2620 counts as an Engineering course",
        ],
        "The Engineering category generally covers Penn Engineering undergraduate and 5000-level courses, with the explicit exceptions below. Naval Science 3010 also qualifies. EAS below 0800 is free-elective only; EAS0097 may be a technical elective up to one CU or a free elective. CIS2620 is Engineering for Fall2020 entrants onward. Study-abroad 2970 may count as technical/application focus but not Engineering; 2960 is free elective only, with possible SS by petition; 2980 may be Engineering. The Green Program receives no credit. VIPR1200/1210 and specific BE concentration courses have restricted program applicability, not blanket ARIN eligibility.",
    )
    englist = eng.find("ul")
    if englist is None:
        raise ValueError("Engineering exclusion list missing")
    for index, li in enumerate(englist.find_all("li", recursive=False)):
        note("engineering-exclusion-" + str(index), "Engineering-category exclusion", own_text(li))
    ssh = guarded(
        54,
        "Social Sciences and Humanities Breadth",
        "ssh-classification",
        [
            "any course numbered below 6000",
            "All Departmental-based topics courses must be approved",
            "must use the “SS” or “H” designations according to their cross-listed academic department",
        ],
        "College SS/H subject categories generally apply below 6000, with exceptions below. Subject freshman seminars may qualify; departmental topics need approval. The existing AI breadth applicability conflict remains unresolved; these are classification lists, not an imposed two-plus-two requirement.",
    )
    headings = ssh.find_all("h3")
    expected = [
        "Social Sciences",
        "Humanities",
        "Courses From Academic Programs With All Multi-Listed Courses",
        "Writing Seminar Course",
    ]
    if [text(h) for h in headings] != expected:
        raise ValueError("SSH section inventory changed")
    for label, h in zip(expected[:3], headings[:3]):
        lists = []
        for n in h.next_siblings:
            if getattr(n, "name", None) == "h3":
                break
            if getattr(n, "name", None) == "ul":
                lists.append(n)
        if len(lists) != (1 if label.startswith("Courses From") else 2):
            raise ValueError("SSH subject/individual pools missing")
        for ix, listing in enumerate(lists):
            for j, li in enumerate(listing.find_all("li", recursive=False)):
                value = own_text(li)
                refs = []
                if ix == 1:
                    lead = li.find("strong")
                    if not lead:
                        raise ValueError("SSH named-subject label missing")
                    heading = text(lead)
                    match = re.search(r"\(([A-Z]{2,5})\)", heading) or re.match(
                        r"([A-Z]{2,5})\b", heading
                    )
                    remainder = value[len(heading) :]
                    # Historical HSSC entries contain a year, not a course code.
                    if match and "taken prior" not in remainder:
                        # A parenthesized cross-list is not another course in this subject.
                        refs = pool(match[1], remainder.split("(")[0])
                note(
                    "ssh-" + slug(label) + f"-{ix}-{j}",
                    label + " classification",
                    value,
                    refs,
                    category="human_context",
                )
    note(
        "ssh-multilist-review",
        "Unlisted cross-listed classifications",
        "AFST, AFRC, AAMW, CIMS and GSWS follow their cross-listed department’s SS/H category; entries without a cross-list need case-by-case coordinator review. WRIT follows the separately mapped writing classification list.",
        category="human_context",
    )
    guarded(
        53,
        "Social Science and Humanities Courses Requirement",
        "ssh-exclusions",
        [
            "courses in the business discipline, military science",
            "primarily a study of mathematics or a physical science",
            "substitute up to two",
        ],
        "SS/H excludes business and military-science subjects, primarily mathematical/physical-science courses and primarily skill-training courses, except explicit classified exceptions. Up to two SS/H courses may be substituted with approved TBS courses, subject to the unresolved AI breadth applicability rule. WRIT follows its individual classification.",
    )
    tbs = guarded(
        59,
        "Technology in Business and Society Courses",
        "tbs-policy",
        [
            "substitute up to two",
            "may not be counted as engineering courses",
            "EAS 2420 will no longer count as TBS starting in Spring 2025",
            "OIDD 2340 (.5 cu) is for students in the M&T program only",
        ],
        "At most two approved TBS courses may substitute for SS/H. New unlisted options need OAS/undergraduate-chair review before enrollment. TBS cannot also be classified as Engineering. The TBS page reiterates two SS plus two H and depth/writing; applicability to 37-CU ARIN remains unresolved. EAS2420 ceased qualifying in Spring2025. OIDD2340 is M&T-only; OIDD3990 plus WH1010 combine to one TBS CU for M&T. EAS5050 appears here but is also on the no-credit list: do not resolve that conflict by silently permitting it.",
    )
    listing = tbs.find("ul")
    if listing is None:
        raise ValueError("Approved TBS list missing")
    for index, li in enumerate(listing.find_all("li", recursive=False)):
        lead = li.find("strong")
        if lead is None:
            raise ValueError("TBS subject missing")
        label = text(lead)
        value = own_text(li)[len(label) :].lstrip(": ")
        prefix = re.match(r"([A-Z]{2,5})\b", label)
        refs = []
        if prefix and label != "PFP Free":
            refs = pool(prefix[1], value)
        for cid in refs:
            number = courses[cid]["code"].split()[-1]
            if re.search(number + r" \(\.5 cu\)", value):
                courses[cid]["credits"] = 0.5
        note(
            "tbs-" + str(index),
            label + " — TBS classification",
            label + ": " + value,
            refs,
            category="human_context",
        )
    return dict(
        id=PID,
        courses=list(courses.values()),
        requirements=rules,
        curriculum_status="partial",
        notes=[
            "Category membership does not override ARIN requirements. Lists include conditional and excluded categories as explicitly labeled notes; do not sum option pools. Course names and unstated credits remain null."
        ],
    )


def parse_additional_policies(html):
    root = content(html, "Student Handbook")
    rules = []
    specs = [
        (
            18,
            "Course Load",
            "load",
            [
                "No student should register for fewer than 4 courses",
                "First-semester students are not permitted",
                "Students on probation are limited to a maximum of 4.5 cu",
            ],
            "Normal enrollment is five courses; below4CU or above5.5CU needs advisor sign-off. First-term maximum is5.5CU. Later overloads need good standing,3.0GPA,no incompletes and a per-term request before add deadline;7CU needs a petition and plan. Probation maximum is4.5CU. Summer limits are4CU over11weeks and2CU per short session. These are enrollment rules, not extra degree credits.",
        ),
        (
            30,
            "Graduate-level Courses",
            "graduate-approval",
            ["6000 or higher", "Graduate Group Chair", "50% or more"],
            "Some5000-level courses need advisor/instructor approval;6000+ needs the course-permission form;7000-level also needs graduate-chair and associate-dean signatures. At least half enrolled CUs each term should satisfy the undergraduate degree, and no more than half should be graduate-level. Exceeding the graduate share affects undergraduate financial-aid eligibility.",
        ),
        (
            31,
            "Independent Study",
            "independent-study",
            ["University's Standing Faculty", "2.0 CUs", "not PF"],
            "Independent study needs a standing-faculty supervisor and application by the add deadline; maximum2CU within the undergraduate degree. Internship-based credit must produce an academic product; approved0099 enrollment is1CU graded, not pass/fail. Students must be actively in an Engineering degree/major.",
        ),
        (
            43,
            "Petition for Action",
            "petition",
            ["Core Sub Form", "Petitions Committee"],
            "Requirement deviations need Petition for Action review; engineering/technical elective substitutions also need the departmental Core Sub Form. Degree-rule exceptions go to the affected school(s); other enrollment petitions go to the home school. Final decisions rest with the Petitions Committee.",
        ),
        (
            45,
            "Quaker Consortium",
            "consortium",
            ["Bryn Mawr, Haverford or Swarthmore College", "fall and spring", "grades will appear"],
            "Penn Engineering students may take Bryn Mawr, Haverford or Swarthmore courses in fall/spring through the Quaker Consortium. Grades enter the Penn transcript under the reciprocal credit arrangement. The linked registration instructions require login; no portal was accessed.",
        ),
        (
            9,
            "Advanced Placement",
            "ap-duplicates",
            ["forfeit the AP credit", "waivers do not carry academic credit"],
            "Taking the Penn equivalent forfeits corresponding AP credit. Chemistry lecture AP does not itself supply lab credit; an approved lab-experience waiver removes the lab requirement but supplies no credits. Subject exam/placement equivalencies require the registrar and relevant department; no new blanket ARIN substitution is inferred.",
        ),
    ]
    for n, title, key, markers, summary in specs:
        node = section(root, n, title)
        require_phrases(node, markers)
        rules.append(req(PID, "college-" + key, title, SID, kind="note", summary=summary))
    return dict(id=PID, courses=[], requirements=rules)


def parse_abroad(html):
    root = content(html, "Study Abroad")
    require_phrases(
        root,
        [
            "minimum of 3.0 cumulative GPA",
            "minimum of 7.0 CUs left",
            "Seniors are not eligible",
            "4.5 CUs",
            "all courses taken abroad must be requested through XCAT",
            "grades will be calculated into the cumulative GPA",
        ],
    )
    source = PID + "-study-abroad"
    rules = []
    summaries = [
        (
            "eligibility",
            "Approved study-abroad eligibility",
            "Require good academic/disciplinary standing,3.0 cumulative and prior-term GPA,no prior-term failures/GR,and a plan to resolve I/NR before departure. At least7CU must remain. First-year students and seniors are ineligible for semester abroad; the earliest abroad period is summer after year one. Program approval and advisor sign-off are required.",
        ),
        (
            "approval",
            "Study-abroad course approval",
            "Plan with advisors to finish in eight semesters without forced overload. All abroad courses require XCAT approval and posting; submit a final course list and official return transcript. Courses numbered2980 need a core-substitution request. Penn determines credit equivalence and appropriate requirement slots; approved-program availability is not individual approval.",
        ),
        (
            "load",
            "Study-abroad load and grades",
            "Normally take4–4.5 Penn-equivalent CU. Host-required higher loads and qualifying dual degrees have exceptions; the XCAT section permits up to5.5CU for dual degrees. All abroad courses must appear on the Penn transcript, and grades enter the cumulative GPA. Pass/fail remains subject to Engineering policy and notice to the abroad advisor by5PM ET Friday of the ninth program week.",
        ),
    ]
    for key, title, summary in summaries:
        rules.append(req(PID, "abroad-" + key, title, source, kind="note", summary=summary))
    return dict(id=PID, courses=[], requirements=rules, curriculum_status="partial")


def parse_handbook(html):
    from .canonical_handbook import parse as prior_parse

    observations = [prior_parse(html), parse_distributions(html), parse_additional_policies(html)]
    courses = {}
    rules = []
    for obs in observations:
        for c in obs["courses"]:
            if c["id"] not in courses:
                courses[c["id"]] = c
            else:
                for field in ["name", "credits"]:
                    if courses[c["id"]].get(field) is None and c.get(field) is not None:
                        courses[c["id"]][field] = c[field]
        rules.extend(obs["requirements"])
    return dict(
        id=PID,
        courses=list(courses.values()),
        requirements=rules,
        curriculum_status="partial",
        notes=[
            "Fresh college policies/classifications; unresolved ARIN program/college conflicts need review. No audit or verification timestamp is emitted."
        ],
    )
