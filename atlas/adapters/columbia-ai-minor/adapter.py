"""Observe Columbia's named undergraduate AI minor in the current college bulletin."""

from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = "columbia-ai-minor"
SOURCES = (
    "https://bulletin.columbia.edu/columbia-college/departments-instruction/computer-science/",
)


def parse(html: str) -> dict:
    return parse_identity(
        html,
        program_id=PROGRAM_ID,
        title="Artificial Intelligence",
        award="minor",
        kind="minor",
        aliases=("Minor in Artificial Intelligence",),
    )
