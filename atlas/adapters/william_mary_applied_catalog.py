"""Observe the CourseLeaf major table; never merge the undated FAQ curriculum."""
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from atlas.adapters.national_curriculum_common import clean, content, course, rule

PROGRAM_ID = 'william-mary-applied-ai-ba'
CATALOG = 'https://catalog.wm.edu/programs/applied-artificial-intelligence-ba-interdisciplinary-studies-cdsp/index.html'
SID = PROGRAM_ID + '-catalog-2026-27'


def parse(html):
    root = content(html, 'Applied Artificial Intelligence (BA in Interdisciplinary Studies)')
    edition = re.search(r'(\d{4})[–-](\d{4}) Edition', clean(BeautifulSoup(html, 'html.parser').get_text(' ', strip=True)))
    if not edition or edition.groups() != ('2026', '2027'):
        raise ValueError('Catalog edition requires a new source review')
    scope = root.find(id='requirementstext') or root.find(id='requirementscontainer')
    if scope is None:
        raise ValueError('Catalog requirements tab missing')
    text = clean(scope.get_text(' ', strip=True))
    major = re.search(r'requires (\d+) credit hours to complete', text)
    degree = re.search(r'minimum of (\d+) credits are required', text)
    if not major or not degree or not re.search(r'Core Courses:', text):
        raise ValueError('Major/degree credit statements or core heading missing')
    tables = scope.find_all('table')
    if len(tables) != 1:
        raise ValueError('Expected one complete major table')
    parent = PROGRAM_ID + '-catalog-major'
    groups = [rule(parent, 'Applied AI major (2026–2027)', SID, credits=int(major[1]),
                   unit='semester_hours', summary='Published major total; core, capstone and elective rules below are parts of this total.'),
              rule(PROGRAM_ID + '-catalog-degree-total', 'Minimum credits for the BA degree', SID,
                   kind='note', credits=int(degree[1]), unit='semester_hours',
                   summary='Degree minimum, including the major and other degree requirements. Not an additional major credit requirement.')]
    courses = []
    section = 'core'
    last = None
    total = None
    electives = False
    for row in tables[0].find_all('tr'):
        cells = row.find_all(['td', 'th'], recursive=False)
        if not cells:
            continue
        rowtext = clean(row.get_text(' ', strip=True))
        if row.find('th') and rowtext == 'Code Title Hours':
            continue
        if rowtext.startswith('Total Hours'):
            total = int(clean(cells[-1].get_text()))
            continue
        if rowtext == 'Capstone:':
            section = 'capstone'
            last = None
            continue
        if rowtext == 'Electives:':
            section = 'electives'
            last = None
            continue
        if section == 'electives':
            if electives or len(cells) != 2 or 'Applied AI attribute' not in rowtext or 'consultation' not in rowtext or 'advisor' not in rowtext:
                raise ValueError('Unrecognized elective approval rule')
            credits = int(clean(cells[-1].get_text()))
            groups.append(rule(PROGRAM_ID + '-catalog-electives', 'Applied AI or advisor-approved electives', SID,
                               parent=parent, kind='choose_credits', credits=credits,
                               unit='semester_hours', summary=clean(cells[0].get_text(' ', strip=True))))
            electives = True
            continue
        links = [a for a in row.find_all('a') if re.fullmatch(r'[A-Z]+\s+\d{3}', clean(a.get_text()))]
        if len(links) != 1:
            raise ValueError('Unrecognized course or structural row: ' + rowtext)
        a = links[0]
        code = clean(a.get_text())
        is_or = bool(re.match(r'^or\b', rowtext))
        if is_or:
            if last is None:
                raise ValueError('Alternative has no preceding course')
            match = re.fullmatch(r'or\s+[A-Z]+\s+\d{3}\s*[-–]\s*(.+?)\s*\((\d+)\)', rowtext)
            if not match:
                raise ValueError('Unrecognized inline alternative')
            name, amount = match.groups()
            last.update(kind='choose_courses', count=1, credits=None,
                        title='Ethics course alternatives', summary='Choose one of the listed courses; their credit amounts differ.')
        else:
            if len(cells) != 3:
                raise ValueError('Course row must have code, title and hours')
            name = clean(cells[1].get_text(' ', strip=True))
            amount = clean(cells[2].get_text())
        if not re.fullmatch(r'\d+', amount):
            raise ValueError('Non-scalar course credits require review')
        c = course('wm-applied-ai', code, name, SID, urljoin(CATALOG, a.get('href', '')),
                   credits=int(amount), unit='semester_hours')
        if any(old['id'] == c['id'] for old in courses):
            raise ValueError('Duplicate course identity')
        courses.append(c)
        if is_or:
            last['course_ids'].append(c['id'])
        else:
            last = rule(PROGRAM_ID + '-catalog-' + code.lower().replace(' ', '-'),
                        ('Capstone: ' if section == 'capstone' else '') + name,
                        SID, [c['id']], parent=parent, credits=int(amount), unit='semester_hours')
            groups.append(last)
    if total != int(major[1]) or not electives or not any(g['title'].startswith('Capstone:') for g in groups):
        raise ValueError('Incomplete major table or inconsistent published total')
    return {'id': PROGRAM_ID, 'catalog_year': '2026-2027', 'courses': courses, 'requirements': groups}
