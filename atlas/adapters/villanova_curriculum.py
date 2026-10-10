"""Observed Villanova VSB catalog sections and reviewed rule interpretations.

No seed data is read. Exact policy fragments are guards on summaries: changed or
missing policy requires review rather than retaining the prior interpretation.
"""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, requirement, slug, text
from atlas.adapters.discovery_common import parse_identity


def parse_program(html, *, pid, title, award, kind, url):
    identity = parse_identity(
        html,
        program_id=pid,
        title=title,
        award=award,
        kind=kind,
        award_terms=("Co-Major",) if kind == "additional_major" else (),
    )
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    if main is None:
        raise ValueError("Villanova main content missing")
    body = text(main)
    source = pid + "-identity"
    courses, rules = {}, []
    root = pid + "-curriculum"
    ai_ml = pid == "villanova-ai-ml-minor"
    co = kind == "additional_major"
    heading = next(
        (h for h in main.find_all("h2") if text(h).startswith("Course Requirements for ")), None
    )
    if heading is None or not (total := re.search(r"\((\d+) Credits\)", text(heading))):
        raise ValueError("Required course section/credit total missing")

    def rule(key, label, **kwargs):
        item = requirement(pid, key, label, source, parent=root, unit="unknown", **kwargs)
        rules.append(item)
        return item

    rules.append(
        requirement(
            pid,
            "curriculum",
            "Local program requirements",
            source,
            credits=int(total[1]),
            unit="unknown",
            summary="Complete the local curriculum and applicable policies below. Published amounts are credits; credit-system normalization remains unverified.",
        )
    )

    def policy(key, fragments, summary, refs=None):
        if any(fragment.casefold() not in body.casefold() for fragment in fragments):
            raise ValueError("Policy changed or missing: " + key)
        return rule(
            key,
            key.replace("-", " ").capitalize(),
            kind="note",
            summary=summary,
            course_ids=refs or [],
            category="other",
        )

    sections = [
        s
        for s in main.find_all("div", class_="paragraph--type--degree-section")
        if s.find("article", class_="node--type-class")
        and not s.find_parent("section", class_="node--type-elective-group")
    ]
    if len(sections) != (1 if ai_ml else 2):
        raise ValueError("Expected required/elective catalog sections missing")
    for idx, section in enumerate(sections):
        refs = []
        for row in section.find_all("article", class_="node--type-class"):
            codecell = row.find("div", class_="col-3")
            namecell = row.find("div", class_="col-7")
            amount = row.find(class_="field--name-field-credits")
            if not codecell or not namecell or amount is None:
                raise ValueError("Incomplete course row")
            code = text(codecell)
            if not re.fullmatch(r"[A-Z]+ \d{4}", code):
                raise ValueError("Unexpected course code: " + code)
            link = codecell.find("a", href=True)
            value = text(amount)
            c = course(
                code,
                text(namecell),
                source,
                urljoin(url, link["href"]) if link else url,
                credits=float(value) if re.fullmatch(r"\d+(?:\.\d+)?", value) else None,
                institution="villanova",
                unit="unknown",
            )
            courses[c["id"]] = c
            refs.append(c["id"])
        if not refs:
            raise ValueError("No source course rows")
        if idx == 0:
            rule("core", "Required courses", course_ids=refs)
        else:
            desc = section.find(class_="field--name-field-degree-section-description")
            match = re.search(
                r"Plus (?:one|Three) \((\d+)\).*?elective", text(desc) if desc else "", re.I
            )
            if not match:
                raise ValueError("Elective choice count missing")
            rule(
                "electives",
                "Analytics and AI electives",
                kind="choose_courses",
                count=int(match[1]),
                course_ids=refs,
                summary="Choose the published number of electives, subject to the alternative and substitution policies below.",
            )
    if ai_ml:
        policy(
            "unique-courses",
            ["three (3) unique MIS courses"],
            "Complete three unique MIS courses; an approved CSC substitution is subject to the separate restriction below.",
        )
        policy(
            "eligibility",
            ["open to all VSB students"],
            "Open to Villanova School of Business students.",
        )
        policy(
            "free-electives",
            ["may also fulfill the free elective requirements"],
            "Minor courses may also satisfy free electives.",
        )
        m = re.search(r"(CSC 1052) \(([^)]+)\)", body)
        if not m:
            raise ValueError("CSC substitution evidence missing")
        c = course(m[1], m[2], source, url, institution="villanova", unit="unknown")
        courses[c["id"]] = c
        # Keep the replacement conditional, not an additional required course.
        policy(
            "programming-substitution",
            [
                "may fulfill MIS 2020 only if",
                "not fulfilling the core Arts and Sciences requirement",
            ],
            "CSC 1052 may replace MIS 2020 only when it is not also fulfilling the core Arts and Sciences requirement.",
            ["villanova-mis-2020", c["id"]],
        )
        policy(
            "excluded-concentration",
            ["Applied Quantitative Finance Concentration", "may not also minor"],
            "Students in the Applied Quantitative Finance concentration may not also complete this minor.",
        )
    else:
        if co:
            m = re.search(r"must be taken in conjunction with a major in (.+?)\.", body)
            if not m:
                raise ValueError("Co-major parent-major restriction missing")
            rule(
                "primary-major",
                "Required primary major",
                kind="note",
                category="other",
                summary="The BBA co-major requires a primary major in " + m[1] + ".",
            )
            policy(
                "major-overlap",
                ["Only one course", "fulfill another VSB major"],
                "At most one co-major course may also satisfy another VSB major.",
            )
            policy(
                "database-alternative",
                ["MIS 3050 or MIS 2030"],
                "The elective listing provides MIS 3050 or MIS 2030 as one three-credit option; they are not two independent elective slots.",
                ["villanova-mis-3050", "villanova-mis-2030"],
            )
            policy(
                "other-approved-electives",
                ["Other Approved Electives"],
                "Catalog exposes an Other Approved Electives entry with no listed courses or approval procedure. This unresolved entry prevents a complete inventory.",
            )
        else:
            policy(
                "unique-courses",
                ["three (3) unique business courses"],
                "Complete three unique business courses for this minor.",
            )
            policy(
                "free-electives",
                ["may also fulfill the free elective requirements"],
                "Minor courses may also satisfy free electives.",
            )
        policy(
            "joint-program-eligibility",
            [
                "For students pursuing both",
                "Master of Science in Business Analytics and Artificial Intelligence",
            ],
            "The following graduate-course options apply to students pursuing both Analytics and AI and the MSBAi program.",
        )
        conditional = []
        for code in ["MSA 8105", "MSA 8110", "MSA 8240"] + (["CSC 4480"] if co else []):
            m = re.search(re.escape(code) + r" \(([^)]+)\)", body)
            if not m:
                raise ValueError("Conditional option missing: " + code)
            c = course(code, m[1], source, url, institution="villanova", unit="unknown")
            courses[c["id"]] = c
            conditional.append(c["id"])
        policy(
            "graduate-elective",
            ["MSA 8105", "may fulfill an Analytics & Artificial Intelligence elective"],
            "For eligible joint-program students, MSA 8105 may satisfy one Analytics and AI elective.",
            ["villanova-msa-8105"],
        )
        policy(
            "graduate-substitutions",
            ["In addition, one of the following", "MSA 8110", "MSA 8240"],
            "For eligible joint-program students, one additional listed substitution may count: "
            + (
                "CSC 4480 or MSA 8110 for MIS 2030; only one of these three courses may count. "
                if co
                else "MSA 8110 for MIS 2030; only one of that pair may count. "
            )
            + "Alternatively, MSA 8240 may replace MIS 3060; only one of that pair may count.",
            conditional[1:] + ["villanova-mis-2030", "villanova-mis-3060"],
        )
        if not co:
            policy(
                "excluded-course",
                ["CSC 4480", "may not fulfill an Analytics & Artificial Intelligence requirement"],
                "CSC 4480 is explicitly ineligible for this minor; the co-major has a different rule.",
            )
        policy(
            "graduate-permission",
            [
                "up to nine credits",
                "permission of the department, graduate programs, and undergraduate programs",
                "cannot apply to undergraduate degree requirements retroactively",
            ],
            "Undergraduates need department, graduate-program and undergraduate-program permission for up to nine graduate credits. Graduate-program application requires relevant approvals. Courses must be taken while undergraduate; they cannot be applied retroactively after degree conferral.",
        )
    identity.update(
        courses=list(courses.values()),
        requirements=rules,
        curriculum_status="partial",
        notes=[
            "Observed catalog curriculum and policy clauses; completeness and source applicability require separate reviewer audit."
        ],
    )
    return identity


