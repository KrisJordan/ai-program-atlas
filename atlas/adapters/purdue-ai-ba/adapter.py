"""Purdue BA admissions identity parser; does not claim catalog coverage."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

PROGRAM_ID = "purdue-ai-ba"

SOURCES = ("https://admissions.purdue.edu/majors/artificial-intelligence/",)


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    if (
        h1 is None
        or " ".join(h1.get_text(" ", strip=True).split())
        != "Artificial Intelligence (Liberal Arts)"
    ):
        raise ValueError("Expected Purdue Liberal Arts AI admissions heading")
    quick = soup.find(re.compile("^h[2-4]$"), string=re.compile(r"^Quick Facts$"))
    if quick is None:
        raise ValueError("Quick Facts missing")
    facts = " ".join(quick.find_next("ul").get_text(" ", strip=True).split())
    if "Degree: Bachelor of Arts" not in facts or "West Lafayette" not in facts:
        raise ValueError("BA award/campus not confirmed by Quick Facts")
    plan = soup.find("a", string=re.compile("Explore Plan of Study"))
    if plan is None:
        raise ValueError("Catalog plan link missing")
    return {
        "id": "purdue-ai-ba",
        "title": "Artificial Intelligence (Liberal Arts)",
        "award_level": "BA",
        "program_kind": "degree",
        "hosting_unit": "College of Liberal Arts",
        "catalog_year": None,
        "curriculum_status": "pending",
        "courses": [],
        "requirements": [],
        "links": [
            {"kind": "overview", "url": SOURCES[0], "label": "Official BA admissions overview"},
            {
                "kind": "catalog",
                "url": urljoin(SOURCES[0], plan["href"]),
                "label": "Official plan of study (access blocked during pilot)",
            },
        ],
        "notes": [
            "Identity and BA award verified from admissions Quick Facts; course-level requirements await catalog access."
        ],
    }
