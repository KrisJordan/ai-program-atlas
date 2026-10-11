"""UVA local concentration observation with a distinct parent-degree boundary."""

from atlas.adapters.uva_ai_curriculum import parse_concentration

PROGRAM_ID = "uva-bacs-ai-concentration"
SOURCES = [
    "https://uvacsadvising.org/ai-concentration.html",
    "https://engineering.virginia.edu/department/computer-science/academics/undergraduate-programs/bs-computer-science",
]


def parse(html: str) -> dict:
    return parse_concentration(html, pid=PROGRAM_ID, url=SOURCES[0], parent_degree="BACS")


SOURCES.append(
    "https://engineering.virginia.edu/department/computer-science/cs-undergraduate-artificial-intelligence-concentrations"
)

from atlas.adapters.uva_ai_policies import parsers
SOURCE_PARSERS={SOURCES[0]:parse,**parsers(PROGRAM_ID)}
SOURCES=list(dict.fromkeys([*SOURCES,*SOURCE_PARSERS]))
