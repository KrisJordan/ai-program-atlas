"""Observe factual course metadata, without copying catalog descriptions or seed data."""

import hashlib
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, text

COURSE_SOURCE = (
    "https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/courses/"
)


def parse_metadata(html, *, pid, codes):
    soup = BeautifulSoup(html, "html.parser")
    if not any(
        text(h) == "School of Computer Science Courses" for h in soup.find_all(["h1", "h2"])
    ):
        raise ValueError("CMU course directory heading missing")
    year = re.search(r"20\d{2}[-–]20\d{2}\s+Catalog", text(soup))
    if not year:
        raise ValueError("CMU course directory edition missing")
    found = {}
    description_digests = {}
    for block in soup.find_all("dl", class_="courseblock"):
        heading, body = block.find("dt"), block.find("dd")
        if not heading or not body:
            raise ValueError("CMU course block structure changed")
        match = re.fullmatch(r"(\d{2}-\d{3})\s+(.+)", text(heading))
        if not match or match[1] not in codes:
            continue
        code, title = match.groups()
        if code in found:
            raise ValueError("Duplicate CMU course code: " + code)
        # BR, rather than inline links, bounds prerequisite expressions.
        copy = BeautifulSoup(str(body), "html.parser")
        for br in copy.find_all("br"):
            br.replace_with("\n")
        lines = [" ".join(line.split()) for line in copy.get_text(" ", strip=False).splitlines()]
        lines = [line for line in lines if line]
        units = re.fullmatch(r"[^:]+:\s*(\d+(?:\.\d+)?) units", lines[0])
        record = course(
            code,
            title,
            pid + "-course-directory",
            COURSE_SOURCE,
            category="other",
            credits=float(units[1]) if units else None,
        )
        prerequisites = [
            re.sub(r"^Prerequisites?:\s*", "", line)
            for line in lines
            if re.match(r"^Prerequisites?:", line)
        ]
        if len(prerequisites) > 1:
            raise ValueError("Repeated prerequisite field: " + code)
        record["prerequisites"] = prerequisites[0] if prerequisites else None
        description = " ".join(line for line in lines[1:] if not re.match(r"^(?:Prerequisites?|Corequisites?|Course Website):", line))
        description_digests[code] = hashlib.sha256(description.encode()).hexdigest()
        found[code] = record
    if not found:
        raise ValueError("No requested CMU course metadata observed")
    return {
        "id": pid,
        "catalog_year": year[0].split()[0],
        "curriculum_status": "partial",
        "courses": list(found.values()),
        "observed_description_digests": description_digests,
        "requirements": [],
        "notes": [
            "Course metadata observation only. Missing prerequisites are unknown; catalog descriptions and unvisited course-site links are deliberately not copied. Program requirement inventory is a separate source."
        ],
    }
