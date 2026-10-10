from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = "wpi-business-analytics-applied-ai-bs"
SOURCES = ["https://www.wpi.edu/academics/study/business-analytics-applied-ai-bs"]
TITLE = "Business Analytics & Applied AI"
AWARD = "BS"
KIND = "degree"


def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title=TITLE, award=AWARD, kind=KIND)
