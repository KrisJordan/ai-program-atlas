"""Observed Villanova local curriculum; completeness is reviewer-only."""

from atlas.adapters.villanova_curriculum import parse_program

PROGRAM_ID = "villanova-analytics-ai-co-major"
SOURCES = [
    "https://live-villanova-catalog.cleancatalog.io/analytics-artificial-intelligence/analytics-artificial-intelligence-comajor",
    "https://www.villanova.edu/university/business/academics/undergraduate-programs/degrees.html",
    "https://live-villanova-catalog.cleancatalog.io/",
]


def parse(html: str) -> dict:
    verify_other_electives(html)
    return parse_program(
        html,
        pid=PROGRAM_ID,
        title="Analytics & Artificial Intelligence",
        award="other",
        kind="additional_major",
        url=SOURCES[0],
    )


from atlas.adapters.villanova_curriculum import parse_course

SOURCE_PARSERS = {SOURCES[0]: parse}
SOURCES.append("https://live-villanova-catalog.cleancatalog.io/management/mgt-3170")
SOURCE_PARSERS["https://live-villanova-catalog.cleancatalog.io/management/mgt-3170"] = lambda html: (
    parse_course(
        html,
        pid=PROGRAM_ID,
        code="MGT 3170",
        url="https://live-villanova-catalog.cleancatalog.io/management/mgt-3170",
    )
)
SOURCES.append("https://live-villanova-catalog.cleancatalog.io/management/mgt-4170")
SOURCE_PARSERS["https://live-villanova-catalog.cleancatalog.io/management/mgt-4170"] = lambda html: (
    parse_course(
        html,
        pid=PROGRAM_ID,
        code="MGT 4170",
        url="https://live-villanova-catalog.cleancatalog.io/management/mgt-4170",
    )
)


def verify_other_electives(html):
    """Do not silently keep the empty-list interpretation after new content appears."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    headings = [
        h
        for h in soup.find_all("h5", class_="modal-title")
        if " ".join(h.get_text(" ", strip=True).split()) == "Other Approved Electives"
    ]
    if len(headings) != 1:
        raise ValueError("Other Approved Electives modal missing or duplicated")
    modal = headings[0].find_parent(class_="modal")
    body = modal.find(class_="modal-body") if modal else None
    if body is None:
        raise ValueError("Other Approved Electives body missing")
    value = " ".join(body.get_text(" ", strip=True).split())
    if value != "Total Credits" or body.find(["a", "article", "iframe", "object", "embed"]):
        raise ValueError("Other Approved Electives now contains content; review its inventory")
