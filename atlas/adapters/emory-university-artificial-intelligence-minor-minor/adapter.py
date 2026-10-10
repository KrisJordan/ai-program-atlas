"""Observe Emory's AI-only requirements and separately parse its elective PDF text."""
import re
from atlas.adapters.national_curriculum_common import require_phrases,content,clean,course,rule,policy
PROGRAM_ID='emory-university-artificial-intelligence-minor-minor'
SOURCES=('https://computerscience.emory.edu/undergraduate/degrees-and-requirements/minors.html',)
SOURCE_ID=PROGRAM_ID+'-official'
ELECTIVE_URL='https://computerscience.emory.edu/documents/electives/ai-minor-electives.pdf'
ELECTIVE_ID='emory-ai-minor-electives'

def parse(html):
    root=content(html,'Minor in Artificial Intelligence')
    require_phrases(root, ['minimum GPA requirement of 2.0', 'better of the grades', 'as long as the subjects differ', 'cannot be used as an elective for the CS minors'])
    heading=next((n for n in root.find_all(['h2','h3','h4']) if clean(n.get_text(' ',strip=True))=='AI Minor'),None)
    if not heading:raise ValueError('AI-specific section missing')
    table=heading.find_next('table');courses=[];groups=[]
    for i,row in enumerate(table.find_all('tr')[1:]):
        cells=row.find_all('td',recursive=False)
        if len(cells)!=2:raise ValueError('Unknown AI minor table row')
        left=clean(cells[0].get_text(' ',strip=True));right=clean(cells[1].get_text(' ',strip=True))
        choice=re.search(r'\((\d+)\) courses? chosen from',left)
        ids=[]
        if choice:
            entries=cells[1].find_all('p')
            for item in entries:
                code,name=clean(item.get_text(' ',strip=True)).split(':',1)
                c=course('emory',code.strip(),name.strip(),SOURCE_ID,SOURCES[0],category='ai_ml');courses.append(c);ids.append(c['id'])
            if not entries:
                if not cells[1].find('a',href=ELECTIVE_URL):raise ValueError('Elective PDF link changed')
                groups.append(rule('emory-electives','Interdisciplinary electives',SOURCE_ID,kind='choose_courses',count=int(choice[1]),summary='Choose two courses from the separately published AI minor elective list. That list is reviewed separately from this HTML page.'));continue
            groups.append(rule('emory-choice-'+str(i),'Machine learning choice' if i==3 else 'Language/text/data choice',SOURCE_ID,ids,kind='choose_courses',count=int(choice[1]),category='ai_ml'))
        else:
            if not re.fullmatch(r'CS \d{3}',left):raise ValueError('Unrecognized required course code')
            c=course('emory',left,right,SOURCE_ID,SOURCES[0],category='foundations' if left=='CS 110' else 'human_context' if left=='CS 312' else 'ai_ml');courses.append(c)
            groups.append(rule('emory-required-'+left.lower().replace(' ','-'),right,SOURCE_ID,[c['id']]))
    # Department explicitly allows CS170 for CS110; obtain its title from the adjacent CS table.
    substitution=None
    for row in root.find_all('tr'):
        cells=row.find_all('td',recursive=False)
        if len(cells)==2 and clean(cells[0].get_text(' ',strip=True))=='CS 170':
            substitution=course('emory','CS 170',clean(cells[1].get_text(' ',strip=True)),SOURCE_ID,SOURCES[0],category='foundations');break
    if substitution is None:raise ValueError('CS170 substitution metadata missing')
    if 'CS 170 is a viable substitution for CS 110' not in clean(root.get_text(' ',strip=True)):raise ValueError('Substitution policy changed')
    courses.append(substitution);g=next(g for g in groups if g['id']=='emory-required-cs-110');g.update(kind='choose_courses',count=1,title='Introductory computing alternative',summary='CS170 is an explicitly approved substitute for CS110.');g['course_ids'].append(substitution['id'])
    for marker,gid,title,summary in [
      ('taken for a letter grade','grading','Grading and GPA','All counted courses require letter grades. Department major/minor GPA must be at least2.0; repeated courses use the better grade.'),
      ('cannot be combined with any other CS or AI major/minor','eligibility','Combination restriction','The CS/AI minors cannot be combined with any other CS or AI major or minor.'),
      ('must successfully complete all prerequisite courses','prerequisites','Prerequisite enforcement','All course prerequisites must be completed before enrollment; the department states this cannot be bypassed. Consult the current Atlas course catalog.'),
      ('more than one CS 485 topics course','topics','Repeatable topics','Multiple CS485 topics may count when their subjects differ.'),
      ('CS 323: Machine Learning Applications','scope','CS323 scope','CS323 was developed for the AI minor and cannot be an elective for the CS minors.')]:
      groups.append(policy(root,marker,'emory-'+gid,title,summary,SOURCE_ID))
    return dict(id=PROGRAM_ID,title='Artificial Intelligence',award_level='minor',program_kind='minor',courses=courses,requirements=groups)


def parse_electives_text(text):
    """Text extracted from the official two-page PDF; no embedded seed course pool."""
    if 'AI Minor Electives' not in text or not re.search(r'choose any two',text,re.I):raise ValueError('Elective document identity or choice missing')
    courses=[]
    for line in text.splitlines():
        line=clean(line)
        # PDF text positions split ECON312; join only this observed numeric token.
        line=re.sub(r'^(ECON) 31 2 ',r'\1 312 ',line)
        m=re.fullmatch(r'([A-Z]+ \d{3}R?)\s+(.+)',line)
        if not m:continue
        code,name=m.groups()
        if code=='CHEM 470':name+=' / Drug Discovery'
        category='mathematics' if code.startswith(('MATH','POLS 376','QTM 315')) else 'human_context' if code.startswith(('PHIL','NBB','SOC','FILM','ENG','PSYC','QTM 310')) else 'applications'
        courses.append(course('emory',code,name,ELECTIVE_ID,ELECTIVE_URL,category=category,topic=name if code in ('CS 485','PSYC 471R','CHEM 470') else None))
    if len(courses)<30:raise ValueError('Elective PDF extraction incomplete')
    return dict(id=PROGRAM_ID,courses=courses,requirements=[rule('emory-electives','Interdisciplinary electives',ELECTIVE_ID,[c['id'] for c in courses],kind='choose_courses',count=2,summary='Choose two approved courses. Named special-topic restrictions apply; the department warns the list may evolve. CHEM470 lists Machine Learning for Chemistry and Drug Discovery as approved topics.')])
