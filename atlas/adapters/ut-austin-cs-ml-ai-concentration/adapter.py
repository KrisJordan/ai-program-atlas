"""UT CS identity refresh and separately reviewed PDF-text requirement extraction."""
import re
from bs4 import BeautifulSoup

PROGRAM_ID = 'ut-austin-cs-ml-ai-concentration'
TITLE = 'Machine Learning & Artificial Intelligence Concentration'
DIRECTORY = 'https://www.cs.utexas.edu/undergraduate/concentrations'
LEGACY = 'https://www.cs.utexas.edu/concentrations/mlai'
PDF_URL = 'https://www.cs.utexas.edu/sites/default/files/2025-12/UTCS_Concentrations_Course_Listings_12172025.pdf'
SOURCE_ID = PROGRAM_ID + '-course-list'
SOURCES = (DIRECTORY, LEGACY, 'https://ai.utexas.edu/academics')


def clean(text):
    return ' '.join(text.replace('\u200b', '').split())


def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    for node in soup.find_all(['nav', 'footer', 'script', 'style', 'aside']):
        node.decompose()
    main = soup.find('main')
    if main is None or not main.find('h1') or clean(main.find('h1').get_text()) != 'Concentrations':
        raise ValueError('Current undergraduate concentration directory missing')
    heading = main.find(lambda n: n.name in ['h2','h3'] and clean(n.get_text()) == 'Machine Learning & Artificial Intelligence')
    if heading is None or 'current CS student' not in main.get_text(' ',strip=True):
        raise ValueError('ML/AI concentration or CS student context missing')
    link = main.find('a',href=re.compile(r'/sites/default/files/[^?#]+\.pdf$'),string=re.compile('Explore Concentration Courses'))
    if link is None:
        raise ValueError('Current concentration course-list link missing')
    return dict(id=PROGRAM_ID,title=TITLE,award_level='concentration',program_kind='concentration')


def slug(text):
    return re.sub('[^a-z0-9]+','-',text.lower()).strip('-')


def parse_pdf_text(text):
    """Caller must use reviewed PDF extraction; HTML transport does not parse PDFs."""
    text = text.replace('\u200b','')
    if not re.search(r'CONCENTRATIONS\s+COURSE\s+LISTINGS',text):
        raise ValueError('Wrong PDF publication')
    title = 'Machine Learning and Artificial Intelligence Concentration'
    start = re.search(r'^\s*'+title+r'\s*$',text,re.M)
    if not start:
        raise ValueError('ML/AI PDF section missing')
    remainder = text[start.end():]
    end = re.search(r'^\s*Mobile Computing Concentration\s*$',remainder,re.M)
    if not end:
        raise ValueError('PDF section boundary missing')
    section = remainder[:end.start()]
    section = section.replace('These courses may change and additional courses may be added in the future.','')
    normalized = clean(section)
    if not re.search(r'complete one of the following courses:',normalized) or not re.search(r'take three of the following elective classes:',normalized):
        raise ValueError('One-foundation/three-electives rule changed')
    if 'are taken, one may count as an elective.' not in normalized or 'If both ' not in normalized:
        raise ValueError('Unused-foundation eligibility rule missing')
    pieces = re.split(r'^\s*Electives\s*$',section,flags=re.M)
    if len(pieces)!=2:
        raise ValueError('Ambiguous PDF elective boundary')
    def extract(part):
        result=[]
        for line in part.splitlines():
            line=clean(line)
            if line.startswith('●'):
                match=re.fullmatch(r'●\s*(CS\s+\d{3}[A-Z]?(?:\(H\))?(?:\s+\(\d{3}H\))?)\s+(.+)',line)
                if not match:
                    raise ValueError('Unrecognized course bullet; review wrapped/changed list')
                result.append((clean(match.group(1)),clean(match.group(2))))
        return result
    foundations, electives = extract(pieces[0]), extract(pieces[1])
    if len(foundations)!=2 or len(electives)<3:
        raise ValueError('Incomplete concentration course pool')
    rows=foundations+electives
    if len(set(rows))!=len(rows):
        raise ValueError('Duplicate course choice')
    # Permit only the reviewed semantic structure, not new hidden condition prose.
    residue=section
    residue=re.sub(r'^\s*●[^\n]*(?:\n|$)','',residue,flags=re.M)
    residue=clean(residue)
    expected=('Foundation Courses To earn the '+title+', you will need to complete one of the following courses: '
              +'If both '+foundations[0][0]+' '+foundations[0][1]+' and '+foundations[1][0]+' '+foundations[1][1]
              +' are taken, one may count as an elective. Electives You will also need to take three of the following elective classes:')
    if residue != expected:
        raise ValueError('New or conflicting PDF requirement prose requires review')
    courses=[]
    for code,name in rows:
        # Special-topic CS378 instances remain distinct by title; preserve printed honors notation.
        cid=PROGRAM_ID+'-'+slug(code+' '+name)
        courses.append(dict(id=cid,code=code,name=name,description=None,prerequisites=None,credits=None,credit_unit='unknown',category='ai_ml',source_id=SOURCE_ID,url=PDF_URL,public_site=None,syllabus=None))
    foundation_ids=[c['id'] for c in courses[:2]]
    elective_ids=[c['id'] for c in courses[2:]]
    def rule(suffix,title,kind,ids=(),count=None,summary='',parent=None):
        return dict(id=PROGRAM_ID+'-'+suffix,parent_id=PROGRAM_ID+'-'+parent if parent else None,title=title,kind=kind,count=count,credits=None,credit_unit='unknown',category='ai_ml',source_id=SOURCE_ID,source_text=None,summary=summary,course_ids=list(ids))
    requirements=[
        rule('curriculum','Concentration course requirements','all',summary='One foundation plus three electives; the unused foundation is conditionally eligible as an elective.'),
        rule('foundation','Choose one foundation','choose_courses',foundation_ids,1,'Choose one published foundation route; preserve the source’s parenthetical honors notation.',parent='curriculum'),
        rule('electives','Choose three eligible electives','choose_courses',elective_ids+foundation_ids,3,'Choose three listed electives. A foundation route is eligible here only if both foundation routes are taken and the other is used to satisfy the foundation requirement.',parent='curriculum'),
        rule('unused-foundation','Unused foundation may serve as an elective','note',foundation_ids,summary='If both foundation courses are taken, one may count as an elective. The course used for the foundation requirement is not also counted among the three electives.',parent='electives'),
    ]
    return dict(id=PROGRAM_ID,title=TITLE,award_level='concentration',program_kind='concentration',curriculum_status='partial',courses=courses,requirements=requirements)

