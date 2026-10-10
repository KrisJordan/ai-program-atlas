"""Tufts minor accordion extraction, preserving alternatives and topic identities."""

import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, requirement, slug, text
from atlas.adapters.discovery_common import parse_identity

CODE = r"[A-Za-z]+\s*\d+(?:/(?:[A-Za-z]+\s*)?\d+)*"


def normalize_code(value):
    return "/".join(
        re.sub(r"([A-Za-z]+)\s*(\d+)", lambda m: m[1].upper() + " " + m[2], part)
        for part in value.split("/")
    )


def parse_minor(html, *, pid, title, url, development):
    identity = parse_identity(html, program_id=pid, title=title, award="minor", kind="minor")
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    if main is None:
        raise ValueError("Tufts main content missing")
    body = text(main)
    source = pid + "-identity"
    root = pid + "-curriculum"
    courses = {}
    rules = []
    if not re.search(r"requires (?:taking )?five courses and at least 15 credits", body):
        raise ValueError("Tufts total course and credit policy changed")
    rules.append(
        requirement(
            pid,
            "curriculum",
            "Five courses and at least 15 credits",
            source,
            credits=15,
            unit="unknown",
            summary="Complete five courses and at least 15 source credits, including the alternatives and policies below. Credit-unit normalization remains unknown.",
        )
    )

    def rule(key, label, **kwargs):
        r = requirement(pid, key, label, source, parent=root, unit="unknown", **kwargs)
        rules.append(r)
        return r

    def policy(key, fragments, summary, refs=None):
        if any(f not in body for f in fragments):
            raise ValueError("Tufts policy changed: " + key)
        rule(
            key,
            key.replace("-", " ").capitalize(),
            kind="note",
            summary=summary,
            category="other",
            course_ids=refs or [],
        )

    if development:
        policy(
            "eligibility",
            [
                "open to all undergraduate students in Arts and Sciences and Engineering, including majors in Computer Science, Data Science, and Electrical and Computer Engineering"
            ],
            "Open to all Arts and Sciences and Engineering undergraduates, including CS, Data Science and ECE majors.",
        )
        policy(
            "minimum-grade",
            ["grade of C- or better"],
            "Every course counted for the minor must have a grade of at least C-.",
        )
    else:
        policy(
            "eligibility",
            [
                "except those pursuing a B.S. in Computer Science, Data Science, or Computer Engineering in the School of Engineering or a B.A. or B.S. in Computer Science in the School of Arts and Sciences"
            ],
            "Open to Arts and Sciences and Engineering undergraduates except Engineering BS students in CS, Data Science or Computer Engineering, and Arts and Sciences BA/BS students in CS.",
        )
    labels = [
        "Core Courses (Four Required)" if development else "Core Courses (Three Required)",
        "Elective Courses (Select One)" if development else "Disciplinary Electives (Select Two)",
    ]
    blocks = []
    for label in labels:
        block = next(
            (
                li
                for li in main.find_all("li", class_="accordion-item")
                if li.find("h3") and text(li.find("h3")) == label
            ),
            None,
        )
        if block is None:
            raise ValueError("Required accordion missing: " + label)
        ul = block.find("ul")
        if ul is None:
            raise ValueError("Course list missing: " + label)
        blocks.append(ul)

    def add(label, tail=""):
        label = re.sub(r"^or\s+", "", label)
        match = re.fullmatch("(" + CODE + r")\s*(?:-\s*)?(.+)", label)
        if not match:
            raise ValueError("Unrecognized Tufts course: " + label)
        code = normalize_code(match[1])
        name = match[2].strip()
        amount = re.search(r"\((\d+) credits", tail)
        c = course(
            code,
            name,
            source,
            url,
            credits=int(amount[1]) if amount else None,
            institution="tufts",
            unit="unknown",
        )
        if code in ("CS 150", "CHEM 193", "CHEM 194"):
            c["id"] += "-" + slug(name)
        # Preserve source logic/punctuation rather than guessing omitted parentheses.
        if "credits," in tail:
            c["prerequisites"] = tail.split("credits,", 1)[1].strip()
        courses[c["id"]] = c
        if c["prerequisites"] and (
            "requires" in c["prerequisites"] or "recommends" in c["prerequisites"]
        ):
            rule(
                "preparation-" + slug(code),
                "Published preparation for " + code,
                kind="note",
                category="foundations",
                course_ids=[c["id"]],
                summary="Source preparation statement for "
                + code
                + ": "
                + c["prerequisites"]
                + " Recommended preparation is distinguished from required prior completion; source punctuation is retained.",
            )
        return c["id"]

    core = rule(
        "core",
        labels[0],
        summary="Each following core slot is required; alternatives within one slot satisfy that slot once.",
    )
    for index, li in enumerate(blocks[0].find_all("li", recursive=False), 1):
        strongs = li.find_all("strong")
        value = text(li)
        refs = []
        if not strongs:
            raise ValueError("Core course identity spans missing")
        for n, strong in enumerate(strongs):
            label = text(strong)
            start = value.index(label) + len(label)
            tail = value[
                start : value.index(text(strongs[n + 1]), start)
                if n + 1 < len(strongs)
                else len(value)
            ].strip()
            refs.append(add(label, tail.removesuffix(" or").strip()))
        r = requirement(
            pid,
            "core-slot-" + str(index),
            "Core slot " + str(index),
            source,
            parent=core["id"],
            kind="choose_courses" if len(refs) > 1 else "all",
            count=1 if len(refs) > 1 else None,
            course_ids=refs,
            unit="unknown",
            summary="Choose one alternative." if len(refs) > 1 else "Required course.",
        )
        rules.append(r)
    expected = 4 if development else 3
    if len(blocks[0].find_all("li", recursive=False)) != expected:
        raise ValueError("Core slot inventory changed")
    refs = []
    for li in blocks[1].find_all("li", recursive=False):
        value = text(li)
        if value.startswith("Directed study, research, and thesis"):
            policy(
                "approved-independent-work",
                [
                    "Directed study, research, and thesis courses involving AI, as approved by the minor director"
                ],
                "AI-related directed study, research or thesis may satisfy the disciplinary elective category with minor-director approval; this is an open approval option, not an additional required course.",
            )
            continue
        # The source explicitly offers EE159 as an alternative in one list row.
        for part in re.split(r"\s+or\s+(?=[A-Z]+\s*\d)", value):
            refs.append(add(part))
    if not refs:
        raise ValueError("Elective inventory missing")
    rule(
        "electives",
        labels[1],
        kind="choose_courses",
        count=1 if development else 2,
        course_ids=refs,
        summary="Choose one listed elective."
        if development
        else "Choose two disciplinary electives; approved independent-work options may substitute under the separate approval rule.",
    )
    if not development:
        policy(
            "elective-list-review",
            [
                "Changes to the disciplinary elective list are made in consultation with members of the AI Council"
            ],
            "Changes to the disciplinary elective list are made in consultation with AI Council members from Engineering and Arts and Sciences.",
        )
    identity.update(
        courses=list(courses.values()),
        requirements=rules,
        curriculum_status="partial",
        notes=[
            "Observed program page and all local accordion course rows. Linked checklist forms remain unreviewed; no automatic completeness or host-degree certification. Slash codes represent one cross-listed course observation, not multiple elective slots."
        ],
    )
    return identity
