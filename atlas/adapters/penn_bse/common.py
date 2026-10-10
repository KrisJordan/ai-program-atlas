"""Small helpers for Penn's distinct official program page layouts."""

import re

from bs4 import BeautifulSoup

from atlas.adapters.cmu_bs.common import course, requirement, text


def penn_course(code, name, source, url, category="ai_ml", credits=None):
    return course(
        code, name, source, url, category, credits, institution="penn", unit="course_units"
    )


def req(pid, key, title, source, **kwargs):
    return requirement(pid, key, title, source, unit="course_units", **kwargs)


def list_courses(container, source, url, category="ai_ml"):
    result = {}
    for li in container.find_all("li"):
        # Own text only, so nested alternatives do not corrupt a course title.
        copy = BeautifulSoup(str(li), "html.parser").li
        for nested in copy.find_all(["ul", "ol"]):
            nested.decompose()
        line = text(copy)
        match = re.match(r"(?:Or\s+)?([A-Z]{2,5})\s+(\d{4})\s*:?[ ]+(.+)", line)
        if not match:
            continue
        code = match.group(1) + " " + match.group(2)
        item = penn_course(code, match.group(3), source, url, category)
        result[item["id"]] = item
    return list(result.values())
