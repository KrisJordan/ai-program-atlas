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


# A separate metadata candidate never certifies program requirements.
from atlas.adapters.cmu_bs.course_metadata import COURSE_SOURCE, parse_metadata

METADATA_CODES = (
    "15-122",
    "15-150",
    "15-210",
    "15-213",
    "15-251",
    "07-280",
    "07-380",
    "15-386",
    "15-482",
    "15-494",
    "16-350",
    "16-362",
    "16-384",
    "10-403",
    "10-405",
    "10-414",
    "10-417",
    "10-418",
    "10-422",
    "10-423",
    "10-424",
    "10-425",
    "11-441",
    "11-485",
    "36-402",
    "11-411",
    "11-442",
    "11-492",
    "15-387",
    "15-463",
    "16-385",
    "05-317",
    "05-318",
    "05-391",
    "16-467",
    "16-161",
    "16-735",
    "17-200",
    "80-249",
    "85-110",
    "85-213",
    "85-413",
    "85-408",
    "85-421",
    "15-112",
    "21-112",
    "21-120",
    "21-127",
    "21-128",
    "15-151",
    "21-122",
    "21-241",
    "36-218",
    "15-259",
    "21-325",
    "36-226",
    "21-425",
    "36-225",
    "36-235",
    "36-236",
    "36-401",
)
SOURCES.append(COURSE_SOURCE)
SOURCE_PARSERS = {
    COURSE_SOURCE: lambda html: parse_metadata(html, pid=PROGRAM_ID, codes=METADATA_CODES)
}
