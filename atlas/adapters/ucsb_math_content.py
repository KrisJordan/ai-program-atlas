"""Independent department mathematics descriptions; existing degree units unchanged."""
import hashlib
import json
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import text

URL='https://www.math.ucsb.edu/undergraduate/undergraduate-course-descriptions'
SOURCE_ID='ucsb-ai-bs-math-department-descriptions'
SPEC=json.loads(Path(__file__).with_suffix('.json').read_text())


def block(soup, code):
    heading=next((h for h in soup.find_all('h2')if text(h)=='Math '+code.split()[1]),None)
    if not heading:raise ValueError('UCSB mathematics heading missing')
    parts=[]
    for sibling in heading.find_next_siblings():
        if sibling.name=='h2':break
        # Description/prerequisite paragraphs only, excluding resource links.
        if sibling.name=='p' and not sibling.find('a'):parts.append(text(sibling))
    return ' '.join(parts)


def parse(html):
    soup=BeautifulSoup(html,'html.parser');courses=[]
    for code,e in SPEC.items():
        if hashlib.sha256(block(soup,code).encode()).hexdigest()!=e['block_digest']:
            raise ValueError('UCSB mathematics description or prerequisite changed')
        courses.append(dict(id=e['course_id'],code=code,description=e['description'],
                            prerequisites=e['prerequisites'],category='mathematics',
                            source_id=SOURCE_ID,url=URL))
    return {'id':'ucsb-ai-bs','courses':courses,'requirements':[],
            'notes':['Undated departmental general descriptions; no units stated here. Existing degree-source credits retained.']}
