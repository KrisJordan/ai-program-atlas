from atlas.adapters.upper_tail_identity import parse_special

PROGRAM_ID = "indiana-cs-ai-specialization"
SOURCES = ["https://luddy.iu.edu/academics/undergraduate/bs-computer-science.html"]
TITLE = "Computer Science — Artificial Intelligence specialization"
AWARD = "concentration"
KIND = "concentration"


def parse(html: str) -> dict:
    return parse_special(
        html, mode="indiana", program_id=PROGRAM_ID, title=TITLE, award=AWARD, kind=KIND
    )
