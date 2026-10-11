"""Read Yeshiva College's current AI concentration table, never its sibling track."""
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
PROGRAM_ID = 'yeshiva-cs-ai-concentration'
SOURCE_ID = PROGRAM_ID + '-catalog'
SOURCES = ('https://yu.smartcatalogiq.com/en/current/university-catalog/undergraduate-programs/yeshiva-college/copy-of-computer-science-artificial-intelligence-bs',)

def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    for noise in soup.find_all(['nav', 'footer', 'script', 'style']):
        noise.decompose()
    main = soup.find(id='main')
    h1 = main.find('h1') if main else None
    if h1 is None or h1.get_text(' ', strip=True) != 'Computer Science, BS':
        raise ValueError('Yeshiva CS BS heading missing or changed')
    body = main.find(id='degreeRequirements')
    if body is None:
        raise ValueError('Degree requirements missing')
    text = ' '.join(body.get_text(' ', strip=True).split())
    if 'The Computer Science major includes concentrations in Artificial Intelligence and Distributed Systems.' not in text:
        raise ValueError('Explicit AI concentration relationship missing')
    if not body.find('a', href=re.compile(r'/general-education-and-jewish-studies-requirements/yeshiva-college-bs$')):
        raise ValueError('Yeshiva College BS scope missing')
    heading = next((h for h in body.find_all('h2') if re.fullmatch(r'Artificial Intelligence Concentration Requirements \(\d+ credits\)', h.get_text(' ', strip=True))), None)
    if heading is None:
        raise ValueError('AI concentration requirement heading missing')
    total = int(re.search(r'\((\d+) credits\)', heading.get_text()).group(1))
    parts = []
    for node in heading.next_siblings:
        if getattr(node, 'name', None) == 'h2':
            break
        parts.append(str(node))
    section = BeautifulSoup(''.join(parts), 'html.parser')
    tables = section.find_all('table')
    if len(tables) != 1:
        raise ValueError('Expected one unambiguous AI required-course table')
    residual = BeautifulSoup(str(section), 'html.parser')
    for table in residual.find_all('table'):
        table.decompose()
    if residual.get_text(' ', strip=True):
        raise ValueError('New concentration prose requires review')
    courses = []
    for row in tables[0].find_all('tr'):
        cells = row.find_all('td', recursive=False)
        if len(cells) != 3:
            raise ValueError('Unexpected requirement row')
        code, name, amount = [c.get_text(' ', strip=True) for c in cells]
        link = cells[0].find('a', href=True)
        if not re.fullmatch(r'(COM|MAT) \d{4}', code) or not name or not re.fullmatch(r'\d+(?:\.\d+)?', amount) or not link:
            raise ValueError('Unrecognized or incomplete course row')
        url = urljoin(SOURCES[0], link['href'])
        if not url.startswith('https://yu.smartcatalogiq.com/en/current/university-catalog/courses-by-subject-area/'):
            raise ValueError('Unexpected course source URL')
        cid = PROGRAM_ID + '-' + code.lower().replace(' ', '-')
        courses.append(dict(id=cid,code=code,name=name,description=None,prerequisites=None,credits=float(amount),credit_unit='unknown',category='other',source_id=SOURCE_ID,url=url,public_site=None,syllabus=None))
    if not courses or len({c['id'] for c in courses}) != len(courses) or sum(c['credits'] for c in courses) != total:
        raise ValueError('Incomplete, duplicate or inconsistent required-course table')
    requirement = dict(id=PROGRAM_ID+'-required',parent_id=None,title='AI concentration required courses',kind='all',count=None,credits=total,credit_unit='unknown',category='other',source_id=SOURCE_ID,source_text=None,summary=f'Complete the published AI concentration course table ({total} source-stated credits). This includes common CS and mathematics requirements of the host major.',course_ids=[c['id'] for c in courses])
    return dict(id=PROGRAM_ID,title='Artificial Intelligence',award_level='concentration',program_kind='concentration',curriculum_status='partial',courses=courses,requirements=[requirement])

# Human-reviewed summaries are emitted only for the exact scoped source prose.
# A changed policy must be reviewed; no seed file supplies parser output.
import hashlib
import json
from pathlib import Path
POLICY_PROFILES = json.loads(Path(__file__).with_name('reviewed-policies.json').read_text())
FAQ_PROFILES = json.loads(Path(__file__).with_name('reviewed-faq.json').read_text())
DEPARTMENT = 'https://www.yu.edu/yeshiva-college/ug/computer-science'

def policy_digest(text):
    return hashlib.sha256(' '.join(text.split()).encode()).hexdigest()

def policy_note(profile):
    return dict(id=PROGRAM_ID+'-policy-'+profile['id'],parent_id=None,title=profile['title'],kind='note',count=None,credits=None,credit_unit='unknown',category='other',source_id=profile['source_id'],source_text=None,summary=profile['summary'],course_ids=[])

