"""Small official course-page observations, not a static description replay."""

import re
from fractions import Fraction
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, text

COURSES = {
    "CS 2119": "https://wpi.cleancatalog.net/computer-science/cs-2119",
    "CS 4341": "https://wpi.cleancatalog.net/computer-science/cs-4341",
    "CS 4342": "https://wpi.cleancatalog.net/computer-science/cs-4342",
    "MIS 3730": "https://wpi.cleancatalog.net/management-information-systems/mis-3730",
    "MIS 3787": "https://wpi.cleancatalog.net/management-information-systems/mis-3787",
}


def parse_course(html, pid, code, title, award, kind):
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    heading = main.find("h1") if main else None
    if not heading or not text(heading).startswith(code + ":"):
        raise ValueError("Course code heading changed")
    name = text(heading).split(":", 1)[1].strip()
    source = pid + "-course-" + code.lower().replace(" ", "-")
    credits = main.find(class_="field--name-field-credits")
    amount = credits.find(class_="field__item") if credits else None
    try:
        value = float(Fraction(text(amount))) if amount else None
    except (ValueError, ZeroDivisionError):
        value = None
    c = course(code, name, source, COURSES[code], credits=value, institution="wpi")
    recommended = main.find(class_="field--name-field-recommended")
    bits = []
    if recommended:
        content = recommended.find(class_="field__item")
        if content:
            bits.append("Recommended background (not a mandatory prerequisite): " + text(content))
    desc = main.find(class_="field--name-field-description")
    if desc:
        bits += re.findall(r"Undergraduate credit may not be earned both[^.]*\.", text(desc))
    c["prerequisites"] = " ".join(bits) or None
    year = re.search(r"Undergraduate Catalog (20\d{2}-20\d{2})", text(soup))
    return dict(
        id=pid,
        title=title,
        award_level=award,
        program_kind=kind,
        catalog_year=year[1] if year else None,
        curriculum_status="partial",
        courses=[c],
        requirements=[],
        notes=[
            "Course metadata only. Recommended background is explicitly advisory; no curriculum verification is implied. Descriptions require separate concise editorial review."
        ],
    )


def attach(namespace, codes):
    parsers = namespace.setdefault("SOURCE_PARSERS", {namespace["SOURCES"][0]: namespace["parse"]})
    for code in codes:
        url = COURSES[code]
        if url not in namespace["SOURCES"]:
            namespace["SOURCES"].append(url)
        parsers[url] = lambda html, code=code: parse_course(
            html,
            namespace["PROGRAM_ID"],
            code,
            namespace["TITLE"],
            "concentration" if namespace["PROGRAM_ID"].endswith("concentration") else "BS",
            "concentration" if namespace["PROGRAM_ID"].endswith("concentration") else "degree",
        )
