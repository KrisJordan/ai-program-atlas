"""Bounded observations of the five actually rendered current Rutgers subject tabs."""
import hashlib
import json
import re
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course, rule
from atlas.adapters.njit_degree_policies import PID

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html, subject):
    source = SPEC['sources'][subject]
    soup = BeautifulSoup(html, 'html.parser')
    panels = soup.select('[role=tabpanel]')
    selected = soup.select('[role=tab][aria-selected=true]')
    headings = [clean(x.get_text(' ',strip=True)) for x in soup.select('h1')]
    if len(panels)!=1 or len(selected)!=1 or clean(selected[0].get_text(' ',strip=True))!=source['tab'] or source['heading'] not in headings:
        raise ValueError('Actual Rutgers subject course tab required')
    panel=panels[0]
    if hashlib.sha256(clean(panel.get_text(' ',strip=True)).encode()).hexdigest()!=source['panel_digest']:
        raise ValueError('Rutgers subject inventory changed; review required')
    wanted={code for code,s in SPEC['courses'].items() if s['subject']==subject}
    seen,courses,conflicts=set(),[],[]
    for block in panel.select('p'):
        text=clean(block.get_text(' ',strip=True))
        match=re.match(r'21:(\d+):(\d+(?:[-,]\d+)*) (.*?) \(([^)]+)\)(.*)',text)
        if not match or match[1]!=subject:continue
        for n in match[2].replace('-',',').split(','):
            code='R'+subject+' '+n
            if code not in wanted:continue
            if code in seen:raise ValueError('Duplicate Rutgers identity')
            seen.add(code);s=SPEC['courses'][code]
            if match[3]!=s['title'] or hashlib.sha256(text.encode()).hexdigest()!=s['digest']:
                raise ValueError('Rutgers course content changed')
            c=course('njit',code,s['title'],PID+'-rutgers-subject-'+subject,source['url'],s['credits'],'semester_hours',s['category'])
            c.update(description=s['description'],prerequisites=s['prerequisites'])
            courses.append(c)
            if s['credit_conflict']:conflicts.append(dict(code=code,rutgers_credits=s['credits'],njit_credits=3))
    if seen!=wanted:raise ValueError('Rutgers course identities missing')
    requirements = []
    if subject == '216':
        requirements.append(rule(PID+'-rutgers-ecology-eligibility', 'Conditional Rutgers ecology option eligibility', PID+'-rutgers-subject-216', ['njit-r216-205','njit-r216-206','njit-r216-109','njit-r216-110'], kind='note', summary='Current Rutgers 21:216:205 and 206 require one another concurrently and 21:120:200 with C or better. These are conditional selection/enrollment rules, not universal additional degree requirements. Green Planet Laboratory 110 requires 109 before or concurrently. Both 109 and 110 exclude majors and students who took or plan to take 21:120:101–102; the source does not further identify the word majors. NJIT lists R216 206 as 3 credits; Rutgers lists its laboratory as 1 credit. No applicability or credit reconciliation is inferred.'))
    return {'id':PID,'courses':courses,'requirements':requirements,'observed_credit_conflicts':conflicts}


SOURCE_PARSERS={s['url']:partial(parse,subject=subject) for subject,s in SPEC['sources'].items()}
