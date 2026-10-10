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
    "11-411",
    "16-385",
    "15-386",
    "15-482",
    "15-494",
    "16-280",
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
    "11-442",
    "11-492",
    "15-387",
    "15-463",
    "05-317",
    "05-318",
    "05-391",
    "16-467",
    "16-161",
    "16-735",
    "17-200",
    "80-249",
)
SOURCES.append(COURSE_SOURCE)
SOURCE_PARSERS = {
    COURSE_SOURCE: lambda html: parse_metadata(html, pid=PROGRAM_ID, codes=METADATA_CODES)
}
