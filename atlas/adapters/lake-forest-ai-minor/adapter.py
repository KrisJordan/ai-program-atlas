"""Observe the public AI minor overview and its current track headings."""
from bs4 import BeautifulSoup

PROGRAM_ID = 'lake-forest-ai-minor'
SOURCES = ('https://www.lakeforest.edu/academics/majors-and-minors/artificial-intelligence',)
SOURCE_ID = 'lake-forest-ai-overview'


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    h1 = soup.find('h1', string=lambda s: s and s.strip() == 'Artificial Intelligence')
    if not h1:
        raise ValueError('AI program heading missing')
    text = ' '.join(soup.get_text(' ', strip=True).split())
    if 'interdisciplinary minor' not in text:
        raise ValueError('Explicit minor identity missing')
    headings = [h.get_text(' ', strip=True) for h in soup.find_all('h3')]
    tracks = [h for h in headings if h.startswith('AI ') and h in ('AI Studies', 'AI Governance')]
    if len(set(tracks)) != 2:
        raise ValueError('Track structure changed; review required')
    return dict(id=PROGRAM_ID, title=h1.get_text(strip=True), award_level='minor',
                program_kind='minor', curriculum_status='partial', courses=[],
                requirements=[dict(id=PROGRAM_ID+'-tracks', parent_id=None,
                    title='Track choice', kind='note', count=None, credits=None,
                    credit_unit='unknown', category='other', source_id=SOURCE_ID,
                    source_text=None, summary='Observed track headings: '+', '.join(dict.fromkeys(tracks))+'. Full requirements require catalog review.', course_ids=[])])
