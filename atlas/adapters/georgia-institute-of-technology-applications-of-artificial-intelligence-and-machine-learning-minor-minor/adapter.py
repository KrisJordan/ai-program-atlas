"""Extract all four whole-track pathways and minor-specific policy restrictions."""
import importlib
import re
from urllib.parse import urljoin
from atlas.adapters.national_curriculum_common import content,clean,course,rule,policy
PROGRAM_ID='georgia-institute-of-technology-applications-of-artificial-intelligence-and-machine-learning-minor-minor'
SOURCES=('https://catalog.gatech.edu/programs/minor-artificial-intelligence-machine-learning/','https://catalog.gatech.edu/academics/minors/')
SOURCE_ID=PROGRAM_ID+'-official'

def parse(html):
    root=content(html,'Minor in Applications of Artificial Intelligence and Machine Learning')
    tables=root.find_all('table',class_='sc_courselist')
    if len(tables)!=4:raise ValueError('Expected four catalog tracks')
    courses={};groups=[rule('gt-apps-tracks','Select one complete track',SOURCE_ID,kind='alternative',summary='Choose one whole track. Mixing requirements across tracks is prohibited; any admitted student may choose a track regardless of home college, subject to prerequisites.')]
    for ti,t in enumerate(tables):
        heading=t.find_previous('h6');title=clean(heading.get_text(' ',strip=True)) if heading else ''
        if not title.endswith('Track'):raise ValueError('Track heading absent')
        tid='gt-apps-track-'+str(ti);tg=rule(tid,title,SOURCE_ID,parent='gt-apps-tracks',unit='semester_hours');groups.append(tg);group=None
        for row in t.find_all('tr'):
            cells=row.find_all('td',recursive=False)
            if not cells:continue
            text=clean(row.get_text(' ',strip=True));first=clean(cells[0].get_text(' ',strip=True))
            if 'listsum' in row.get('class',[]):tg['credits']=int(clean(cells[-1].get_text()));continue
            m=re.match(r'Core Course (\d)',first)
            if m:
                choose='Select one' in first
                group=rule(tid+'-core-'+m[1],first,SOURCE_ID,parent=tid,kind='choose_courses' if choose else 'all',count=1 if choose else None,credits=int(clean(cells[-1].get_text())) if clean(cells[-1].get_text()).isdigit() else None,unit='semester_hours');groups.append(group);continue
            if first.lower().startswith('elective courses'):
                group=rule(tid+'-electives','Electives',SOURCE_ID,parent=tid,kind='choose_courses',count=2,credits=6,unit='semester_hours',summary='Choose two approved elective courses (6hours). Approved AI/ML research may supply up to3hours, with designated unit approval. Named topics only.');groups.append(group);continue
            if first.startswith('Select '):
                if group is None:raise ValueError('Choice directive without category')
                m=re.search(r'Select (\d+|two|one)',first);group['count']={'two':2,'one':1}.get(m[1],int(m[1]) if m[1].isdigit() else None);group['kind']='choose_courses';continue
            if first.startswith('Research Credit'):
                if group is None:raise ValueError('Research option outside elective group')
                groups.append(rule(tid+'-research','Approved research option',SOURCE_ID,parent=group['id'],kind='note',credits=3,unit='semester_hours',summary='At most3hours of AI/ML-related research, reviewed and approved by the designated academic unit. XXXX4699 is a catalog placeholder, not a verified course code.'));continue
            a=cells[0].find('a',class_='code')
            if not a:continue
            if group is None or len(cells)!=3:raise ValueError('Course without requirement group')
            code=first;name=clean(cells[1].get_text(' ',strip=True));number=clean(cells[2].get_text());credit=int(number) if number.isdigit() else None
            topic=name if 'Special Topics' in name else None
            c=course('gt-apps',code,name,SOURCE_ID,urljoin(SOURCES[0],a['href']),credits=credit,unit='semester_hours' if credit else 'unknown',category='human_context' if code=='PHIL 3101' else 'mathematics' if group['id'].endswith('core-1') else 'applications',topic=topic)
            courses[c['id']]=c;group['course_ids'].append(c['id'])
        if tg['credits'] is None:raise ValueError('Track total missing')
    for marker,gid,title,summary in [
      ('minor is open to students pursuing majors','eligibility','Eligibility','Eligible colleges are Ivan Allen Liberal Arts, Engineering, Scheller Business and Sciences; catalog directs students to the minor website for up-to-date eligible majors and advisers.'),
      ('No “mix and match” is allowed','whole-track','Whole-track rule','Students must choose a complete track and may not mix track requirements. Discuss compatibility with the academic adviser.'),
      ('Only 3 credit hours of research','research','Research credit','Research must address AI/ML and receive designated unit approval; no more than3hours may count as an elective.'),
      ('can fulfill the BMED 2400 pre-requisites','bmed','BMED2400 alternative prerequisites','Ivan Allen and Scheller students taking Engineering-track BMED2400 may satisfy its prerequisites with MATH1712 plus CS1315 or CS1301.'),
      ('must take CS 1301 or an equivalent approved programming language course','programming','Scheller programming prerequisite','The Scheller track requires CS1301 or an approved equivalent programming course as prerequisite for AI in Business.'),
      ('At least two courses must be taken outside','breadth','School breadth','Take at least two courses outside the home school and courses from at least two schools. Cross-listed courses are not outside the home school for students in any cross-listing school.'),
      ('grade of C or higher','grades','Grade and level minima','Every minor course needs C or better; at least9credits must be at3000level or higher.'),
      ('No course counted towards this minor','overlap','Overlap restrictions','No minor course may count toward another undergraduate minor or certificate. Major overlap follows Institute restrictions without additional minor restrictions.')]:
      groups.append(policy(root,marker,'gt-apps-'+gid,title,summary,SOURCE_ID))
    return dict(id=PROGRAM_ID,title='Applications of Artificial Intelligence and Machine Learning',award_level='minor',program_kind='minor',courses=list(courses.values()),requirements=groups)


def parse_institute_policies(html):
    original=importlib.import_module('atlas.adapters.georgia-institute-of-technology-computing-and-artificial-intelligence-minor-minor.adapter').parse_policies(html)
    original['id']=PROGRAM_ID
    # This minor's specific rule prohibits all other-minor overlap, superseding the general allowance.
    original['requirements']=[g for g in original['requirements'] if g['id']!='gt-policy-minor-overlap']
    for g in original['requirements']:
        if g['id']=='gt-policy-letter':g['summary']='All minor courses require letter grades and C or better.'
    return original
SOURCE_PARSERS={SOURCES[1]:parse_institute_policies}
