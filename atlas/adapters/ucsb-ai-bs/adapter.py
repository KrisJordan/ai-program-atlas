"""UCSB AI program curriculum webpage; sample schedules never become requirements."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, requirement, text
PROGRAM_ID='ucsb-ai-bs'
SOURCES=('https://ai.cs.ucsb.edu/curriculum','https://ai.cs.ucsb.edu/','https://ai.cs.ucsb.edu/sites/default/files/2026-04/AI%20major%20rqmnts_4.10%20(1).pdf','https://www.cs.ucsb.edu/index.php/happenings/announcement/ucsb-launches-dedicated-website-new-bs-artificial-intelligence-inaugural')


def parse(html):
    s=BeautifulSoup(html,'html.parser');h=s.find('h1')
    if h is None or text(h)!='Curriculum' or not any(text(h)=='Bachelor of Science in Artificial Intelligence' for h in s.find_all('h2')):raise ValueError('UCSB curriculum heading changed')
    body=text(s.find('main') or s)
    if 'Core Areas' not in body or 'Degree Requirements' not in body or '180 total units' not in body:raise ValueError('UCSB requirement sections missing')
    table=next((t for t in s.find_all('table') if [text(h) for h in t.find_all('th')]==['Course Code','Name','Units']),None)
    if table is None:raise ValueError('UCSB preparation table missing')
    sid=PROGRAM_ID+'-curriculum';records={};nodes=[]
    def add(key,label,**kw):
        n=requirement(PROGRAM_ID,key,label,sid,unit='quarter_hours',**kw);nodes.append(n);return n['id']
    root=add('degree','Degree total',credits=180)
    prep=add('preparation','Preparation for the major',parent=root,category='foundations')
    for row in table.find_all('tr'):
        cells=row.find_all('td')
        if len(cells)!=3:continue
        code=text(cells[0]).upper(); name=text(cells[1]).replace(' New Course','');raw=text(cells[2])
        if not re.fullmatch(r'(MATH|CMPSC|ECE) \d+[A-Z]*',code):raise ValueError('UCSB course code changed')
        c=course(code,name,sid,SOURCES[0],credits=int(raw) if raw.isdigit() else None,institution='ucsb',unit='quarter_hours',category='mathematics' if code.startswith('MATH') else 'foundations');records[c['id']]=c
        add(c['id'],code,parent=prep,course_ids=[c['id']],category=c['category'])
    area=body.split('Core Areas',1)[1].split('Degree Requirements',1)[0]
    upper=add('upper','Published core areas',parent=root,summary='Named core courses from the Core Areas section; requirement units and choices additionally appear in the worksheet.')
    for m in re.finditer(r'\b(CMPSC|ECE) (\d+[A-Z]*): (.*?)(?=\b(?:CMPSC|ECE) \d|Probability, statistics|Core AI|Responsible AI|Capstone Experience|$)',area):
        code=m[1]+' '+m[2];name=re.split(r'\( new \)| Learn how| Understand the broader',m[3])[0].strip()
        c=course(code,name,sid,SOURCES[0],institution='ucsb',unit='quarter_hours');records.setdefault(c['id'],c)
        if c['id'] not in [i for n in nodes for i in n['course_ids']]:add(c['id'],code,parent=upper,course_ids=[c['id']])
    for key,label,pattern,category in [('major-electives','Major electives',r'Major electives: (\d+)','electives'),('science','Science electives',r'Science electives: (\d+)','other'),('general','General education and university requirements',r'General Education and University requirements: (\d+)','human_context')]:
        match=re.search(pattern,body)
        if not match:raise ValueError('UCSB unit breakdown changed: '+key)
        add(key,label,parent=root,kind='choose_credits',credits=int(match[1]),category=category,summary='Published webpage unit allocation; approved lists and detailed rules require further review.')
    add('capstone','Capstone experience',parent=root,kind='note',summary='The webpage describes an integrative AI project but does not identify its course requirement or units.')
    return dict(id=PROGRAM_ID,title='Artificial Intelligence',award_level='BS',program_kind='degree',catalog_year=None,curriculum_status='partial',courses=list(records.values()),requirements=nodes,notes=['Only explicit curriculum tables/core areas were parsed; illustrative four-year schedules were excluded. Webpage and 2026–27 worksheet conflict on CMPSC 41 units and upper-division totals. Science approved lists and capstone details remain unresolved.'])

from atlas.adapters import ucsb_policies as policies
SOURCES += (policies.REQUIREMENTS_URL, policies.GRADING_URL, policies.ELWR_URL, policies.GEAR_URL)
SOURCE_PARSERS = {
    SOURCES[0]: parse,
    policies.REQUIREMENTS_URL: policies.parse_requirements,
    policies.GRADING_URL: policies.parse_grading,
    policies.ELWR_URL: policies.parse_elwr,
}

from atlas.adapters import ucsb_progression as progression
SOURCES += (progression.TRANSFER_URL, progression.REPEAT_URL, progression.PROGRESS_URL,
            progression.NOTICE_URL, progression.PETITION_URL, progression.FAQ_URL)
SOURCE_PARSERS.update({progression.TRANSFER_URL: progression.parse_transfer,
                      progression.REPEAT_URL: progression.parse_repeat,
                      progression.PROGRESS_URL: progression.parse_progress,
                      progression.NOTICE_URL: progression.parse_notice,
                      progression.PETITION_URL: progression.parse_petitions,
                      progression.FAQ_URL: progression.parse_faq})
SOURCES += (progression.WRITING_URL, progression.GUIDANCE_URL)
SOURCE_PARSERS.update({progression.WRITING_URL: progression.parse_writing})

from atlas.adapters import uc_policy_closure as policy_closure
SOURCES += (policy_closure.CALGETC_URL,)
SOURCE_PARSERS.update({policy_closure.CALGETC_URL: lambda html: policy_closure.parse_calgetc(html, PROGRAM_ID)})
