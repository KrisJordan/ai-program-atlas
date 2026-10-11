"""Public first-year seminar policy and individually read art option."""
import hashlib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course, rule
from atlas.adapters.njit_degree_policies import PID

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())
FYS_DESCRIPTION = 'University transition combines academic and study skills, campus resources, career connections, self-assessment and social adjustment; no one taxonomy subject dominates this broad orientation.'
AD_DESCRIPTION = 'Iterative drawing studies visual art and develops creative ideation and communication through sketching and interpretation of existing work.'


def guarded(root, key):
    if root is None or hashlib.sha256(clean(root.get_text(' ',strip=True)).encode()).hexdigest() != SPEC[key]['digest']:
        raise ValueError('NJIT reviewed '+key+' content missing or changed')


def seminar(html):
    soup = BeautifulSoup(html,'html.parser')
    root = soup.select_one('.field--name-field-content')
    guarded(root,'seminar')
    sid = PID+'-seminar-policy'
    # This policy does not state credits. The separate degree plan establishes
    # the zero-credit amount; this partial observation does not manufacture it.
    c = dict(id='njit-fys-sem',code='FYS SEM',name='First-Year Student Seminar',
             description=FYS_DESCRIPTION,category='other',source_id=sid,url=SPEC['seminar']['url'],
             public_site=SPEC['seminar']['url'])
    r = rule(PID+'-seminar-completion','First-year seminar completion policy',sid,[c['id']],kind='note',
        summary='The seminar is a graduation requirement for new first-time students. A satisfactory S grade is required; otherwise retake and pass before graduation. Retakes are online and asynchronous. Attendance is mandatory; two or more absences put the student at risk of failure, not an automatic stated failure rule. Participation in discussion is required.')
    return {'id':PID,'courses':[c],'requirements':[r]}


def art(html):
    soup = BeautifulSoup(html,'html.parser')
    blocks = [b for b in soup.select('.courseblock') if clean(b.get_text(' ',strip=True)).startswith('AD 333.')]
    if len(blocks)!=1:
        raise ValueError('NJIT AD333 identity missing or duplicate')
    root = blocks[0]
    guarded(root,'art')
    sid = PID+'-art-option-review'
    c = course('njit','AD 333','Sketching for Art + Ideation',sid,SPEC['art']['url'],3,'semester_hours','human_context')
    c['description'] = AD_DESCRIPTION
    c['prerequisites'] = ' '.join(re.findall(r'(?:Prerequisites?|Restrictions?):\s*[^.]+\.?',clean(root.get_text(' ',strip=True))))
    return {'id':PID,'courses':[c]}


SOURCE_PARSERS = {SPEC['seminar']['url']:seminar,SPEC['art']['url']:art}
