"""Observe only Lewis & Clark's AI minor section, not neighboring CS credentials."""
import re
from bs4 import BeautifulSoup

PROGRAM_ID = 'lewis-clark-ai-minor'
SOURCE_ID = 'lewis-clark-cs-catalog'
BASE = 'https://docs.lclark.edu/undergraduate/'
SOURCES = (BASE+'computerscience/',
           'https://college.lclark.edu/programs/artificial-intelligence/',
           'https://college.lclark.edu/programs/artificial-intelligence/minoring/',
           BASE+'policiesprocedures/majorsminors/',
           BASE+'policiesprocedures/grading/',
           BASE+'policiesprocedures/transfercredit/')


def clean(node):
    return ' '.join(node.get_text(' ', strip=True).split())


def note(suffix, title, summary, source=SOURCE_ID):
    return dict(id=PROGRAM_ID+'-'+suffix, parent_id=None, title=title, kind='note', count=None,
                credits=None, credit_unit='unknown', category='other', source_id=source,
                source_text=None, summary=summary, course_ids=[])


def parse(html):
    soup=BeautifulSoup(html,'html.parser')
    heading=soup.find('h3', string=lambda s:s and s.strip()=='Minor Requirements: Artificial Intelligence')
    if heading is None:
        raise ValueError('AI minor heading missing')
    nodes=[]
    for sibling in heading.next_siblings:
        if getattr(sibling,'name',None)=='h3':break
        nodes.append(str(sibling))
    section=BeautifulSoup(''.join(nodes),'html.parser')
    text=clean(section)
    if 'A minimum of 24 credits distributed as follows:' not in text or 'A minimum of 12 discrete credits are required for the minor.' not in text:
        raise ValueError('AI minor total or exclusive-credit policy changed')
    specs=[('core','Required core','all',None,'foundations',3),
           ('math','One mathematical course','choose_courses',1,'mathematics',8),
           ('advanced','One advanced or applied AI course','choose_courses',1,'ai_ml',1),
           ('context','One social context course','choose_courses',1,'human_context',3)]
    lists=section.find_all('li',recursive=True)
    groups=[[],[],[],[]]
    for li in lists:
        tables=li.find_all('table')
        if not tables:
            link=li.find('a',class_='code')
            if link:groups[0].append((link,clean(li)[len(clean(link)):].strip()))
            continue
        label=clean(li).split(':')[0]
        index={'One mathematical course chosen from':1,'One advanced or applied AI course chosen from':2,'One social context course chosen from':3}.get(label)
        if index is None:raise ValueError('Minor group wording changed')
        for tr in li.find_all('tr'):
            cells=tr.find_all('td');link=tr.find('a',class_='code')
            if link and len(cells)>=2:groups[index].append((link,clean(cells[1])))
    if [len(g) for g in groups]!=[3,8,1,3]:raise ValueError('AI option pools changed')
    courses=[];requirements=[]
    for spec,entries in zip(specs,groups):
        suffix,title,kind,count,category,_=spec
        r=note(suffix,title,None);r.update(kind=kind,count=count,category=category)
        for link,name in entries:
            code=clean(link)
            if not re.fullmatch(r'(?:CS|ECON|MATH|PSY|PHIL|RHMS) \d{3}',code):raise ValueError('Course code changed')
            cid='lewis-clark-'+code.lower().replace(' ','-')
            courses.append(dict(id=cid,code=code,name=name,description=None,prerequisites=None,credits=None,
                                credit_unit='unknown',category='ai_ml' if code=='CS 369' else category,
                                source_id=SOURCE_ID,url=SOURCES[0],public_site=None,syllabus=None))
            r['course_ids'].append(cid)
        requirements.append(r)
    requirements += [note('total','Minimum total','Complete at least 24 credits.'),note('exclusive','Exclusive minor credits','At least 12 credits must be discrete to this minor.')]
    return dict(id=PROGRAM_ID,title='Artificial Intelligence',award_level='minor',program_kind='minor',
                curriculum_status='partial',courses=courses,requirements=requirements,
                notes=['Local AI minor observation; general minor rules require separate review.'])


SUMMARIES={
 'CS 171':('functional decomposition','Programming fundamentals and decomposition of computational problems.'),
 'CS 172':('Abstract data types','Data structures, algorithms and object-oriented programming.'),
 'CS 230':('ordinary differential equations','Computational approaches to calculus, linear systems and differential equations.'),
 'CS 369':('adversarial search','Intelligent agents, search, machine learning and philosophical questions about intelligence.'),
 'CS 469':('diffusion models','Deep-network construction and training, architectures and language/image applications.'),
}

