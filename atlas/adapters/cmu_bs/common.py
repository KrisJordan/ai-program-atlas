"""CMU CourseLeaf observations, never a refresh of the curated seed record."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def text(node):
    return " ".join(node.get_text(" ", strip=True).split())


def requirement(
    pid,
    key,
    title,
    source,
    category="ai_ml",
    kind="all",
    parent=None,
    count=None,
    credits=None,
    course_ids=None,
    summary=None,
    unit="units",
):
    return {
        "id": pid + "-" + key,
        "parent_id": parent,
        "title": title,
        "kind": kind,
        "count": count,
        "credits": credits,
        "credit_unit": unit,
        "category": category,
        "source_id": source,
        "source_text": None,
        "summary": summary or title,
        "course_ids": course_ids or [],
    }


def course(
    code, name, source, url, category="ai_ml", credits=None, institution="cmu", unit="units"
):
    return {
        "id": institution + "-" + slug(code),
        "code": code,
        "name": name,
        "description": None,
        "prerequisites": None,
        "credits": credits,
        "credit_unit": unit,
        "category": category,
        "source_id": source,
        "url": url,
        "public_site": None,
        "syllabus": None,
    }


def parse_catalog(html, *, pid, title, award, kind, source_url, sections):
    """Extract only selected curriculum tables, bounded by real section headings.

    Sections map exact heading to semantic mode. Unknown comment groups are notes,
    not guessed graduation constraints. Composite rows never donate a combined
    credit value to an individual course. The returned partial candidate requires
    review; it contains no last_verified or source fetched_at timestamp.
    """
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main") or soup
    h1 = main.find("h1")
    if not h1 or text(h1) != title:
        raise ValueError("CMU program heading missing or changed")
    year = re.search(r"(20\d{2})[-–](20\d{2})\s+Catalog", soup.get_text(" ", strip=True))
    if not year:
        raise ValueError("CMU catalog edition missing")
    source = pid + "-catalog"
    courses = {}
    requirements = []
    for heading, mode in sections.items():
        node = next((h for h in main.find_all(["h3", "h4"]) if text(h) == heading), None)
        if node is None:
            raise ValueError("CMU curriculum section missing: " + heading)
        tables = []
        for n in node.next_siblings:
            if getattr(n, "name", None) in ("h2", "h3", "h4"):
                break
            if getattr(n, "name", None) == "table" and "sc_courselist" in n.get("class", []):
                tables.append(n)
        if not tables:
            raise ValueError("CMU curriculum table missing: " + heading)
        parent = requirement(
            pid,
            slug(heading),
            heading,
            source,
            category="foundations" if mode == "cs" else "ai_ml",
            kind="note" if mode in ("minor-clusters", "societal") else "all",
            summary=(
                "Choose courses from two distinct technical clusters; each at least 9 units."
                if mode == "minor-clusters"
                else "Choose one course from either societal cluster, at least 9 units."
                if mode == "societal"
                else heading
            ),
        )
        requirements.append(parent)
        for ti, table in enumerate(tables):
            initial = table.find("td")
            label = text(initial) if initial else heading
            choose = bool(re.search(r"\b(one|One)\b", label))
            group = requirement(
                pid,
                slug(heading) + "-table-" + str(ti + 1),
                label,
                source,
                category=parent["category"],
                kind="choose_courses" if choose else "all",
                count=1 if choose else None,
                parent=parent["id"],
            )
            requirements.append(group)
            for row in table.find_all("tr"):
                cells = row.find_all("td", recursive=False)
                codecell = row.find("td", class_="codecol")
                if codecell is None:
                    comment = row.select_one(".courselistcomment")
                    if comment:
                        label = text(comment)
                        if "others as designated" in label.lower():
                            continue
                        choose = (
                            "one" in label.lower()
                            or "1 course" in label.lower()
                            or "cluster" in label.lower()
                        )
                        group = requirement(
                            pid,
                            slug(heading) + "-" + slug(label),
                            label,
                            source,
                            kind=(
                                "note"
                                if mode in ("minor-clusters", "societal")
                                else "choose_courses"
                                if choose
                                else "note"
                            ),
                            count=1
                            if choose and mode not in ("minor-clusters", "societal")
                            else None,
                            parent=parent["id"],
                        )
                        requirements.append(group)
                    continue
                links = codecell.find_all("a")
                if len(links) != 1 or len(cells) < 2:
                    continue  # composite probability alternatives are deliberately unparsed
                code = text(links[0])
                if not re.fullmatch(r"\d{2}-\d{3}", code):
                    continue
                name = re.split(r"\s*\((?:students|if)\b", text(cells[1]), maxsplit=1)[0].strip()
                hours = row.select_one(".hourscol")
                value = text(hours) if hours else ""
                credits = float(value) if re.fullmatch(r"\d+(\.\d+)?", value) else None
                item = course(
                    code,
                    name,
                    source,
                    urljoin(source_url, links[0].get("href", "")),
                    parent["category"],
                    credits,
                )
                courses[item["id"]] = item
                if mode == "minor-core" and code not in ("07-280", "07-380"):
                    # Probability alternatives are one requirement, not six required courses.
                    prob = next((r for r in requirements if r["id"] == pid + "-probability"), None)
                    if prob is None:
                        prob = requirement(
                            pid,
                            "probability",
                            "Probability",
                            source,
                            category="mathematics",
                            kind="choose_courses",
                            count=1,
                            parent=parent["id"],
                        )
                        requirements.append(prob)
                    prob["course_ids"].append(item["id"])
                else:
                    group["course_ids"].append(item["id"])
        if not any(r["course_ids"] for r in requirements if r["parent_id"] == parent["id"]):
            raise ValueError("No course rows in " + heading)
    requirements = [
        r
        for r in requirements
        if r["course_ids"] or any(x["parent_id"] == r["id"] for x in requirements)
    ]
    return {
        "id": pid,
        "title": title,
        "award_level": award,
        "program_kind": kind,
        "catalog_year": year.group(1) + "-" + year.group(2),
        "curriculum_status": "partial",
        "courses": list(courses.values()),
        "requirements": requirements,
        "notes": [
            "Observed selected official curriculum tables; mathematics, general education, prerequisites and policy exceptions require review. No curated verification timestamp is renewed by this parser."
        ],
    }
