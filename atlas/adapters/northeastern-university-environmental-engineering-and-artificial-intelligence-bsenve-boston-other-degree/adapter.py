"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'northeastern-university-environmental-engineering-and-artificial-intelligence-bsenve-boston-other-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/engineering/civil-environmental/environmental-engineering-artificial-intelligence-bsenve/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Environmental Engineering and Artificial Intelligence, BSEnvE (Boston)', award='other', kind='degree', aliases=('Environmental Engineering and Artificial Intelligence, BSEnvE',), award_terms=('BSEnvE',), identity_scopes=('courseleaf-title',))
