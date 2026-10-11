"""Source-specific major-table observations; degree-wide inventory remains partial."""

from atlas.adapters.case_ai_degrees import parse_case

PROGRAM_ID = "case-western-reserve-university-artificial-intelligence-ba-degree"
SOURCES = (
    "https://bulletin.case.edu/engineering/computer-data-sciences/artificial-intelligence-ba/",
)


def parse(html):
    return parse_case(html, PROGRAM_ID, "BA", SOURCES[0])


from atlas.adapters import case_degree_policies as policies

SOURCES += (policies.DEGREE_URL, policies.UGER_URL)


def parse_degree_policy(html):
    return policies.parse_degree(html, PROGRAM_ID, "BA")


def parse_uger_policy(html):
    return policies.parse_uger(html, PROGRAM_ID, "BA")


SOURCE_PARSERS = {policies.DEGREE_URL: parse_degree_policy, policies.UGER_URL: parse_uger_policy}
