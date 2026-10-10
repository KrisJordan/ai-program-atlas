from atlas.adapters.cmu_bs.common import parse_catalog

SOURCES = [
    "https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/minors/artificial-intelligence-minor/"
]


def parse(html: str) -> dict:
    return parse_catalog(
        html,
        pid="cmu-minor-ai",
        title="Artificial Intelligence, Minor",
        award="minor",
        kind="minor",
        source_url=SOURCES[0],
        sections={
            "Required Core Courses": "minor-core",
            "Technical Electives": "minor-clusters",
            "Societal Aspects of AI": "societal",
        },
    )


PROGRAM_ID = "cmu-minor-ai"
