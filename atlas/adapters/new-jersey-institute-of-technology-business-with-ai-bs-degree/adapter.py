"""Identity-only observation from the school page with an explicit BS award."""
from atlas.adapters.final_discovery_common import parse_claims

PROGRAM_ID = 'new-jersey-institute-of-technology-business-with-ai-bs-degree'
SOURCES = ('https://management.njit.edu/bachelors-science-business-ai',)


def parse(html: str) -> dict:
    return parse_claims(html, program_id=PROGRAM_ID, title='Business with AI',
                        award='BS', kind='degree', heading='What is Business with AI',
                        claims=['Bachelor of Science in Business with AI'])
