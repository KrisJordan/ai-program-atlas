from atlas.adapters.cmu_bs.common import parse_catalog
from atlas.adapters.cmu_additional.requirements import enrich_requirements

SOURCES = [
    "https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/artificialintelligence/artificial-intelligence-additional-major/"
]


def parse(html: str) -> dict:
    observed = parse_catalog(
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
    return enrich_requirements(html, observed, SOURCES[0])


PROGRAM_ID = "cmu-additional-ai"
