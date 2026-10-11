"""Exact dated OCW architecture observations; no current-offering equivalence."""
import hashlib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import course

MANIFEST=json.loads(Path(__file__).with_name('reviewed_architecture_ocw.json').read_text())


def clean(node):
    return ' '.join(node.get_text(' ',strip=True).split()) if node else ''


def observe(html):
    soup=BeautifulSoup(html,'html.parser')
    banner=soup.select_one('#course-banner');main=soup.select_one('#course-main-content')
    if banner is None or main is None:
        raise ValueError('OCW architecture banner or syllabus missing')
    parts=clean(banner.select_one('.course-number-term-detail')).split(' | ')
    if len(parts)!=3 or not re.fullmatch(r'(Fall|Spring) \d{4}',parts[1]):
        raise ValueError('OCW architecture dated identity missing')
    title=clean(banner.find('h1'))
    headings=[clean(h) for h in main.find_all(['h2','h3','h4'])]
    if not any(h in headings for h in ['Course Description','General Information','Course Overview']):
        raise ValueError('OCW architecture substantive description missing')
    prerequisites=None
    for h in main.find_all(['h2','h3','h4']):
        if clean(h) not in ['Prerequisites','Prerequisite']:continue
        fragments=[]
        for sibling in h.next_siblings:
            if getattr(sibling,'name',None) in ['h2','h3','h4']:break
            if hasattr(sibling,'get_text'):fragments.append(clean(sibling))
        prerequisites=' '.join(fragments).strip() or None
    return dict(code=parts[0],name=title,term=parts[1],level=parts[2],prerequisites=prerequisites,
                content_digest=hashlib.sha256(clean(main).encode()).hexdigest())


def parse(html,url):
    observed=observe(html);saved=MANIFEST['sources'][url];rows=[]
    if observed!=saved['observation']:
        return dict(id='mit-ai-decision-making-bs',courses=[],requirements=[],notes=['Dated architecture syllabus changed; manual metadata review withheld.'])
    for cid,identity in saved['courses'].items():
        c=course('mit-ai-hass',identity['code'],identity['name'],saved['source_id'],url,unit='units');c['id']=cid
        c.update(description=saved['summary'],category='human_context',prerequisites=observed['prerequisites'],public_site=url,syllabus=url)
        c['notes']=saved['notes']
        rows.append(c)
    return dict(id='mit-ai-decision-making-bs',courses=rows,requirements=[],observed_architecture_syllabus=observed)


SOURCE_PARSERS={url:(lambda html,url=url:parse(html,url)) for url in MANIFEST['sources']}
