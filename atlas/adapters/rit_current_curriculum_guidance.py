"""Observe public instructions for determining an enrolled student's curriculum."""
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean
from atlas.adapters.rit_writing_closure import PID
URL='https://www.rit.edu/study/curriculum-requirements'
SOURCE_ID='rit-current-student-curriculum-guidance'

def parse(html):
    s=BeautifulSoup(html,'html.parser');main=s.find('main')
    if not main or s.select('input[type="password"]'):raise ValueError('Public curriculum guidance required')
    title='Curriculum Requirements for Current Students'
    if not any(clean(h.get_text(' ',strip=True))==title for h in main.find_all(['h1','h2'])):raise ValueError('Current-student heading missing')
    text=clean(main.get_text(' ',strip=True))
    if 'academic year that you matriculated into your current program' not in text or 'academic year that you have been advised to follow' not in text:raise ValueError('Curriculum applicability wording changed')
    links=[dict(label=clean(a.get_text(' ',strip=True)),url=a.get('href')) for a in main.find_all('a',href=True)]
    if not any(x['url']=='https://academiccatalog.rit.edu/' for x in links):raise ValueError('Official current catalog destination missing')
    return dict(id=PID,observed_curriculum_guidance=text,observed_curriculum_links=links)

def register(sources,parsers):
    if URL not in sources:sources.append(URL)
    parsers[URL]=parse
