"""Observe actual rendered current PATH course panels, never replay a landing page."""
import hashlib
import json
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean,course
from atlas.adapters.william_mary_ba_policy_review import PID

SPEC=json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html,code):
    s=BeautifulSoup(html,'html.parser');e=SPEC[code]
    panels=[p for p in s.select('.panel__content') if p.select_one('.dtl-course-code') and clean(p.select_one('.dtl-course-code').get_text())==code]
    if len(panels)!=1:raise ValueError('Actual rendered PATH course panel missing or duplicated')
    p=panels[0]
    def val(selector):
        nodes=p.select(selector)
        if len(nodes)!=1:raise ValueError('PATH field missing or duplicated: '+selector)
        return clean(nodes[0].get_text(' ',strip=True))
    link=p.select_one('.panel__head .deep-link')
    if not link or 'https://registration.wm.edu/'+link.get('data-query-string','')!=e['url']:
        raise ValueError('PATH term/section identity changed')
    if val('.detail-title')!=e['title'] or val('.dtl-section')!=e['section']:
        raise ValueError('PATH course title or section changed')
    if val('.detail-hours_html')!=str(e['credits'])+' Credit Hours':raise ValueError('PATH credits changed')
    if val('.detail-grade_mode')!='Grade Mode: Standard Letter':raise ValueError('PATH grading mode changed')
    for selector,field in [('.section--description .section__content','description_digest'),('.section--registration_restrictions .section__content','restriction_digest')]:
        if hashlib.sha256(val(selector).encode()).hexdigest()!=e[field]:raise ValueError('PATH reviewed content changed')
    c=course('wm-applied-ai',code,e['title'],PID+'-path-'+code.lower().replace(' ','-'),e['url'],credits=e['credits'],unit='unknown',category=e['category'])
    c['description']='Fall 2026 public course listing: '+e['description']
    c['prerequisites']=val('.section--registration_restrictions .section__content')
    return {'id':PID,'courses':[c],'requirements':[],'notes':['Section-specific Fall 2026 evidence; prerequisite lists preserve their published Boolean wording. No current course listing resolves the distinct degree-plan DATA305/AAI301 conflict. Credit amount is observed, normalized unit remains unknown.']}


def register(parsers):
    for code,e in SPEC.items():
        if e['url'] in parsers:raise ValueError('Duplicate PATH source')
        parsers[e['url']]=partial(parse,code=code)
