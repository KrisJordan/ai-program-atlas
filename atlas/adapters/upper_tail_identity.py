"""Source-specific identity checks for upper-tail discovery records."""

from bs4 import BeautifulSoup

from atlas.adapters.discovery_common import normalized, parse_identity


def parse_special(html, *, mode, program_id, title, award, kind):
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.find_all(["nav", "header", "footer", "aside", "script", "style"]):
        node.decompose()
    if mode == "delaware":
        if not any(
            "explore 150 majors" in normalized(h.get_text(" ", strip=True))
            for h in soup.find_all("h1")
        ):
            raise ValueError("Delaware undergraduate major directory heading missing")
        return parse_identity(
            html, program_id=program_id, title=title, award=award, kind=kind, award_terms=(title,)
        )
    if mode == "marquette":
        result = parse_identity(
            html, program_id=program_id, title=title, award=award, kind=kind, award_terms=("Major",)
        )
        if not any(
            "additional primary major" in normalized(p.get_text(" ", strip=True))
            for p in soup.find_all("p")
        ):
            raise ValueError("Marquette additional-primary-major restriction missing")
        return result
    parent = {
        "indiana": "Computer Science",
        "merced": "Computer Science and Engineering",
        "wpi": "Artificial Intelligence",
    }[mode]
    parse_identity(html, program_id=program_id, title=parent, award="BS", kind="degree")
    found = False
    if mode == "merced":
        for link in soup.find_all("a"):
            if normalized(parent) not in normalized(link.get_text(" ", strip=True)):
                continue
            row = link.find_parent("li")
            if row and any(
                normalized(li.get_text(" ", strip=True)) == "artificial intelligence emphasis"
                for li in row.find_all("li")
            ):
                found = True
    elif mode == "indiana":
        for heading in soup.find_all(["h2", "h3", "h4"]):
            if normalized(heading.get_text(" ", strip=True)) != "choose a cs specialization":
                continue
            for node in heading.find_next_siblings():
                if node.name in ("h1", "h2", "h3", "h4"):
                    break
                if node.name == "ul" and any(
                    normalized(li.get_text(" ", strip=True)).startswith("artificial intelligence ")
                    for li in node.find_all("li")
                ):
                    found = True
    else:
        for node in soup.find_all(["p", "h2", "h3", "h4"]):
            if (
                normalized(node.get_text(" ", strip=True))
                != "choose one of the following concentrations"
            ):
                continue
            listing = node.find_next_sibling("ul")
            if listing and any(
                normalized(li.get_text(" ", strip=True)) == "advanced ai methods and technologies"
                for li in listing.find_all("li")
            ):
                found = True
    if not found:
        raise ValueError("Expected specialization missing from parent program section")
    return {"id": program_id, "title": title, "award_level": award, "program_kind": kind}
