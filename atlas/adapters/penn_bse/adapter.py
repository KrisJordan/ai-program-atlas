"""Observe Penn Engineering's current accordion curriculum; never load seed data."""

import re

from bs4 import BeautifulSoup

from atlas.adapters.cmu_bs.common import slug

from .common import list_courses, req, text
from .requirements import enrich_requirements
from .linked_policies import (
    HANDBOOK,
    INVENTORY,
    faq_requirements,
    parse_technical_policy,
    parse_technical_inventory,
)

SOURCES = ["https://ai.engineering.upenn.edu/academics/undergraduate/"]
PID = "penn-bse-ai"


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    if not h1 or text(h1) != "B.S.E. in AI Curriculum":
        raise ValueError("Penn undergraduate heading missing")
    blocks = {}
    for item in soup.select(".accordion-item"):
        heading = item.find("h2")
        body = item.select_one(".accordion-body")
        if heading and body:
            blocks[text(heading)] = body
    expected = ["Computing (5 CUs)", "AI Core (6 CUs)", "AI Electives (6 CUs)"]
    if any(k not in blocks for k in expected):
        raise ValueError("Penn AI curriculum sections missing or changed")
    source = PID + "-curriculum"
    courses = {}
    requirements = []
    for title in expected:
        body = blocks[title]
        key = slug(title)
        category = "foundations" if title.startswith("Computing") else "ai_ml"
        items = list_courses(body, source, SOURCES[0], category)
        if not items:
            raise ValueError("Penn course list missing: " + title)
        courses.update({c["id"]: c for c in items})
        parent = req(
            PID,
            key,
            title,
            source,
            category=category,
            kind="all" if not title.startswith("AI Electives") else "choose_credits",
            credits=5 if category == "foundations" else 6,
        )
        requirements.append(parent)
        if title.startswith("AI Core"):
            if not re.search(r"at least one course unit from each", text(body), re.IGNORECASE):
                raise ValueError("Penn AI core selection rule changed")
            headings = body.find_all("h5")
            if len(headings) != 6:
                raise ValueError("Expected six Penn AI core areas")
            for heading in headings:
                ul = heading.find_next_sibling("ul")
                if ul is None:
                    raise ValueError("AI core area list missing")
                options = list_courses(ul, source, SOURCES[0])
                if not options:
                    raise ValueError("AI core area empty")
                requirements.append(
                    req(
                        PID,
                        key + "-" + slug(text(heading)),
                        text(heading),
                        source,
                        kind="choose_credits",
                        credits=1,
                        parent=parent["id"],
                        course_ids=[c["id"] for c in options],
                    )
                )
        else:
            parent["course_ids"] = [c["id"] for c in items]
    observed = {
        "id": PID,
        "title": "Artificial Intelligence, BSE",
        "award_level": "BSE",
        "program_kind": "degree",
        "catalog_year": None,
        "curriculum_status": "partial",
        "courses": list(courses.values()),
        "requirements": requirements,
        "notes": [
            "Live program page does not state a catalog edition. Extracted computing, all six AI core areas and AI elective options; other degree components and optional concentrations require review. Course unit values are not inferred for individual courses."
        ],
    }

    result = enrich_requirements(blocks, observed, source, SOURCES[0])
    result["requirements"].extend(faq_requirements(soup))
    from .subjects import classify_observed
    return classify_observed(result)


PROGRAM_ID = "penn-bse-ai"

SOURCES.extend([HANDBOOK, INVENTORY])
SOURCE_PARSERS = {HANDBOOK: parse_technical_policy, INVENTORY: parse_technical_inventory}

from .canonical_handbook import URL as HANDBOOK_URL
from .distributions import parse_handbook as parse_canonical_handbook, ABROAD, parse_abroad

SOURCES.append(HANDBOOK_URL)
SOURCE_PARSERS[HANDBOOK_URL] = parse_canonical_handbook

SOURCES.append(ABROAD)
SOURCE_PARSERS[ABROAD] = parse_abroad

# Shared public course observations, dispatched with the BSE's own program ID.
from atlas.adapters.penn_cs.course_metadata import register_resources
register_resources(PROGRAM_ID, SOURCES, SOURCE_PARSERS)

from .core_resources import register as register_core_resources
register_core_resources(SOURCES, SOURCE_PARSERS)

from .inventory_titles import parse_inventory_with_titles
SOURCE_PARSERS[INVENTORY] = parse_inventory_with_titles

# Apply the same exact identity review to this program's linked inventories.
# Eligibility-list membership and worksheet labels do not classify subjects.
from .subjects import classify_observed as classify_linked_subjects
for _subject_url in [INVENTORY, HANDBOOK_URL]:
    _subject_parser = SOURCE_PARSERS[_subject_url]
    SOURCE_PARSERS[_subject_url] = lambda html, parser=_subject_parser: classify_linked_subjects(parser(html))