def parse_course_metadata(html):
    soup=BeautifulSoup(html,'html.parser');result=[]
    for block in soup.find_all('div',class_='courseblock'):
        title=block.find(class_='courseblocktitle')
        if title is None:continue
        match=re.match(r'(CS \d{3})\s+(.+)',clean(title))
        if not match or match[1] not in SUMMARIES:continue
        code,name=match.groups();text=clean(block);guard,summary=SUMMARIES[code]
        pre=re.search(r'Prerequisites:\s*(.*?)\s*Usually offered:',text)
        credits=re.search(r'Semester credits:\s*(\d+)\.',text)
        if guard not in text or not pre or not credits:raise ValueError('Course metadata changed: '+code)
        result.append(dict(code=code,name=name,description=summary,prerequisites=re.sub(r'\s+([,.])',r'\1',pre[1]),credits=int(credits[1]),credit_unit='semester_hours'))
    if len(result)!=5:raise ValueError('Expected five in-scope CS course blocks')
    return result


def guarded_notes(html, specs, source):
    text=clean(BeautifulSoup(html,'html.parser'));result=[]
    for suffix,title,guards,summary in specs:
        if not all(g in text for g in guards):raise ValueError('Policy changed: '+suffix)
        result.append(note(suffix,title,summary,source))
    return result


def parse_minor_policy(html):
    return guarded_notes(html,[
      ('residence','Minor residence and overlap',('At least 12 semester credits for the minor must be taken at Lewis & Clark','12 semester credits must be exclusive to the minor'), 'Complete 12 semester credits at Lewis & Clark and 12 exclusive to this minor; the exclusive credits cannot satisfy another major or minor.'),
      ('gpa','Minor GPA',('cumulative GPA of 2.000 or higher in minor courses',),'Maintain a minor GPA of at least 2.000.'),
      ('declare','Declaration and certification',('Students declare a minor on a form','Department chairs are responsible for verifying','No more than two minors'),'Declare with the registrar; the chair certifies completion on the degree application. At most two minors appear on the transcript.'),
      ('shortage','Approved credit shortage',('For minors: a shortage of 1 credit','Subcommittee on Petitions and Appeals','advanced standing credit, L&C overseas credit'),'The registrar may waive a one-credit shortage arising from the specified advanced-standing, overseas or approved transfer-credit circumstances. Other shortages require petition approval.'),
    ],'lewis-clark-minor-policy')


def parse_transfer_policy(html):
    return guarded_notes(html,[
      ('transfer','Transfer approval',('Major/Minor Requirements','at the discretion of the chair or program director','grade below C- (1.700)'),'Transfer courses require registrar eligibility review and chair/program-director approval for minor applicability; grades must meet the C− threshold.'),
      ('transfer-cr','Transfer CR/NC evidence',('P/NP or CR/NC will not be accepted for transfer unless','passing grades are considered to be C- or better'),'Transferred pass/no-pass or credit/no-credit courses require the awarding institution to document a passing standard of C− or higher.'),
    ],'lewis-clark-transfer-policy')


def parse_grading_policy(html):
    return guarded_notes(html,[
      ('grading','Credit/no-credit and repeated courses',('Consent of the instructor is required for the CR/NC option','CR/NC grades are not used for calculating','course credits only once'),'CR/NC election in regularly graded courses requires instructor consent and timely filing; it is excluded from GPA. Repeating a nonrepeatable course does not earn credit twice; both grades enter GPA.'),
    ],'lewis-clark-grading-policy')


# Bounded metadata review: observations do not certify a curriculum audit.
from functools import partial as _metadata_partial
from atlas.adapters.small_complete_metadata_batch2 import CONFIG as _metadata_config, parse_metadata as _parse_metadata

SOURCE_PARSERS = globals().get("SOURCE_PARSERS", {})
for _key in ['lc-econ', 'lc-math', 'lc-psy', 'lc-phil', 'lc-rhms']:
    _cfg = _metadata_config[_key]
    if _cfg["url"] not in SOURCES:
        SOURCES = list(SOURCES) + [_cfg["url"]]
    SOURCE_PARSERS[_cfg["url"]] = _metadata_partial(_parse_metadata, key=_key)
