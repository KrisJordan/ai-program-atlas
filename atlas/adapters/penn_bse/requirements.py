"""Additional degree components observed from Penn's undergraduate program page."""

import re
from atlas.adapters.cmu_bs.common import slug
from .common import list_courses, penn_course, req, text


def enrich_requirements(blocks, observed, source, url):
    required = [
        "Mathematics and Natural Science (7 CUs)",
        "AI Concentrations",
        "Senior Design (2 CU)",
        "Technical Electives (3 CU)",
        "General Electives (8 CUs)",
    ]
    if any(title not in blocks for title in required):
        raise ValueError("Additional Penn degree sections missing or changed")
    pid = observed["id"]
    requirements = observed["requirements"]
    courses = {c["id"]: c for c in observed["courses"]}

    def add(key, title, **kwargs):
        item = req(pid, key, title, source, **kwargs)
        requirements.append(item)
        return item

    body = blocks[required[0]]
    root = add("math-natural-science", required[0], category="mathematics", credits=7)
    items = list_courses(body, source, url, "mathematics")
    if len(items) != 6 or "Natural science [1 CU, no lab requirement]" not in text(body):
        raise ValueError("Penn math/science inventory changed")
    for c in items:
        match = re.fullmatch(r"(.+) or ([A-Z]{2,5} \d{4})", c["name"])
        if match:
            c["name"] = match[1]
            alternative = penn_course(match[2], None, source, url, "mathematics")
            courses[alternative["id"]] = alternative
            add(
                "probability-choice",
                "Probability alternative",
                category="mathematics",
                kind="choose_courses",
                count=1,
                parent=root["id"],
                course_ids=[c["id"], alternative["id"]],
            )
        else:
            root["course_ids"].append(c["id"])
        courses[c["id"]] = c
    if not any(r["id"].endswith("probability-choice") for r in requirements):
        raise ValueError("Penn probability alternative missing")
    add(
        "natural-science",
        "Natural science",
        category="mathematics",
        kind="choose_credits",
        credits=1,
        parent=root["id"],
        summary="One course unit of natural science; no laboratory requirement is specified.",
    )

    body = blocks["AI Concentrations"]
    for phrase in [
        "Concentrations are optional",
        "four courses",
        "Only courses used in the AI Elective category",
    ]:
        if phrase not in text(body):
            raise ValueError("Penn optional concentration rule changed")
    root = add(
        "optional-concentrations",
        "Optional AI concentration",
        kind="note",
        summary="Optional four-course thematic concentration using only AI Elective courses. The page overview implies a concentration choice while this detailed section explicitly makes it optional; advising clarification remains necessary.",
    )
    outer = body.find("ul")
    if not outer:
        raise ValueError("Penn concentration lists missing")
    for li in outer.find_all("li", recursive=False):
        nested = li.find("ul")
        label = (
            "".join(str(node) for node in li.contents if isinstance(node, str)).strip().rstrip(":")
        )
        if not nested or not label:
            raise ValueError("Penn concentration grouping changed")
        items = list_courses(nested, source, url)
        if not items:
            raise ValueError("Penn concentration course list empty")
        # Keep the main requirement-list title when the same code has a different label here.
        for c in items:
            courses.setdefault(c["id"], c)
        add(
            "optional-" + slug(label),
            label + " (if selected)",
            kind="choose_courses",
            count=4,
            parent=root["id"],
            course_ids=[c["id"] for c in items],
            summary="If this optional concentration is selected, complete four courses from this pool using AI Elective slots. This is not an additional degree requirement.",
        )

    body = blocks["Senior Design (2 CU)"]
    if "ESE, CIS or other Penn Engineering senior design courses" not in text(body):
        raise ValueError("Penn senior design policy changed")
    add(
        "senior-design",
        "Senior Design (2 CU)",
        category="applications",
        kind="choose_credits",
        credits=2,
        summary="Complete two course units through ESE, CIS or another Penn Engineering senior-design sequence; the AI program does not provide its own named sequence.",
    )
    body = blocks["Technical Electives (3 CU)"]
    if "Three course units from Engineering, Math, Natural Science" not in text(body):
        raise ValueError("Penn technical elective policy changed")
    links = body.find_all("a", href=True)
    if len(links) != 1:
        raise ValueError("Penn technical elective reference changed")
    add(
        "technical-electives",
        "Technical Electives (3 CU)",
        category="electives",
        kind="choose_credits",
        credits=3,
        summary="Three course units from Engineering, Math, Natural Science or the linked approved technical-elective list: "
        + links[0]["href"]
        + ". The linked list has not been fully mapped.",
    )

    body = blocks["General Electives (8 CUs)"]
    root = add(
        "general-electives", "General Electives (8 CUs)", category="human_context", credits=8
    )
    headings = body.find_all("h5")
    if len(headings) != 2:
        raise ValueError("Penn ethics/cognition sections changed")
    for heading in headings:
        if "Choose at least one of the following" not in text(heading):
            raise ValueError("Penn ethics/cognition choice changed")
        label = text(heading).split(":")[0]
        ul = heading.find_next_sibling("ul")
        if not ul:
            raise ValueError("Penn general-elective pool missing")
        items = list_courses(ul, source, url, "human_context")
        if not items:
            raise ValueError("Penn general-elective pool empty")
        courses.update({c["id"]: c for c in items})
        add(
            slug(label),
            label,
            category="human_context",
            kind="choose_courses",
            count=1,
            parent=root["id"],
            course_ids=[c["id"] for c in items],
            summary="Choose at least one listed course. Individual course-unit values are not stated here.",
        )
    for phrase in [
        "Five course units, including a writing course",
        "Three of these courses must be Social Science or Humanities",
        "2 can be Social Science, Humanities, or Technology in Business",
        "One course unit from free electives",
    ]:
        if phrase not in text(body):
            raise ValueError("Penn general-elective distribution changed")
    ssh = add(
        "social-humanities",
        "Social science / humanities distribution",
        category="human_context",
        credits=5,
        parent=root["id"],
        summary="Five course units including a writing course: three SS/H courses and two SS/H or Technology in Business & Society courses. Approved classifications and writing options require linked degree-policy review.",
    )
    add(
        "ssh-three",
        "Social science or humanities",
        category="human_context",
        kind="choose_courses",
        count=3,
        parent=ssh["id"],
    )
    add(
        "ssh-two",
        "Social science, humanities or Technology in Business & Society",
        category="human_context",
        kind="choose_courses",
        count=2,
        parent=ssh["id"],
    )
    add(
        "writing",
        "Writing course within the distribution",
        category="human_context",
        kind="note",
        parent=ssh["id"],
        summary="Include a writing course among the five SS/H distribution units; not an additional course.",
    )
    add(
        "free-elective",
        "Free elective",
        category="electives",
        kind="choose_credits",
        credits=1,
        parent=root["id"],
    )
    observed["courses"] = list(courses.values())
    observed["notes"] = [
        "All eight primary curriculum accordions observed, including optional concentration pools. Linked approved lists, college-wide completion rules, and the overview/concentration inconsistency remain unresolved; degree curriculum stays partial. Individual course metadata are separate and are not inferred from section totals."
    ]
    return observed
