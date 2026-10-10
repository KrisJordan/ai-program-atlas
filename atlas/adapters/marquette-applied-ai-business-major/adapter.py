from atlas.adapters.upper_tail_identity import parse_special

PROGRAM_ID = "marquette-applied-ai-business-major"
SOURCES = [
    "https://www.marquette.edu/academics/majors/applied-artificial-intelligence-in-business.php"
]
TITLE = "Applied Artificial Intelligence in Business"
AWARD = "other"
KIND = "additional_major"


def parse(html: str) -> dict:
    return parse_special(
        html, mode="marquette", program_id=PROGRAM_ID, title=TITLE, award=AWARD, kind=KIND
    )
