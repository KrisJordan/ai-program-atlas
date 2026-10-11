"""Observe the public AI in Society route without selecting it for AI BS."""
import importlib
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean
from atlas.adapters.rit_writing_closure import PID

URL='https://www.rit.edu/study/ai-society-immersion'
SID='rit-ai-society-route-2026-2027'


def parse(html):
    # Reuse the already source-specific local route parser. Its local completion
    # and program aims must never become host-degree completion or outcomes.
    local=importlib.import_module('atlas.adapters.rit-ai-society-immersion.adapter').parse(html)
    if not local.get('requirements'):
        raise ValueError('Rendered AI in Society immersion curriculum required')
    courses=[]
    for original in local['courses']:
        c=dict(original)
        c.update(id=PID+'-'+c['code'].lower(),source_id=SID,category='other')
        courses.append(c)
    bycode={c['code']:c for c in courses}
    seen=set()
    for card in BeautifulSoup(html,'html.parser').select('.courseblock'):
        def value(selector):
            n=card.select_one(selector)
            return clean(n.get_text(' ',strip=True)) if n else None
        code=value('.detail-code')
        if code not in bycode or code in seen:raise ValueError('Unbound or duplicate course card')
        seen.add(code);c=bycode[code]
        if value('.detail-title')!=c['name']:raise ValueError('Course title differs from route row')
        m=re.fullmatch(r'\((\d+(?:\.\d+)?) Credits?\)',value('.detail-hours_html') or '')
        if not m:raise ValueError('Course amount missing')
        c.update(credits=float(m[1]),description=value('.courseblockextra'),prerequisites=value('.detail-requisites'))
        if not c['description']:raise ValueError('Course description missing')
    return {'id':PID,'courses':courses,'requirements':[],
            'observed_local_immersion_requirements':local['requirements'],
            'notes':['This is one optional declared immersion route; its required course is not a universal AI BS requirement. Source categories are unreviewed; no host degree outcomes or audit emitted.']}


def register(sources,parsers):
    if URL not in sources:sources.append(URL)
    parsers[URL]=parse
