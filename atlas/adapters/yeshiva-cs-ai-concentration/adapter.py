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
