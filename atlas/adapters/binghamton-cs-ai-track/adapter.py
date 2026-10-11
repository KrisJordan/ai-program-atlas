"""Observe Binghamton's public track page, including its HTML course widgets."""
import re
from bs4 import BeautifulSoup
PROGRAM_ID = 'binghamton-cs-ai-track'
SOURCE_ID = PROGRAM_ID + '-department'
SOURCES = ('https://www.binghamton.edu/computer-science/undergraduate-programs/bs-aitrack.html',)

def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    heading = soup.find('h1')
    if not heading or heading.get_text(' ', strip=True) != 'BSCS with Artificial Intelligence Track':
        raise ValueError('Track identity missing or changed')
    body = soup.find(id='content1')
    if body is None:
        raise ValueError('Track content missing')
    text = ' '.join(body.get_text(' ', strip=True).split())
    if not re.search(r'four of the BSCS electives.*two are required, and two are electives', text):
        raise ValueError('Four-course/two-plus-two rule changed')
    pools = {}
    for title in ['Required courses', 'Electives']:
        h = body.find('h3', string=lambda s: s and s.strip() == title)
        if h is None:
            raise ValueError('Track group missing')
        parts = []
        for node in h.next_siblings:
            if getattr(node, 'name', None) == 'h3':
                break
            parts.append(str(node))
        section = BeautifulSoup(''.join(parts), 'html.parser')
        rows = {}
        for widget in section.find_all(attrs={'data-acalog-course-code': True}):
            prefix, number = widget.get('data-acalog-course-prefix'), widget['data-acalog-course-code']
            if prefix != 'CS' or not re.fullmatch(r'\d{3}[A-Z]?', number):
                raise ValueError('Unexpected public course widget')
            rows['CS '+number] = None
        for number, name in re.findall(r'CS\s+(\d{3}[A-Z]?)\s*-\s*([^\n]+)', section.get_text('\n', strip=True)):
            rows['CS '+number] = name.strip()
        if not rows:
            raise ValueError('Empty track pool; do not erase reviewed courses')
        pools[title] = rows
    if len(pools['Required courses']) != 2:
        raise ValueError('Required-course count no longer matches rule')
    courses, requirements = [], []
    for title, rows in pools.items():
        ids = []
        for code, name in rows.items():
            cid = PROGRAM_ID+'-'+code.lower().replace(' ', '-')
            ids.append(cid)
            courses.append(dict(id=cid,code=code,name=name,description=None,prerequisites=None,
                                credits=None,credit_unit='unknown',category='ai_ml',source_id=SOURCE_ID,
                                url=SOURCES[0],public_site=None,syllabus=None))
        required = title == 'Required courses'
        requirements.append(dict(id=PROGRAM_ID+('-core' if required else '-electives'),parent_id=None,
            title=title,kind='all' if required else 'choose_courses',count=None if required else 2,
            credits=None,credit_unit='unknown',category='ai_ml',source_id=SOURCE_ID,source_text=None,
            summary='Complete both named core courses.' if required else 'Choose two track electives from the department page; see the separately reviewed degree-guide conflict.',course_ids=ids))
    return dict(id=PROGRAM_ID,title='BSCS with Artificial Intelligence Track',award_level='concentration',
                program_kind='concentration',curriculum_status='partial',courses=courses,requirements=requirements)
