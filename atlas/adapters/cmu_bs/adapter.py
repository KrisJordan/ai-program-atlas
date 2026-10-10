from .common import parse_catalog

SOURCES = [
    "https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/artificialintelligence/artificial-intelligence-bs/"
]


def parse(html: str) -> dict:
    return parse_catalog(
        html,
        pid="cmu-bs-ai",
        title="Artificial Intelligence, B.S.",
        award="BS",
        kind="degree",
        source_url=SOURCES[0],
        sections={
            "Computer Science": "cs",
            "Artificial Intelligence": "ai",
            "Ethics Course": "ethics",
        },
    )


PROGRAM_ID = "cmu-bs-ai"
