"""Observe the public Fall2022 renumbering page's rendered data, not hidden API."""
import json
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import rule

URL='https://eecsis.mit.edu/numbering.html'
SID='mit-ai-numbering-context'
CODES=['6.9030','6.4100','6.5370','6.5380','6.5390','6.5480','6.5490',
       '6.5890','6.7201','6.5690','6.6440','6.7200']


def observe(html):
    soup=BeautifulSoup(html,'html.parser')
    text=' '.join(soup.get_text(' ',strip=True).split())
    if 'Subject Numbering'not in text or 'Starting fall 2022'not in text:
        raise ValueError('Published renumbering scope missing')
    # Literal public data passed to the page's own rendering function; never
    # execute script or request an unpublished endpoint.
    match=re.search(r'generatePage\((\[.*?\])\);',html,re.S)
    if not match:raise ValueError('Published numbering data missing')
    rows=json.loads(match[1]);found={}
    for row in rows:
        if row.get('newnum')not in CODES:continue
        if not all(isinstance(row.get(k),str)and row[k]for k in ['oldnum','newnum','title']):
            raise ValueError('Numbering identity row incomplete')
        if 'removed'in row and not isinstance(row['removed'],bool):
            raise ValueError('Numbering removal flag invalid')
        if row['newnum']in found:raise ValueError('Duplicate numbering identity')
        found[row['newnum']]=row
    if set(found)!=set(CODES):raise ValueError('Reviewed numbering inventory changed')
    return found


def statement(code,row):
    base=f"The table introduced for Fall2022 identifies {code} as {row['title']} (formerly {row['oldnum']}; level {row.get('level')or'not stated'})."
    if row.get('reason'):
        base+=' Its visible row states: '+row['reason']+'.'
    return base+' This historical numbering evidence does not supply a current annotation, replacement registration code, offering or approval, and does not change its distinct6-4_2025 pool membership.'


def parse(html):
    rows=observe(html)
    requirements=[rule('mit-ai-numbering-'+code.replace('.','-'),
        'Historical numbering context for '+code,SID,
        ['mit-ai-v2025-'+code.replace('.','-')],kind='note',summary=statement(code,row))
        for code,row in rows.items()]
    return dict(id='mit-ai-decision-making-bs',courses=[],requirements=requirements)


SOURCE_PARSERS={URL:parse}
