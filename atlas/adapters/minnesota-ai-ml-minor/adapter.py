"""Source-specific identity observation; curriculum extraction pending."""
from atlas.adapters.final_discovery_common import parse_claims

PROGRAM_ID = 'minnesota-ai-ml-minor'
SOURCES = ('https://cse.umn.edu/cs/artificial-intelligence-and-machine-learning-ai-ml-minor',)
IDENTITY = {'program_id': 'minnesota-ai-ml-minor', 'title': 'Artificial Intelligence and Machine Learning', 'award': 'minor', 'kind': 'minor', 'heading': 'Artificial Intelligence and Machine Learning', 'claims': ['minor in Artificial Intelligence and Machine Learning', 'undergraduate students']}

def parse(html: str) -> dict:
    return parse_claims(html, **IDENTITY)
