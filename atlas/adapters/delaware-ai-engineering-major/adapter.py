from atlas.adapters.upper_tail_identity import parse_special

PROGRAM_ID = "delaware-ai-engineering-major"
SOURCES = ["https://www.udel.edu/apply/undergraduate-admissions/major-finder/"]
TITLE = "Artificial Intelligence Engineering"
AWARD = "other"
KIND = "degree"


def parse(html: str) -> dict:
    return parse_special(
        html, mode="delaware", program_id=PROGRAM_ID, title=TITLE, award=AWARD, kind=KIND
    )
