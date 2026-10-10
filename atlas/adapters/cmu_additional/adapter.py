from atlas.adapters.cmu_bs.common import parse_catalog

SOURCES = [
    "https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/artificialintelligence/artificial-intelligence-additional-major/"
]


def parse(html: str) -> dict:
    return parse_catalog(
        html,
        pid="cmu-additional-ai",
        title="Artificial Intelligence, Additional Major",
        award="other",
        kind="additional_major",
        source_url=SOURCES[0],
        sections={
            "Computer Science Core": "cs",
            "Artificial Intelligence Core": "ai",
            "AI Cluster Electives": "clusters",
            "Ethics and Human Cognition": "ethics",
        },
    )


PROGRAM_ID = "cmu-additional-ai"
