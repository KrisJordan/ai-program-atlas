from atlas.adapters.upper_tail_identity import parse_special

PROGRAM_ID = "uc-merced-cse-ai-emphasis"
SOURCES = ["https://admissions.ucmerced.edu/academics/majors-minors"]
TITLE = "Computer Science and Engineering — Artificial Intelligence Emphasis"
AWARD = "concentration"
KIND = "concentration"


def parse(html: str) -> dict:
    return parse_special(
        html, mode="merced", program_id=PROGRAM_ID, title=TITLE, award=AWARD, kind=KIND
    )
