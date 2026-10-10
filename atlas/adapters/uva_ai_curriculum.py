"""Fresh, separately bounded BSCS/BACS concentration observations."""

import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, requirement, slug, text
from atlas.adapters.discovery_common import parse_identity


def parse_concentration(html, *, pid, url, parent_degree):
    identity = parse_identity(
        html,
        program_id=pid,
        title="Artificial Intelligence",
        award="concentration",
        kind="concentration",
    )
    soup = BeautifulSoup(html, "html.parser")
    for n in soup.find_all(["nav", "aside", "footer"]):
        n.decompose()
    main = soup.find("main")
    if main is None:
        raise ValueError("UVA main curriculum missing")
    heading = next(
        (h for h in main.find_all("h2") if text(h) == parent_degree + " AI Concentration"), None
    )
    if heading is None:
        raise ValueError("Expected parent-degree concentration section missing")
    section = []
    for n in heading.next_siblings:
        if getattr(n, "name", None) == "h2":
            break
        if getattr(n, "name", None):
            section.append(str(n))
    section = BeautifulSoup("".join(section), "html.parser")
    body = text(main)
    local = text(section)
    source = pid + "-identity"
    rules = []
    courses = {}
    root = pid + "-curriculum"
    total = re.search(r"four courses \((\d+) credits\)", local)
    if not total:
        raise ValueError("Local course/credit total missing")
    rules.append(
        requirement(
            pid,
            "curriculum",
            "Four-course AI concentration",
            source,
            credits=int(total[1]),
            unit="unknown",
            summary="Four courses: two foundations and two electives. Credit amounts are source credits; unit normalization is unverified.",
        )
    )

    def rule(key, label, **kwargs):
        r = requirement(pid, key, label, source, parent=root, unit="unknown", **kwargs)
        rules.append(r)
        return r

    def policy(key, fragments, summary):
        if any(f not in body for f in fragments):
            raise ValueError("Reviewed policy changed: " + key)
        rule(
            key, key.replace("-", " ").capitalize(), kind="note", category="other", summary=summary
        )

    policy(
        "parent-degree",
        ["under the BA and BS in Computer Science degree programs", "effective Fall 2026"],
        parent_degree
        + " majors may pursue this concentration, effective Fall 2026. This local inventory does not certify the host degree.",
    )
    policy(
        "transcript-and-overlap",
        [
            "transcript, but not on their diploma",
            "can also count for any other major or minor requirement",
        ],
        "The concentration appears on the transcript, not the diploma. Its courses may also count toward other major or minor requirements.",
    )
    if parent_degree == "BSCS":
        policy(
            "declaration",
            ["BSCS Majors: Submit a change of major form to the SEAS office"],
            "Declare by submitting a change-of-major form to SEAS.",
        )
        groups = [
            ("Required Courses", "core", "all", None),
            ("AI Techniques Elective (3 credits)", "techniques", "choose_courses", 1),
            ("AI Applications & Impacts Elective (3 credits)", "applications", "choose_courses", 1),
        ]
    else:
        policy(
            "declaration",
            ["BACS Majors: Choose the concentration via AirTable (when available - coming soon)."],
            "Declare via AirTable when the announced form becomes available; the source still marks this process coming soon.",
        )
        policy(
            "major-overlap",
            [
                "Each course also satisfies a major requirement for the BACS",
                "also satisfy the CS Restricted Electives",
            ],
            "Concentration courses also satisfy BACS requirements; the two core courses satisfy the CS Restricted Electives. No additional courses beyond the host major are required for the concentration.",
        )
        groups = [
            ("AI Concentration Core", "core", "all", None),
            ("AI Concentration Electives", "electives", "choose_courses", 2),
        ]
    for label, key, kind, count in groups:
        h = next((h for h in section.find_all("h3") if text(h) == label), None)
        if h is None:
            raise ValueError("Expected concentration course section missing: " + label)
        ul = None
        preamble = []
        for sibling in h.next_siblings:
            if getattr(sibling, "name", None) in ("h2", "h3", "h4"):
                break
            if getattr(sibling, "name", None) == "ul":
                ul = sibling
                break
            if getattr(sibling, "name", None):
                preamble.append(text(sibling))
        if ul is None:
            raise ValueError("Course list missing: " + label)
        if kind == "choose_courses":
            instruction = " ".join(preamble)
            choice = re.search(r"complete (one|two|three)(?: courses)?", instruction)
            if not choice:
                raise ValueError("Elective choice instruction missing")
            count = {"one": 1, "two": 2, "three": 3}[choice[1]]
        refs = []
        for li in ul.find_all("li", recursive=False):
            a = li.find("a", href=True)
            match = re.fullmatch(r"([A-Z]+ \d{4}) - (.+)", text(a) if a else "")
            if not match:
                raise ValueError("Unrecognized linked course entry")
            copy = BeautifulSoup(str(li), "html.parser")
            for nested in copy.find_all("ul"):
                nested.decompose()
            credits = re.search(r"— (\d+) credits", text(copy))
            amount = int(credits[1]) if credits else None
            topics = li.find("ul")
            names = (
                [
                    text(t).removeprefix("Approved Topic:").strip()
                    for t in topics.find_all("li", recursive=False)
                ]
                if topics
                else [None]
            )
            for topic in names:
                c = course(
                    match[1],
                    match[2] + (": " + topic if topic else ""),
                    source,
                    url,
                    credits=amount,
                    institution="uva",
                    unit="unknown",
                )
                if topic:
                    c["id"] += "-" + slug(topic)
                courses[c["id"]] = c
                refs.append(c["id"])
        if not refs:
            raise ValueError("Empty concentration list")
        rule(
            key,
            label,
            kind=kind,
            count=count,
            course_ids=refs,
            summary="All listed foundation courses."
            if kind == "all"
            else "Choose "
            + str(count)
            + " course(s). Topic-specific entries qualify only for the named topics; alternatives are not all required.",
        )
    if parent_degree == "BACS":
        h = next((h for h in section.find_all("h4") if text(h) == "Special Topics Courses"), None)
        if h is None or "will require manual override" not in local:
            raise ValueError("Special-topic permission rule missing")
        ul = h.find_next_sibling("ul")
        refs = []
        for li in ul.find_all("li", recursive=False) if ul else []:
            match = re.fullmatch(r"(CS 4501): (.+)", text(li))
            if not match:
                raise ValueError("Unrecognized manual-override topic")
            c = course(
                match[1],
                "Special Topics in Computer Science: " + match[2],
                source,
                url,
                institution="uva",
                unit="unknown",
            )
            c["id"] += "-" + slug(match[2])
            courses[c["id"]] = c
            refs.append(c["id"])
        if not refs:
            raise ValueError("Manual-override topic list missing")
        rule(
            "manual-topics",
            "Additional eligible topics with manual override",
            kind="note",
            course_ids=refs,
            summary="These named CS 4501 topics may satisfy the two-course elective category only with departmental manual override. They are not additional required courses; their individual credits are not stated here.",
        )
    else:
        rule(
            "topic-restrictions",
            "Approved special-topic offerings",
            kind="note",
            summary="CS 4501 and MDST 3510 count only for the topics specifically listed in their respective technique or applications categories; generic course enrollment is insufficient.",
        )
    identity.update(
        courses=list(courses.values()),
        requirements=rules,
        curriculum_status="partial",
        notes=[
            "Source-scoped local concentration inventory. Registrar program pages are linked but were inaccessible during review; no automatic completeness or host-degree certification."
        ],
    )
    return identity
