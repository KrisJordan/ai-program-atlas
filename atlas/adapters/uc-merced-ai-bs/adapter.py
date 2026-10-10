from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = "uc-merced-ai-bs"
SOURCES = ["https://www.ucmerced.edu/majors-and-minors/artificial-intelligence-bs"]
TITLE = "Artificial Intelligence"
AWARD = "BS"
KIND = "degree"


def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title=TITLE, award=AWARD, kind=KIND)
