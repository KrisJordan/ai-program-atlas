"""Actual local-minor observations; refresh never certifies completeness."""

from atlas.adapters.vt_duke_minors import parse_duke_apps, policy_observation

PROGRAM_ID = "duke-university-artificial-intelligence-applications-and-implications-minor-minor"
SOURCE_ID = "duke-apps-department"
SOURCES = (
    "https://cs.duke.edu/undergraduate/degrees/minors",
    "https://cs.duke.edu/undergraduate/degrees/BS/concentrations/ai-ml",
    "https://trinity.duke.edu/undergraduate/academic-policies/change-major-minor-certificate",
)


def parse(html: str) -> dict:
    return parse_duke_apps(html, PROGRAM_ID, SOURCE_ID, SOURCES[0])


def parse_policy_0(html: str) -> dict:
    from atlas.adapters.duke_public_policies import parse_apps_linked_pool

    return parse_apps_linked_pool(html, PROGRAM_ID, "duke-apps-linked-concentration", SOURCES[1])


def parse_policy_1(html: str) -> dict:
    return policy_observation(html, PROGRAM_ID, "duke-trinity-minor-policy", "trinity")


SOURCE_PARSERS = {
    "https://cs.duke.edu/undergraduate/degrees/BS/concentrations/ai-ml": parse_policy_0,
    "https://trinity.duke.edu/undergraduate/academic-policies/change-major-minor-certificate": parse_policy_1,
}


from atlas.adapters.duke_public_policies import (
    GRADES_URL,
    TRANSFER_URL,
    parse_grades,
    parse_transfer,
)

SOURCES += (GRADES_URL, TRANSFER_URL)
SOURCE_PARSERS.update(
    {
        GRADES_URL: lambda html: parse_grades(html, PROGRAM_ID),
        TRANSFER_URL: lambda html: parse_transfer(html, PROGRAM_ID),
    }
)

from atlas.adapters.duke_public_policies import (
    TRINITY_SU_URL,
    TRINITY_TRANSFER_URL,
    parse_trinity_su,
    parse_trinity_transfer,
)

SOURCES += (TRINITY_SU_URL, TRINITY_TRANSFER_URL)
SOURCE_PARSERS.update(
    {
        TRINITY_SU_URL: lambda html: parse_trinity_su(html, PROGRAM_ID),
        TRINITY_TRANSFER_URL: lambda html: parse_trinity_transfer(html, PROGRAM_ID),
    }
)
