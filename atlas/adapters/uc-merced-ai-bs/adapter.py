from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = "uc-merced-ai-bs"
SOURCES = ["https://www.ucmerced.edu/majors-and-minors/artificial-intelligence-bs"]
TITLE = "Artificial Intelligence"
AWARD = "BS"
KIND = "degree"


def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title=TITLE, award=AWARD, kind=KIND)

from atlas.adapters.merced_public_context import AI_URL, parse_ai
SOURCE_PARSERS={AI_URL:parse_ai}
