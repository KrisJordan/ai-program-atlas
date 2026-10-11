"""Bounded actual clinic content; exact evidence guard, no review certification."""
from pathlib import Path
import hashlib
import json
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import course,rule

PID='mit-ai-decision-making-bs'
SPECS=json.loads(Path(__file__).with_name('reviewed_clinic.json').read_text())
DESCRIPTION='Students study cyberattack risks and defensive social engineering, then work in teams with public-sector or healthcare clients to assess vulnerabilities and recommend improvements. Technical security practices are combined with organizational capacity, communication and client collaboration.'


def parse(key,html):
    spec=SPECS[key];soup=BeautifulSoup(html,'html.parser');main=soup.find('main')
    if main is None or soup.find('input',attrs={'type':'password'}):
        raise ValueError('Public clinic content missing')
    text=' '.join(main.get_text(' ',strip=True).split())
    if hashlib.sha256(text.encode()).hexdigest()!=spec['content_digest']:
        return dict(id=PID,courses=[],requirements=[],notes=['Clinic source content changed; prior content interpretation withheld for review.'])
    sid=spec['source_id'];c=course('mit-ai-hass-urban','11.074','Cybersecurity Clinic',sid,spec['url'],unit='units',category='other')
    c['description']=DESCRIPTION if key=='news' else None
    if key=='home':
        summary='The public clinic site states participation is available to registered MIT, Harvard and Wellesley students. The first four weeks include instructional modules and a certification exam; the rest involves a team vulnerability assessment for a real client. This is a conditional course route, not a new fixed degree requirement. Formal prerequisite subjects and credit units are not stated here.'
    else:
        summary='The July13,2026 official account says students must pass the preparatory exam on the first attempt to receive a field assignment. This is an in-course condition, not an inferred prior-course prerequisite. It describes technical security practice alongside organizational and client work. No current-term offering or approved concentration plan is assumed.'
    c['notes']=[summary]
    return dict(id=PID,courses=[c],requirements=[rule('mit-ai-clinic-'+key,'Cybersecurity Clinic: '+('participation and structure'if key=='home'else'field-assignment condition'),sid,parent='mit-ai-hass-urban',kind='note',summary=summary)])


SOURCE_PARSERS={spec['url']:(lambda html,key=key:parse(key,html))for key,spec in SPECS.items()}
