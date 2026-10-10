"""Observe an AI major listing in Furman's public directory; no curriculum claim."""
from bs4 import BeautifulSoup

SOURCES = ("https://www.furman.edu/academics/majors-minors-programs/",)
PROGRAM_ID = "furman-ai-bs"


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    for anchor in soup.find_all("a", href=True):
        if "/artificial-intelligence-major/" not in anchor["href"]:
            continue
        node = anchor
        for _ in range(4):
            if node is None:
                break
            text = " ".join(node.get_text(" ", strip=True).split())
            if len(text) < 1000 and all(s in text for s in (
                "Artificial Intelligence Major", "Bachelor of Science", "Undergraduate Majors"
            )):
                return dict(id="furman-ai-bs", title="Artificial Intelligence",
                    award_level="BS", program_kind="degree", status="unknown",
                    curriculum_status="pending", courses=[], requirements=[],
                    notes=["Title and award observed in public directory; detail page is password protected. Availability and curriculum require further verification."])
            node = node.parent
    raise ValueError("Furman undergraduate AI BS directory card missing or changed")
