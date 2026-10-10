"""Observe the formal AI track in the Stanford undergraduate CS program."""

from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = "stanford-ai-track"
SOURCES = ("https://www.cs.stanford.edu/academics-overview/academics-bachelors-program",)


def parse(html: str) -> dict:
    return parse_identity(
        html,
        program_id=PROGRAM_ID,
        title="Artificial Intelligence (CS BS track)",
        award="concentration",
        kind="concentration",
        aliases=("Artificial Intelligence",),
    )
