"""Observe the edition-specific BA catalog without importing BS or sample-plan rules."""
import hashlib
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

PROGRAM_ID = 'purdue-ai-ba'
URL = 'https://catalog.purdue.edu/preview_program.php?catoid=19&poid=35726'
SOURCE_ID = 'purdue-ai-ba-catalog-2026'
CONTENT = json.loads(Path(__file__).with_suffix('.json').read_text())


def text(node):
    return ' '.join(node.get_text(' ', strip=True).split())


def section(soup, prefix):
    matches = [d for d in soup.select('div.acalog-core')
               if (h := d.find(['h2', 'h3', 'h4'], recursive=False))
               and text(h).startswith(prefix)]
    if len(matches) != 1:
        raise ValueError('Missing or duplicate Purdue BA section: ' + prefix)
    return matches[0]


def course_rows(node):
    rows = []
    for li in node.select('li.acalog-course'):
        a = li.find('a')
        match = re.fullmatch(r'([A-Z]+ \d{5})\s*-\s*(.+)', text(a)) if a else None
        if not match:
            raise ValueError('Unrecognized Purdue BA course row')
        code, name = match.groups()
        coid = re.search(r"(?:show|hide)CatalogData\('19', '3', '(\d+)'", a.get('onclick', '')) or re.search(
            r"showCourse\('19', '(\d+)'", a.get('onclick', ''))
        credit = re.search(r'Credit Hours:\s*(\d+\.\d+)(?:\s+to\s+(\d+\.\d+))?', text(li))
        if not coid or not credit:
            raise ValueError('Purdue BA course identity or credits missing: ' + code)
        detail = li.select_one('.coursepadding h3')
        description = None
        if detail:
            body = text(detail.parent)
            spec = CONTENT.get(code)
            if not spec or hashlib.sha256(body.encode()).hexdigest() != spec['content_hash']:
                raise ValueError('Purdue BA course content changed; manual review required: ' + code)
            description = spec['description']
        rows.append(dict(id='purdue-' + code.lower().replace(' ', '-'), code=code, name=name,
                         description=description, prerequisites=None,
                         credits=None if credit[2] else float(credit[1]),
                         credit_unit='semester_hours', category='other', source_id=SOURCE_ID,
                         url=f'https://catalog.purdue.edu/preview_course.php?catoid=19&coid={coid[1]}',
                         public_site=None, syllabus=None))
    if len({c['id'] for c in rows}) != len(rows):
        raise ValueError('Duplicate Purdue BA course identity')
    return rows


def requirement(suffix, title, kind='all', *, parent=None, courses=(), credits=None,
                count=None, summary='', category='other'):
    return dict(id=PROGRAM_ID + '-' + suffix, parent_id=PROGRAM_ID + '-' + parent if parent else None,
                title=title, kind=kind, count=count, credits=credits, credit_unit='semester_hours',
                category=category, source_id=SOURCE_ID, source_text=None, summary=summary,
                course_ids=[c['id'] for c in courses])


