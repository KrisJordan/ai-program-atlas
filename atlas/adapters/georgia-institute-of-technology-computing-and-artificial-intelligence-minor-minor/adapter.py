"""Observe the catalog minor, separate thread pools, and institute minor policies."""
import re
from urllib.parse import urljoin
from atlas.adapters.national_curriculum_common import require_phrases,clean,content,course,rule,policy
PROGRAM_ID='georgia-institute-of-technology-computing-and-artificial-intelligence-minor-minor'
SOURCES=('https://catalog.gatech.edu/programs/minor-computing-artificial-intelligence/', 'https://www.cc.gatech.edu/academics/threads/intelligence', 'https://catalog.gatech.edu/academics/minors/')
SOURCE_ID=PROGRAM_ID+'-official'
THREAD_ID='gatech-ai-thread-pools'
POLICY_ID='gatech-minor-guidelines'

def parse(html):
    root=content(html,'Minor in Computing and Artificial Intelligence');text=clean(root.get_text(' ',strip=True))
    require_phrases(root, ['complete the minor with 15 hours instead of 16', 'All other minor courses must be completed with a grade of C or higher', 'This includes courses taken at another institution or credit earned through the AP or IB program'])
    if not re.search(r'at least 16 semester hours.*at least 9 hours',text):raise ValueError('Minor minimum changed')
    table=root.find('table',class_='sc_courselist')
    if not table:raise ValueError('Course table missing')
    courses=[];groups=[rule('gt-minimum','Minor minimum and level requirement',SOURCE_ID,kind='note',credits=16,unit='semester_hours',summary='At least16semester hours of CS coursework, including at least9hours at3000level or higher. An ECE substitution exception may reduce the total to15hours; see its unresolved source wording.')]
    section=None
    for row in table.find_all('tr'):
        cells=row.find_all('td',recursive=False)
        if 'areaheader' in row.get('class',[]):section=clean(row.get_text(' ',strip=True));continue
        if len(cells)!=3 or not cells[0].find('a',class_='code'):continue
        a=cells[0].find('a',class_='code');code=clean(a.get_text(' ',strip=True))
        for sup in cells[1].find_all('sup'):sup.decompose()
        name=clean(cells[1].get_text(' ',strip=True));number=clean(cells[2].get_text(' ',strip=True));credits=int(number) if number.isdigit() else None
        c=course('gt',code,name,SOURCE_ID,urljoin(SOURCES[0],a['href']),credits=credits,unit='semester_hours' if credits else 'unknown',category='ai_ml' if code=='CS 3600' else 'systems' if code=='CS 2110' else 'foundations');courses.append(c)
        groups.append(rule('gt-'+code.lower().replace(' ','-'),section+': '+name,SOURCE_ID,[c['id']],summary='Prerequisite; excluded from the16minor hours.' if section=='Prerequisite' else 'Required minor course; CS2110 has an ECE substitution policy.'))
    for category in ('Embodied Intelligence','Approaches to Intelligence'):
        if category not in text:raise ValueError('Elective category missing')
        groups.append(rule('gt-'+category.lower().replace(' ','-'),category,SOURCE_ID,kind='choose_courses',count=1,credits=3,unit='semester_hours',summary='Choose one CS course from this Intelligence Thread category. Non-CS courses in the parent thread cannot count for this minor.'))
    for marker,gid,title,summary in [
      ('disciplines other than computer science','eligibility','Eligibility','Intended for majors outside computer science.'),
      ('CS Minor application is required','application','Application','A CS minor application is required.'),
      ('ECE students with credit for ECE 2035','ece','ECE substitution caveat','The source permits qualifying ECE students to replace CS2110 with a3000/4000level Intelligence Thread CS course and complete15hours. Its eligibility wording says ECE2035 and either ECE2020 without a complete alternative; advisor clarification remains necessary.'),
      ('No Special Problems or Internship','exclusions','Excluded coursework','Special Problems and internship coursework cannot satisfy the CS minor.'),
      ('A grade of A or B is required','grades','Grades','CS1301/CS1315/CS1371 and CS1331 require A or B. Other minor courses require C or better.'),
      ('Only CS courses','cs-only','CS-only rule','Only CS courses count toward the minor.'),
      ('maximum of 3 semester hours of transfer credit','transfer','Transfer limit','At most3semester hours of transfer credit may count, including accepted AP or IB credit.')]:
      groups.append(policy(root,marker,'gt-'+gid,title,summary,SOURCE_ID))
    return dict(id=PROGRAM_ID,title='Computing and Artificial Intelligence',award_level='minor',program_kind='minor',courses=courses,requirements=groups)


def parse_thread(html):
    root=content(html,'Embodied Intelligence');courses=[];groups=[]
    for name in ('Embodied Intelligence','Approaches to Intelligence'):
        heading=next((n for n in root.find_all(re.compile('^h[1-6]$')) if name in clean(n.get_text(' ',strip=True))),None)
        if not heading:raise ValueError('Missing named thread category')
        ul=heading.find_next('ul');ids=[]
        for li in ul.find_all('li'):
            m=re.match(r'(CS\s+\d{4})\s+(.+?),\s*(\d+)$',clean(li.get_text(' ',strip=True)))
            if not m:continue # PSYC belongs to the thread but is excluded by the minor's CS-only rule.
            code,title,credits=m.groups();code=clean(code)
            c=course('gt',code,title,THREAD_ID,SOURCES[1],credits=int(credits),unit='semester_hours',category='ai_ml');courses.append(c);ids.append(c['id'])
        if not ids:raise ValueError('No CS options observed')
        groups.append(rule('gt-'+name.lower().replace(' ','-'),name,THREAD_ID,ids,kind='choose_courses',count=1,credits=3,unit='semester_hours',summary='The minor chooses one CS course from this published thread category; the full CS major thread has a different selection count. Non-CS entries are excluded.'))
    return dict(id=PROGRAM_ID,courses=courses,requirements=groups)


def parse_policies(html):
    root=content(html,'Undergraduate Minor Guidelines');groups=[]
    for marker,gid,title,summary in [
      ('Core IMPACTS courses are restricted from counting','major-overlap','Major overlap and core restriction','Major/minor overlap is allowed by default unless the specific minor imposes breadth restrictions; Core IMPACTS courses cannot count.'),
      ('maximum of 3 credit hours can be shared','minor-overlap','Other minor overlap','At most3credit hours may be shared with another minor.'),
      ('taken on a letter-grade basis','letter','Letter grading','All minor courses require letter grades and C or better; the specific CS prerequisite rules are stricter.'),
      ('must be done by the time or at the time the student applies to graduate','declare','Declaration and award','Declare no later than applying for graduation. Minor and major are conferred together and recorded on the transcript; the minor is not on the diploma and cannot be awarded retroactively.')]:
      groups.append(policy(root,marker,'gt-policy-'+gid,title,summary,POLICY_ID))
    return dict(id=PROGRAM_ID,requirements=groups)
SOURCE_PARSERS={SOURCES[1]:parse_thread,SOURCES[2]:parse_policies}

from atlas.adapters.gatech_minor_followup import COMPUTING_URL, parse_computing
SOURCES += (COMPUTING_URL,)
SOURCE_PARSERS[COMPUTING_URL] = lambda html: parse_computing(html, PROGRAM_ID)
