"""Current USF attribute evidence and manually reviewed course observations."""
from functools import partial
import hashlib
import json
from pathlib import Path
from atlas.adapters.national_curriculum_common import clean, content, course
from importlib import import_module
_base=import_module('atlas.adapters.university-of-south-florida-artificial-intelligence-bs-degree.remaining_courses')
PID=_base.PID
REVIEWS=json.loads(Path(__file__).with_name('general_education_course_reviews.json').read_text())
FIELDS=(*_base.FIELDS,'lbltampacurr')

def parse_course(html,review):
    root=content(html,'Course Details')
    heading=next((clean(h.get_text(' ',strip=True)) for h in root.find_all('h2') if clean(h.get_text()).startswith(review['code']+':')),None)
    if not heading:raise ValueError('USF GE exact course heading missing')
    values={}
    for field in FIELDS:
        element=root.find(id='MainContent_'+field)
        if element is None:raise ValueError('USF GE course field missing: '+field)
        values[field]=clean(element.get_text(' ',strip=True))
    digest=hashlib.sha256(json.dumps(dict(heading=heading,fields=values),sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    if digest!=review['observed_fields_sha256']:raise ValueError('USF GE course content or designation changed; human review required')
    c=course('usf',review['code'],heading.split(':',1)[1].strip(),review['source_id'],review['url'],credits=float(values['lblcredithours']),category=review['category'])
    c['id']=review['course_id'];c['description']='2026–2027 public course inventory: '+review['summary']
    c['prerequisites']='; '.join(label+': '+values[field] for label,field in _base.LABELS if values[field]) or None
    return dict(id=PID,courses=[c])
PARSERS={r['url']:partial(parse_course,review=r) for r in REVIEWS}
