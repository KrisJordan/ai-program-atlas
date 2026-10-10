"""Parse the AI minor course tables, row alternatives, and explicit policies."""
import re
from urllib.parse import urljoin
from atlas.adapters.national_curriculum_common import require_phrases,clean,content,course,rule,policy
PROGRAM_ID='northwestern-university-artificial-intelligence-minor-minor-minor'
SOURCES=('https://catalogs.northwestern.edu/undergraduate/engineering-applied-science/artificial-intelligence/artificial-intelligence-minor/',)
SOURCE_ID=PROGRAM_ID+'-official'

def parse(html):
    root=content(html,'Artificial Intelligence Minor')
    require_phrases(root, ['WCAS Computer Science major', 'major in Artificial Intelligence are not eligible', 'by the end of their junior year', 'any other minor or certificate program', 'major requirements of any degree program'])
    tables=root.find_all('table',class_='sc_courselist')
    if len(tables)!=2: raise ValueError('Expected requirements and elective tables')
    courses={};groups=[]; section=None; entries=[]; last=None
    for ti,table in enumerate(tables):
        if ti==1: section='electives'
        for row in table.find_all('tr'):
            cells=row.find_all(['td','th'],recursive=False)
            text=clean(row.get_text(' ',strip=True))
            if 'areaheader' in row.get('class',[]):
                m=re.fullmatch(r'(Prerequisites|Minor Requirements) \((\d+) units\)',text)
                if not m:raise ValueError('Unexpected minor section')
                section='prerequisites' if m[1]=='Prerequisites' else 'core'
                groups.append(rule('nw-'+section,m[1],SOURCE_ID,credits=int(m[2]),unit='units',summary='Published '+m[2]+' units; alternatives are choices, not extra required courses.'))
                last=None;continue
            if len(cells)!=2 or not cells[0].find('a',class_='code'):continue
            a=cells[0].find('a',class_='code');code=clean(a.get_text(' ',strip=True));name=clean(cells[1].get_text(' ',strip=True))
            is_alt='orclass' in row.get('class',[])
            topic=None
            if code in ('COMP_SCI 396-0','COMP_SCI 397-0','COMP_SCI 496-0'):
                topic=name
                if is_alt and last and '(' not in name:
                    topic=last['topic'];name+=' — approved topic: '+topic
            c=course('nw',code,name,SOURCE_ID,urljoin(SOURCES[0],a['href']),category='mathematics' if section=='prerequisites' else 'ai_ml' if section=='electives' or code in ('COMP_SCI 348-0','COMP_SCI 349-0') else 'foundations',topic=topic)
            courses[c['id']]=c
            if is_alt:
                if not last:raise ValueError('Alternative without preceding course')
                last['ids'].append(c['id'])
            else:
                last=dict(section=section,ids=[c['id']],title=name,topic=topic)
                entries.append(last)
    body=clean(root.get_text(' ',strip=True))
    m=re.search(r'(\d+) upper level electives approved for the Artificial Intelligence minor',body)
    if not m:raise ValueError('Elective choice count missing')
    groups.append(rule('nw-electives','Approved upper-level electives',SOURCE_ID,parent='nw-core',kind='choose_courses',count=int(m[1]),credits=int(m[1]),unit='units',summary='Choose three distinct approved courses. Each nested alternative supplies one elective; cross-listed alternatives and the same topic cannot be counted twice. Special-topic approvals apply only to the named topics.'))
    for i,e in enumerate(entries):
        groups.append(rule('nw-entry-'+str(i),e['title'],SOURCE_ID,e['ids'],parent='nw-'+e['section'],kind='choose_courses' if len(e['ids'])>1 else 'all',count=1 if len(e['ids'])>1 else None,summary='Choose one listed alternative for this course slot.' if len(e['ids'])>1 else 'One approved course option.' if e['section']=='electives' else 'Required course.'))
    for marker,gid,title,summary in [
        ('except students completing a BS in Computer Science','eligibility','Eligibility','Open to undergraduate students except CS BS, WCAS CS major, and AI major students. CS students may use their major AI concentration instead.'),
        ('before the end of their first quarter of their junior year','timing','Planning and declaration','Begin before the end of the first junior-year quarter; declare through MAS by the end of junior year.'),
        ('At least 4 units of coursework must be unique','overlap','Distinct coursework','At least four units must be unique to this minor, unused by other minors, certificates, or any major requirements. They may also satisfy McCormick humanities/social sciences, WCAS distribution, or unrestricted electives.')]:
        groups.append(policy(root,marker,'nw-'+gid,title,summary,SOURCE_ID))
    if not courses or not any(e['section']=='electives' for e in entries):raise ValueError('Missing courses')
    return dict(id=PROGRAM_ID,title='Artificial Intelligence Minor',award_level='minor',program_kind='minor',courses=list(courses.values()),requirements=groups,
                notes=['Parsed program-specific requirements and policies. Topic variants have distinct IDs; alternative listings do not create additional course slots. Catalog labels units; no conversion to semester hours.'])
