"""Read settled public language/health cards; manual reviews are separate evidence."""
import json
import re
from pathlib import Path
from functools import partial
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course
from atlas.adapters.rit_immersion_rule_observer import parse as observe_rules
from atlas.adapters.rit_writing_closure import PID

MANIFEST=json.loads(Path(__file__).with_suffix('.json').read_text())
SPECS={s['url']:(s['title'].split(' — ')[0],s['id']) for s in MANIFEST['sources']}
TARGETS=set(MANIFEST['courses'])


def parse(html, *, url):
    title,sid=SPECS[url]
    observed=observe_rules(html,title=title)
    codes={code for table in observed['observed_tables'] for row in table['rows'] for code in row['course_codes']}
    soup=BeautifulSoup(html,'html.parser');courses=[]
    for card in soup.select('.courseblock'):
        def value(selector):
            node=card.select_one(selector)
            return clean(node.get_text(' ',strip=True)) if node else None
        code,name=value('.detail-code'),value('.detail-title')
        if code not in codes or code not in TARGETS or not name:
            raise ValueError('Unbound language/health course card')
        amount=value('.detail-hours_html') or ''
        match=re.fullmatch(r'\((\d+(?:\.\d+)?)(?:[-–](\d+(?:\.\d+)?))? Credits?\)',amount)
        if not match:raise ValueError('Unrecognized course credit amount')
        description=value('.courseblockextra')
        if not description:raise ValueError('Course description missing')
        c=course(PID,code,name,sid,url,None if match[2] else float(match[1]))
        c.update(description=description,prerequisites=value('.detail-requisites'))
        c['notes']=[]
        if match[2]:c['notes'].append('Printed variable credit amount: '+amount+'. No scalar amount selected.')
        attrs=value('.detail-ge_attrs')
        if attrs:c['notes'].append(attrs)
        # Eligibility embedded in the body remains in the observed description;
        # no prerequisite or taxonomy is inferred from a label or contact hours.
        courses.append(c)
    if not courses:raise ValueError('No settled language/health cards')
    if len({c['id'] for c in courses})!=len(courses):raise ValueError('Duplicate course cards')
    return dict(id=PID,courses=courses,requirements=[],observed_immersion_tables=observed['observed_tables'])


SOURCE_PARSERS={url:partial(parse,url=url)for url in SPECS}
