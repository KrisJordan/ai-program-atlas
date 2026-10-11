"""A verified public topic is context, not every offering of its parent code."""
import hashlib,json
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import rule
URL='https://computing.mit.edu/cross-cutting/common-ground-for-computing-education/c22-audio-computing/'
SID='mit-ai-c22-topic-context'
TITLE='C22 Audio Computing: Processing Sound in Engineering, Science, and the Arts'
REVIEW=json.loads(Path(__file__).with_name('reviewed_audio_topic.json').read_text())


def observe(html):
    soup=BeautifulSoup(html,'html.parser');h=soup.find('h1')
    if h is None or h.get_text(' ',strip=True)!=TITLE:raise ValueError('C22 title missing')
    lists=[ul for ul in soup.find_all('ul')if 'Offered under:'in ul.get_text(' ',strip=True)]
    if len(lists)!=1:raise ValueError('C22 facts list missing/ambiguous')
    block=lists[0].parent;fields={}
    for li in lists[0].find_all('li',recursive=False):
        label=li.find('strong')
        if label:
            key=label.get_text(' ',strip=True);fields[key]=li.get_text(' ',strip=True).removeprefix(key).strip()
    if fields.get('Offered under:')!='21M.389, 21M.589':raise ValueError('C22 offering codes changed')
    required=['Term(s):','Level:','Units:','Prerequisite:']
    if any(not fields.get(k)for k in required):raise ValueError('C22 scope fields missing')
    paragraphs=block.find_all('p',recursive=False)
    if not paragraphs:raise ValueError('C22 description missing')
    description=' '.join(' '.join(p.get_text(' ',strip=True).split())for p in paragraphs)
    payload=dict(fields=fields,description=description)
    return payload,hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()


def parse(html):
    observed,digest=observe(html)
    if digest!=REVIEW['digest']:return dict(id='mit-ai-decision-making-bs',courses=[],requirements=[])
    return dict(id='mit-ai-decision-making-bs',courses=[],requirements=[rule(
        'mit-ai-c22-topic-context','Public C22 topic context for21M.589',SID,
        ['mit-ai-v2025-21m-589'],kind='note',summary=REVIEW['summary'])])


SOURCE_PARSERS={URL:parse}
