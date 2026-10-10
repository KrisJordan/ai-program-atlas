"""WPI Clean Catalog course rows, preserving fractional undergraduate units."""

from fractions import Fraction
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, text


def document(html, heading):
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    if not main or not main.find("h1") or text(main.find("h1")) != heading:
        raise ValueError("WPI program heading changed")
    detail = main.find("div", class_="degree-class-details")
    if not detail:
        raise ValueError("WPI degree details missing")
    return soup, detail


def rows(node, source, base="https://wpi.cleancatalog.net", unit="units"):
    output = {}
    for item in node.find_all("article", class_="node--type-class"):
        code = item.find("div", class_="col-3")
        name = item.find("div", class_="col-7")
        credit = item.find("span", class_="field--name-field-credits")
        if not code or not name or not code.find("a"):
            raise ValueError("WPI course row malformed")
        amount = None
        if credit:
            try:
                amount = float(Fraction(text(credit)))
            except (ValueError, ZeroDivisionError):
                pass
        c = course(
            text(code),
            text(name),
            source,
            urljoin(base, code.find("a")["href"]),
            institution="wpi",
            credits=amount,
            unit=unit,
        )
        output[c["id"]] = c
    return output


def sections(detail):
    return detail.find_all("div", class_="paragraph--type--degree-section")


def description(section):
    d = section.find("div", class_="field--name-field-degree-section-description")
    return text(d) if d else ""
