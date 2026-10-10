from atlas.adapters.upper_tail_identity import parse_special

PROGRAM_ID = "wpi-ai-advanced-methods-concentration"
SOURCES = ["https://www.wpi.edu/academics/study/artificial-intelligence-bs"]
TITLE = "Artificial Intelligence — Advanced AI Methods and Technologies concentration"
AWARD = "concentration"
KIND = "concentration"


def parse(html: str) -> dict:
    return parse_special(
        html, mode="wpi", program_id=PROGRAM_ID, title=TITLE, award=AWARD, kind=KIND
    )