def parse_course(html, *, pid, code, url):
    """Exact catalog course identity and prerequisite observation, not full-text export."""
    import hashlib

    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    h = main.find("h1") if main else None
    if h is None or not text(h).startswith(code + ":"):
        raise ValueError("Expected Villanova course heading missing")
    title = text(h).split(":", 1)[1].strip()
    amount = main.find(class_="field--name-field-credits")
    val = amount.find(class_="field__item") if amount else None
    desc = main.find(class_="field--name-field-description")
    pr = main.find(class_="field--name-field-pr")
    pr = pr.find(class_="field__item") if pr else None
    c = course(
        code,
        title,
        "villanova-" + slug(code) + "-catalog",
        url,
        credits=float(text(val)) if val and re.fullmatch(r"\d+(?:\.\d+)?", text(val)) else None,
        institution="villanova",
        unit="unknown",
    )
    c["prerequisites"] = text(pr) if pr else None
    return {
        "id": pid,
        "courses": [c],
        "requirements": [],
        "curriculum_status": "partial",
        "observed_description_digest": hashlib.sha256(text(desc).encode()).hexdigest()
        if desc
        else None,
        "notes": [
            "Course catalog metadata only; description summaries require review. Source :Y prerequisite notation is preserved without interpretation."
        ],
    }