def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    if not any(text(h) == 'Artificial Intelligence, BA' for h in soup.find_all('h1')):
        raise ValueError('Purdue BA catalog award heading missing')
    if '2026-2027 University Catalog' not in text(soup):
        raise ValueError('Purdue BA catalog edition changed')
    degree = section(soup, 'Degree Requirements')
    if '120 Credits Required' not in text(degree):
        raise ValueError('Purdue BA degree credit total changed')
    major = section(soup, 'Departmental/Program Major Course Requirements')
    if '(51-53 credits)' not in text(major):
        raise ValueError('Purdue BA major credit range changed')
    courses, requirements = [], [requirement('major', 'Departmental/Program Major Course Requirements (51–53 credits)',
                                              summary='Complete Areas A–E. Major courses cannot double count within the major; the calculus route determines the published credit range.')]
    areas = [('area-a', 'Area A:', 'all', 16), ('area-b', 'Area B:', 'all', None),
             ('area-c-ethics', 'Ethics/ Value Theory', 'choose_credits', 3),
             ('area-c-history', 'History of Philosophy', 'choose_credits', 3),
             ('area-c-science', 'Philosophy of Science, Tech, and Mathematics', 'choose_credits', 3),
             ('area-d', 'Area D:', 'choose_credits', 3), ('area-e', 'Area E:', 'all', 3)]
    requirements.append(requirement('area-c', 'Area C: Additional Philosophy Course Requirements (9 credits)',
                                    parent='major', credits=9, summary='Complete 3 credits in each of the three listed subject areas.'))
    observed = {}
    for suffix, prefix, kind, credits in areas:
        node = section(soup, prefix)
        rows = course_rows(node)
        if suffix in CONTENT['_inventory'] and [c['code'] for c in rows] != CONTENT['_inventory'][suffix]:
            raise ValueError('Purdue BA choice inventory changed; manual review required: ' + prefix)
        observed[suffix] = rows
        courses.extend(rows)
        heading = text(node.find(['h2', 'h3', 'h4'], recursive=False))
        if suffix == 'area-b':
            expected = ['CS 17600', 'CS 18000', 'CS 18200', 'CS 24300', 'CS 36100',
                        'MA 16010', 'MA 16020', 'MA 16100', 'MA 16500']
            if [c['code'] for c in rows] != expected:
                raise ValueError('Purdue BA computing/calculus inventory changed')
            clean = BeautifulSoup(str(node), 'html.parser')
            for table in clean.select('table'):
                table.decompose()
            rule = text(clean)
            if not re.search(r'MA 16010.*\band\b.*MA 16020.*\bOR\b.*MA 16100.*\bOR\b.*MA 16500', rule):
                raise ValueError('Purdue BA calculus AND/OR structure changed')
            requirements.append(requirement(suffix, heading, parent='major', summary='Five fixed CS courses plus one calculus route; published total 20–22 credits.'))
            requirements.append(requirement('cs', 'Required computer science courses', parent=suffix,
                                            courses=rows[:5], credits=16))
            requirements.append(requirement('calculus', 'Calculus alternatives', 'alternative', parent=suffix,
                                            count=1, category='mathematics', summary='MA 16010 AND MA 16020, OR MA 16100, OR MA 16500. These are three routes, not four fixed math courses.'))
            for route, selected, load in [('applied', rows[5:7], 6), ('16100', rows[7:8], 5), ('16500', rows[8:9], 4)]:
                requirements.append(requirement('calculus-' + route, ' + '.join(c['code'] for c in selected),
                                                parent='calculus', courses=selected, credits=load, category='mathematics'))
        else:
            if not rows:
                raise ValueError('Empty Purdue BA course pool: ' + prefix)
            if f'({credits} credits)' not in heading:
                raise ValueError('Purdue BA section credit rule changed: ' + prefix)
            requirements.append(requirement(suffix, heading, kind, parent='area-c' if suffix.startswith('area-c-') else 'major',
                                            courses=rows, credits=credits,
                                            summary='Complete the stated credit load from this pool.' if kind == 'choose_credits' else
                                            'Complete the listed courses.' if suffix != 'area-e' else
                                            'Complete 3 credits of PHIL 41500; the course itself permits 1–3 credits per enrollment.'))
    if [c['code'] for c in observed['area-a']] != ['PHIL 25601', 'PHIL 30000', 'PHIL 31400', 'PHIL 32300', 'PHIL 41400'] or [c['code'] for c in observed['area-e']] != ['PHIL 41500']:
        raise ValueError('Purdue BA fixed philosophy inventory changed')
    if len({c['id'] for c in courses}) != len(courses):
        raise ValueError('Duplicate Purdue BA major identity across areas')
    policy_sections = [('area-c-d-level', 'Note for Areas C & D', 'major'),
                       ('cla-core', 'Other Departmental - Liberal Arts Core', None),
                       ('cla-disciplines', 'Core I: Disciplinary Diversity', 'cla-core'),
                       ('cla-social', 'Core II: Social Diversity', 'cla-core'),
                       ('cla-language', 'Core III: Linguistic Diversity', 'cla-core'),
                       ('cla-foundational', 'Foundational Requirements', 'cla-core'),
                       ('cla-overlap-exemptions', 'Notes', 'cla-core'),
                       ('electives', 'Electives (', None), ('gpa', 'GPA Requirements', None),
                       ('major-notes', 'Course Requirements and Notes', 'major'),
                       ('pass-no-pass', 'College of Liberal Arts Pass/No Pass Option Policy', None),
                       ('university-core', 'University Core Requirements', None),
                       ('civics', 'Civics Literacy Proficiency Requirement', None),
                       ('residence', 'Upper Level Requirement', None),
                       ('prerequisite-information', 'Pre-Requisite Information', None),
                       ('world-language-notes', 'World Language Courses', 'cla-core')]
    for suffix, prefix, parent in policy_sections:
        node = section(soup, prefix)
        # Full policy text is checked against an individually reviewed digest. Only
        # original concise summaries are published; changed wording needs review.
        spec = CONTENT['_policies'][suffix]
        if hashlib.sha256(text(node).encode()).hexdigest() != spec['content_hash']:
            raise ValueError('Purdue BA policy changed; manual review required: ' + prefix)
        requirements.append(requirement(suffix, text(node.find(['h2', 'h3', 'h4'], recursive=False)),
                                        'note', parent=parent, summary=spec['summary']))
    outcome_node = section(soup, 'Program Learning Outcomes')
    if hashlib.sha256(text(outcome_node).encode()).hexdigest() != CONTENT['_outcome_hash']:
        raise ValueError('Purdue BA learning outcomes changed; manual review required')
    return dict(id=PROGRAM_ID, title='Artificial Intelligence', award_level='BA', program_kind='degree',
                hosting_unit='Department of Philosophy, College of Liberal Arts', catalog_year='2026–2027',
                curriculum_status='partial', courses=courses, requirements=requirements,
                outcomes=CONTENT['_outcomes'])
