"""Observe canonical directory and advising guidance without inventing a Department List."""

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import requirement

PID = "penn-state-ai-engineering-minor"
DIRECTORY = "https://www.eecs.psu.edu/students/undergraduate/Majors-Minors-Certificates.aspx"
FAQ = "https://www.eecs.psu.edu/students/undergraduate/advising/faqs.aspx"


def text(n):
    return " ".join(n.get_text(" ", strip=True).split())


def parse_directory(html):
    soup = BeautifulSoup(html, "html.parser")
    heading = next(
        (h for h in soup.find_all("h4") if text(h) == "Artificial Intelligence Engineering Minor"),
        None,
    )
    if heading is None:
        raise ValueError("Canonical EECS minor directory section missing")
    p = heading.find_next("p")
    link = p.find("a", href=True) if p else None
    if link is None or not link["href"].rstrip("/").endswith(
        "/artificial-intelligence-engineering-minor"
    ):
        raise ValueError("AI minor directory destination changed; inspect new source")
    return dict(
        id=PID,
        curriculum_status="partial",
        courses=[],
        requirements=[
            requirement(
                PID,
                "directory-route",
                "Public directory returns to the bulletin",
                "penn-state-eecs-minors",
                kind="note",
                summary="The canonical EECS directory identifies the jointly offered AI Engineering minor and links its Learn more entry to the minor bulletin. This is identity/provenance context, not an approved Department List.",
            )
        ],
    )


def parse_faq(html):
    soup = BeautifulSoup(html, "html.parser")

    def answer(key):
        h = soup.find("p", id=key)
        if h is None:
            raise ValueError("Advising FAQ section missing: " + key)
        nodes = []
        for n in h.find_next_siblings():
            if n.name == "p" and n.get("id"):
                break
            if n.name:
                nodes.append(n)
        return " ".join(text(n) for n in nodes), nodes

    department, nodes = answer("department")
    if "handbook for each major" not in department:
        raise ValueError("Department-list guidance changed")
    links = [a for n in nodes for a in n.find_all("a", href=True) if text(a) == "AIE"]
    if (
        len(links) != 1
        or urljoin(FAQ, links[0]["href"])
        != "https://www.eecs.psu.edu/students/undergraduate/artificial-intelligence-engineering-bs.aspx"
    ):
        raise ValueError("AIE handbook/list destination changed; inspect new source")
    prerequisites, _ = answer("prerequisites")
    override, _ = answer("override")
    if (
        "strictly enforced" not in prerequisites
        or "course substitution" not in prerequisites
        or "LionPATH" not in override
        or "assigned advisor" not in override
    ):
        raise ValueError("Prerequisite override policy changed")
    rules = [
        requirement(
            PID,
            "faq-list-route",
            "Department-list guidance does not establish minor options",
            "penn-state-eecs-advising-faq",
            kind="note",
            summary="The FAQ refers readers to each major handbook for departmental lists. Its AIE link leads to the AI Engineering BS overview, which does not enumerate the minor Department List or explicitly authorize a BS pool for the minor. No major-to-minor equivalence is inferred.",
        ),
        requirement(
            PID,
            "faq-prerequisites",
            "Prerequisite enforcement and substitution review",
            "penn-state-eecs-advising-faq",
            kind="note",
            summary="EECS course prerequisites are strictly enforced. Students expecting a course substitution to satisfy a prerequisite must request an override through the enrollment section of LionPATH and are advised to consult their assigned adviser. The minor CMPSC 445 alternative does not itself waive the separately published A-I 410 prerequisites. No private system or form was accessed.",
        ),
    ]
    return dict(id=PID, curriculum_status="partial", courses=[], requirements=rules)
