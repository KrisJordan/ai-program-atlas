"""Source-specific identity observation; curriculum extraction pending."""
from atlas.adapters.final_discovery_common import parse_claims

PROGRAM_ID = 'georgia-ai-emphasis'
SOURCES = ('https://cs.uga.edu/news/stories/2025/area-emphasis-artificial-intelligence-ai-provides-preparation-similar-emerging-ai',)
IDENTITY = {'program_id': 'georgia-ai-emphasis', 'title': 'Artificial Intelligence', 'award': 'concentration', 'kind': 'concentration', 'heading': 'Area of Emphasis in Artificial Intelligence', 'claims': ['approved Area of Emphasis in Artificial Intelligence', 'recognition in the transcript']}

def parse(html: str) -> dict:
    return parse_claims(html, **IDENTITY)
