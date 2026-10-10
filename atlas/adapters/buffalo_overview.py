"""Observed Buffalo overview facts; never substitutes for catalog course requirements."""

import re

from bs4 import BeautifulSoup

FAMILY_URL = "https://engineering.buffalo.edu/ai-society/academics.html"


def text(node):
    return " ".join(node.get_text(" ", strip=True).split())


def requirement(pid, suffix, title, summary, source_id, count=None):
    return {
        "id": pid + "-" + suffix,
        "parent_id": None,
        "title": title,
        "kind": "note",
        "count": count,
        "credits": None,
        "credit_unit": "unknown",
        "category": "other",
        "source_id": source_id,
        "source_text": None,
        "summary": summary,
        "course_ids": [],
    }


def section(soup, heading):
    h = soup.find(lambda n: n.name in ["h1", "h2", "h3"] and text(n) == heading)
    if h is None:
        raise ValueError("Expected Buffalo section: " + heading)
    result = []
    for node in h.find_all_next():
        if node.name in ["h1", "h2", "h3"]:
            break
        if node.name in ["p", "li"]:
            result.append(text(node))
    return result


def parse_degree(html, pid, title, url):
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find(lambda n: n.name in ["h1", "h2"] and text(n) == title):
        raise ValueError("Expected named Buffalo program heading")
    learning = section(soup, "What will I learn?")
    careers = section(soup, "What can I do with an " + title + " degree?")
    if not learning or not careers:
        raise ValueError("Missing program learning or career content")
    # Extract explicitly listed opportunities, which can include roles, settings or activities.
    heading = soup.find(
        lambda n: (
            n.name in ["h2", "h3"] and text(n) == "What can I do with an " + title + " degree?"
        )
    )
    roles = []
    for node in heading.find_all_next():
        if node.name in ["h1", "h2", "h3"]:
            break
        if node.name == "li":
            roles.append(text(node).rstrip("."))
    result = {
        "id": pid,
        "title": title,
        "outcomes": [
            {
                "text": r,
                "kind": "source_stated",
                "source_id": pid + "-program",
                "locator": "What can I do with an " + title + " degree?",
            }
            for r in roles
        ],
    }
    if any("capstone" in t.lower() for t in learning):
        result["requirements"] = [
            requirement(
                pid,
                "overview-capstone",
                "Applied capstone",
                "The program overview identifies a capstone applying program learning to a practical problem; course code and credits are not stated.",
                pid + "-program",
            )
        ]
        result["curriculum_status"] = "partial"
    learning_text = " ".join(learning)
    if title == "AI and Language and Intercultural Competence":
        match = re.search(r"choose from (.+?)—as you take advanced", learning_text)
        if not match:
            raise ValueError("Language specialization options changed or missing")
        result.setdefault("requirements", []).append(
            requirement(
                pid,
                "language-choice",
                "Language specialization",
                "Choose a language specialization from: "
                + match[1]
                + ". Exact language sequences remain unverified.",
                pid + "-program",
            )
        )
    if title == "AI and Logic and Ontology":
        if "internship" not in learning_text:
            raise ValueError("Internship component changed or missing")
        result.setdefault("requirements", []).append(
            requirement(
                pid,
                "internship",
                "Internship component",
                "The overview identifies an internship in addition to the capstone. Course code, credits and detailed approval rules remain unverified.",
                pid + "-program",
            )
        )
    return result


def parse_family(html, pid, title):
    soup = BeautifulSoup(html, "html.parser")
    body = text(soup)
    if "All AI+X degrees consist of the following components" not in body or title not in body:
        raise ValueError("AI+X scope statement or named member missing")
    items = [text(n) for n in soup.find_all("li")]
    labels = [
        "Mathematical prerequisites",
        "Society Core",
        "Technology Component",
        "Integrative Courses",
        "Capstone Experience",
    ]
    found = []
    for label in labels:
        matches = [v for v in items if label in v]
        if len(matches) != 1:
            raise ValueError("Missing or ambiguous AI+X component: " + label)
        found.append(matches[0])
    if "five three-credit courses" not in found[1] or "four-credit courses" not in found[2]:
        raise ValueError("AI+X credit/component rule changed; review required")
    summaries = [
        "Mathematical preparation depends on the individual AI+X degree.",
        "Choose five three-credit society courses. Approved options and degree-specific selection rules remain unverified.",
        "The technology component draws from four-credit mathematics, probability/statistics, computing and data-science courses, combined for the particular degree.",
        "Integrative coursework applies AI or relevant computational and mathematical methods within the partner discipline.",
        "The experiential capstone brings students from AI+X and general AI degrees together on AI-and-society problems.",
    ]
    return {
        "id": pid,
        "curriculum_status": "partial",
        "requirements": [
            requirement(pid, "family-" + str(i), label, summary, pid + "-family")
            for i, (label, summary) in enumerate(zip(labels, summaries), 1)
        ],
    }


def parse_minor(html, pid, title):
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find(lambda n: n.name == "h1" and text(n) == "Minor in " + title):
        raise ValueError("Expected named Buffalo minor heading")
    body = text(soup)
    result = {"id": pid, "title": title}
    if title == "AI Ethics":
        m = re.search(r"requires approximately (\d+) credits", body)
        if not m:
            raise ValueError("Approximate minor credit statement missing")
        result["requirements"] = [
            requirement(
                pid,
                "approximate-credits",
                "Approximate minor size",
                f"The department overview describes approximately {m[1]} credits. This is not an exact catalog total or a verified requirement inventory.",
                pid + "-program",
            )
        ]
        result["curriculum_status"] = "partial"
    else:
        if "CAS Major/Minor Change Request" not in body:
            raise ValueError("Minor declaration route missing")
        result["requirements"] = [
            requirement(
                pid,
                "declaration",
                "Current-student declaration route",
                "Current UB students add this minor using the CAS Major/Minor Change Request. Eligibility, course inventory and overlap policies remain unverified.",
                pid + "-program",
            )
        ]
        result["curriculum_status"] = "partial"
    return result
