from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = "wpi-ai-bs"
SOURCES = ["https://www.wpi.edu/academics/study/artificial-intelligence-bs"]
TITLE = "Artificial Intelligence"
AWARD = "BS"
KIND = "degree"


def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title=TITLE, award=AWARD, kind=KIND)
