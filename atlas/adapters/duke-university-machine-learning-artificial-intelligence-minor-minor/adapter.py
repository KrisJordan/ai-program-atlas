"""Actual local-minor observations; refresh never certifies completeness."""

from atlas.adapters.vt_duke_minors import parse_duke_ml, policy_observation

PROGRAM_ID = "duke-university-machine-learning-artificial-intelligence-minor-minor"
SOURCE_ID = "duke-ml-department"
SOURCES = (
    "https://ece.duke.edu/academics/undergrad/minors/",
    "https://undergraduate.bulletins.duke.edu/programs/U-ECE-MLAI/requirements-IkDU1",
    "https://trinity.duke.edu/undergraduate/academic-policies/change-major-minor-certificate",
)


def parse(html: str) -> dict:
    return parse_duke_ml(html, PROGRAM_ID, SOURCE_ID, SOURCES[0])


def parse_policy_0(html: str) -> dict:
    return policy_observation(html, PROGRAM_ID, "duke-ml-bulletin", "bulletin")


def parse_policy_1(html: str) -> dict:
    return policy_observation(html, PROGRAM_ID, "duke-trinity-minor-policy", "trinity")


SOURCE_PARSERS = {
    "https://undergraduate.bulletins.duke.edu/programs/U-ECE-MLAI/requirements-IkDU1": parse_policy_0,
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

from atlas.adapters.duke_public_policies import PRATT_URL, parse_pratt

SOURCES += (PRATT_URL,)
SOURCE_PARSERS[PRATT_URL] = lambda html: parse_pratt(html, PROGRAM_ID)

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