def parse_policy(html, profile):
    soup=BeautifulSoup(html,'html.parser')
    for noise in soup.find_all(['nav','footer','script','style']):noise.decompose()
    main=soup.find(id='main')
    if main is None or main.find('h1') is None or main.h1.get_text(' ',strip=True)!=profile['heading']:
        raise ValueError('Wrong undergraduate policy scope')
    if policy_digest(main.get_text(' ',strip=True))!=profile['sha256']:
        raise ValueError('Changed policy prose needs review')
    return dict(id=PROGRAM_ID,requirements=[policy_note(profile)])

def parse_department_policies(html):
    soup=BeautifulSoup(html,'html.parser')
    for noise in soup.find_all(['nav','footer','script','style']):noise.decompose()
    h1=soup.find('h1')
    if h1 is None or h1.get_text(' ',strip=True)!='Computer Science' or 'Yeshiva College' not in soup.get_text(' ',strip=True):
        raise ValueError('Wrong Yeshiva College department scope')
    rules=[]
    for profile in FAQ_PROFILES:
        headings=[h for h in soup.find_all('h2') if h.get_text(' ',strip=True)==profile['heading']]
        if len(headings)!=1 or policy_digest(headings[0].parent.get_text(' ',strip=True))!=profile['sha256']:
            raise ValueError('Changed department FAQ needs review')
        rules.append(policy_note(profile))
    return dict(id=PROGRAM_ID,requirements=rules)

SOURCE_PARSERS = {url:(lambda html,p=profile:parse_policy(html,p)) for url,profile in POLICY_PROFILES.items()}
SOURCE_PARSERS[DEPARTMENT]=parse_department_policies
SOURCES = SOURCES + tuple(POLICY_PROFILES) + (DEPARTMENT,)

COURSE_PROFILES=json.loads(Path(__file__).with_name('reviewed-courses.json').read_text())
CREDIT_PROFILE=json.loads(Path(__file__).with_name('reviewed-credit-policy.json').read_text())

def parse_course_metadata(html,profile):
    soup=BeautifulSoup(html,'html.parser')
    for noise in soup.find_all(['nav','footer','script','style']):noise.decompose()
    main=soup.find(id='main')
    if main is None or main.h1 is None or ' '.join(main.h1.get_text(' ',strip=True).split())!=profile['code']+' '+profile['name']:
        raise ValueError('Exact Yeshiva course code/title missing')
    descriptions=main.select('.desc');amounts=main.select('.sc_credits .credits')
    if len(descriptions)!=1 or len(amounts)!=1:
        raise ValueError('Ambiguous course description/credit structure')
    if any(n.get_text(' ',strip=True) for n in main.select('.sc_prereqs, .sc_coreqs')):
        raise ValueError('New separately structured requisites need review')
    residual=BeautifulSoup(str(main),'html.parser')
    for node in residual.select('h1, .desc, .sc_credits, .sc_prereqs, .sc_coreqs'):
        node.decompose()
    if residual.get_text(' ',strip=True):
        raise ValueError('New course restrictions or prose require review')
    text=' '.join(descriptions[0].get_text(' ',strip=True).split())
    parts=re.split(r'Prerequisites?\(s\):',text,maxsplit=1)
    if policy_digest(parts[0].strip())!=profile['description_sha256']:
        raise ValueError('Changed course narrative requires new summary review')
    requisites=parts[1].strip() if len(parts)==2 else None
    # A source page with no requisite statement remains unknown, not "none".
    # Preserve corequisite and prerequisite-or-corequisite alternatives in the text.
    credits=amounts[0].get_text(' ',strip=True)
    if not re.fullmatch(r'\d+(?:\.\d+)?',credits):
        raise ValueError('Unrecognized course credits')
    cid=PROGRAM_ID+'-'+profile['code'].lower().replace(' ','-')
    course=dict(id=cid,code=profile['code'],name=profile['name'],description=profile['description'],prerequisites=requisites,credits=float(credits),credit_unit='unknown',category='other',source_id=profile['source_id'],url=next((url for url,p in COURSE_PROFILES.items() if p['source_id']==profile['source_id']),None),public_site=None,syllabus=None)
    return dict(id=PROGRAM_ID,courses=[course])

def parse_credit_policy_pdf_text(text):
    if policy_digest(text)!=CREDIT_PROFILE['sha256']:
        raise ValueError('Changed institutional credit policy requires review')
    return dict(id=PROGRAM_ID,notes=[CREDIT_PROFILE['summary']])

CREDIT_POLICY_PDF_TEXT_PARSER=parse_credit_policy_pdf_text
SOURCE_PARSERS.update({url:(lambda html,p=profile:parse_course_metadata(html,p)) for url,profile in COURSE_PROFILES.items()})
SOURCES=SOURCES+tuple(COURSE_PROFILES)+('https://yu.smartcatalogiq.com/en/current/university-catalog/university-policies/undergraduate-policies/credit-hour-policy','https://www.yu.edu/provost/policies')
