from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = "drexel-ai-ml-bs"
SOURCES = [
    "https://catalog.drexel.edu/undergraduate/computer-information-sciences/artificialintellicenceandmachinelearningbs/"
]
TITLE = "Artificial Intelligence & Machine Learning"
AWARD = "BS"
KIND = "degree"


def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title=TITLE, award=AWARD, kind=KIND)
