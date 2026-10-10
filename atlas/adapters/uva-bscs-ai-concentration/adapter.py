"""Source-scoped identity observation; curriculum review remains pending."""
from atlas.adapters.discovery_common import parse_identity
from bs4 import BeautifulSoup

PROGRAM_ID = 'uva-bscs-ai-concentration'
SOURCES = ['https://uvacsadvising.org/ai-concentration.html', 'https://engineering.virginia.edu/department/computer-science/academics/undergraduate-programs/bs-computer-science']


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.find_all(["nav", "aside", "footer"]):
        node.decompose()
    root = soup.find("main") or soup
    if 'BSCS AI Concentration' not in [h.get_text(" ", strip=True) for h in root.find_all("h2")]:
        raise ValueError("Expected parent-degree concentration section missing")
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence', award='concentration', kind='concentration')