PDF_TEXT_PARSER = parse_pdf_text

import hashlib
import json
from pathlib import Path
COURSES_URL='https://www.cs.utexas.edu/undergraduate/degrees-and-programs/courses'
CREDIT_URL='https://catalog.utexas.edu/general-information/academic-policies-and-procedures/credit-value-and-course-numbers/'
ADVISING_URL='https://www.cs.utexas.edu/undergraduate/academic-advising'
COURSE_PROFILES=json.loads(Path(__file__).with_name('reviewed-courses.json').read_text())

def parse_course_metadata(html, profiles=None):
    profiles=COURSE_PROFILES if profiles is None else profiles
    soup=BeautifulSoup(html,'html.parser')
    for noise in soup.find_all(['nav','footer','script','style','aside']):noise.decompose()
    main=soup.find('main')
    if main is None or main.h1 is None or clean(main.h1.get_text())!='Undergraduate Courses':
        raise ValueError('Wrong UT undergraduate course directory')
    courses=[]
    for profile in profiles:
        headings=[h for h in main.find_all('h4') if clean(h.get_text())==profile['heading']]
        if len(headings)!=1:
            raise ValueError('Exact reviewed course heading missing or duplicated')
        block=headings[0].find_parent(class_='accordion-item')
        body=block.select_one('.accordion-body') if block else None
        if body is None or hashlib.sha256(clean(body.get_text(' ',strip=True)).encode()).hexdigest()!=profile['sha256']:
            raise ValueError('Changed course description or prerequisites need review')
        courses.append(dict(id=PROGRAM_ID+'-'+slug(profile['code']+' '+profile['name']),code=profile['code'],name=profile['name'],description=profile['description'],prerequisites=profile['prerequisites'],credits=None,credit_unit='unknown',category='ai_ml',source_id=PROGRAM_ID+'-courses',url=COURSES_URL,public_site=None,syllabus=None))
    return dict(id=PROGRAM_ID,courses=courses)

def parse_credit_policy(html):
    soup=BeautifulSoup(html,'html.parser');body=soup.find(id='textcontainer')
    text=clean(body.get_text(' ',strip=True)) if body else ''
    if hashlib.sha256(text.encode()).hexdigest() != 'cb37de986992537d9837e529f871480c9ec9bb5775ecb2092820f44936eacff6':
        raise ValueError('Changed credit-numbering policy needs review')
    if ('Except in the Dell Medical School, the first digit of the course number indicates the credit value of the course in semester hours.' not in text
        or '301 through 399, a value of three semester hours' not in text):
        raise ValueError('UT credit-numbering rule changed or missing')
    return dict(id=PROGRAM_ID,notes=['UT’s published numbering rule assigns three semester hours to courses numbered 301–399. The nine printed concentration routes all use a 3xx code; this does not resolve honors/topic identity or individual prerequisites.'])

SOURCE_PARSERS={COURSES_URL:parse_course_metadata,CREDIT_URL:parse_credit_policy}
SOURCES=SOURCES+(COURSES_URL,CREDIT_URL,ADVISING_URL)
