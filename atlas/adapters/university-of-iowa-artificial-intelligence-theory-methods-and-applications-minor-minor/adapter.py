"""Observe Iowa's local AI minor rules; review, never parsing, certifies completeness."""
import hashlib
import re

from bs4 import BeautifulSoup

PROGRAM_ID = 'university-of-iowa-artificial-intelligence-theory-methods-and-applications-minor-minor'
SOURCES = ('https://catalog.registrar.uiowa.edu/engineering/electrical-computer-engineering/artificial-intelligence-theory-methods-applications-minor/',)
SOURCE_ID = 'iowa-ai-minor-catalog'


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('h1', class_='page-title')
    if title is None or 'Artificial Intelligence: Theory, Methods, and Applications' not in title.get_text():
        raise ValueError('Iowa AI minor heading missing')
    text = soup.get_text(' ', strip=True).replace('\xa0', ' ')
    def number(pattern):
        match = re.search(pattern, text, re.I)
        if not match:
            raise ValueError('Required Iowa policy missing: ' + pattern)
        return float(match[1])
    total = number(r'applications requires (\d+) s\.h\.')
    elective_credits = number(r'complete at least (\d+) s\.h\. in elective')
    gpa = number(r'grade-point average of at least ([\d.]+)')
    transfer = number(r'maximum of (\d+) s\.h\. of transfer')
    for required in ['pass/nonpass', 'undergraduate degree-seeking', 'at least two of the three categories', 'numbered 5000', 'major that does not require a computer programming course', 'major that does not require a matrix algebra course', 'major that does not require a probability course', 'maximum of one AI-related course', 'AI ethics']:
        if required not in text:
            raise ValueError('Required Iowa rule needs review: ' + required)
    courses, groups = {}, {}
    categories = {'Required Course': 'ai_ml', 'Theory': 'mathematics', 'Methods': 'ai_ml', 'Applications': 'applications', 'Support': 'systems'}
    def cid(code):
        return 'iowa-' + code.lower().replace(':', '-')
    def add(code, name, credits, category):
        key = cid(code)
        if key not in courses:
            courses[key] = dict(id=key, code=code, name=name, description=None, prerequisites=None, credits=credits, credit_unit='semester_hours', category=category, source_id=SOURCE_ID, url=SOURCES[0], public_site=None, syllabus=None)
        return key
    for table in soup.find_all('table', class_='sc_courselist'):
        heading = table.find_previous(['h2', 'h3'])
        section = heading.get_text(' ', strip=True) if heading else ''
        if section not in categories:
            continue
        members = []
        for row in table.find_all('tr'):
            cells = row.find_all('td', recursive=False)
            if len(cells) < 3:
                continue
            code = re.search(r'[A-Z]+:\d{4}', cells[0].get_text(' ', strip=True))
            if not code:
                continue
            credit = cells[-1].get_text(' ', strip=True)
            members.append(add(code[0], cells[1].get_text(' ', strip=True), float(credit) if re.fullmatch(r'\d+(?:\.\d+)?', credit) else None, categories[section]))
        groups[section] = list(dict.fromkeys(members))
    if set(groups) != set(categories) or not all(groups.values()):
        raise ValueError('A required Iowa course table is missing or empty')
    for span in soup.find_all('span', class_='sc_courseinline'):
        anchor = span.find('a')
        if anchor is None:
            continue
        code = anchor.get_text(' ', strip=True)
        if not re.fullmatch(r'[A-Z]+:\d{4}', code):
            continue
        name = span.get_text(' ', strip=True)[len(code):].strip()
        add(code, name or None, None, 'foundations' if code == 'ENGR:1300' else 'mathematics')
    req = []
    def node(id, parent, title, kind='note', ids=(), credits=None, summary=''):
        req.append(dict(id='iowa-' + id, parent_id='iowa-' + parent if parent else None, title=title, kind=kind, count=None, credits=credits, credit_unit='semester_hours', category='other', source_id=SOURCE_ID, source_text=None, summary=summary, course_ids=list(ids)))
    node('minor', None, 'AI minor: local requirements', 'all', credits=total, summary=f'Complete {total:g} semester hours under the required-course and elective rules. This is the minor, not the parent degree.')
    node('required', 'minor', 'Required course or permitted substitution', 'alternative', summary='Take ENGR:3110, or substitute an ECE 5000–5999 course appearing in the theory, methods, or applications lists.')
    node('intro', 'required', 'Introduction to AI', 'all', groups['Required Course'])
    substitutions = [c for section in ('Theory', 'Methods', 'Applications') for c in groups[section] if 5000 <= int(courses[c]['code'].split(':')[1]) <= 5999]
    node('substitution', 'required', 'Listed upper-level ECE substitution', ids=substitutions, summary='One listed ECE 5000–5999 course may replace the introductory requirement; this is an alternative, not an additional compulsory pool.')
    node('electives', 'minor', 'Elective selection', 'choose_credits', credits=elective_credits, summary=f'Choose at least {elective_credits:g} semester hours spanning at least two of theory, methods, and applications. At most one support-category elective may count.')
    for section in ('Theory', 'Methods', 'Applications', 'Support'):
        node(section.lower(), 'electives', section + ' options', ids=groups[section], summary='Listed eligible options; apply the overall elective/category rules.' if section != 'Support' else 'At most one support elective. These courses are options, not all required.')
    node('approvals', 'electives', 'Non-ECE options and ethics approval', summary='With ECE Undergraduate Committee approval, at most one AI-related non-ECE course may count in methods/applications, and at most one in support. An approved AI-ethics course may count as support.')
    conditions = [
        ('programming', ['ENGR:1300'], 'If the student’s major does not require programming, ENGR:1300 may count as a minor elective.'),
        ('algebra', ['MATH:2550', 'MATH:2700'], 'If the major does not require matrix algebra, either listed algebra course may be the support course.'),
        ('probability', ['ECE:3995', 'STAT:2020', 'STAT:3120'], 'If the major does not require probability, one listed course may be the support course. ECE:3995 qualifies only for the introduction-to-probability-and-statistics topic.'),
    ]
    for key, codes, summary in conditions:
        if any(cid(code) not in courses for code in codes):
            raise ValueError('Conditional course missing: ' + key)
        node('conditional-' + key, 'electives', 'Conditional ' + key + ' option', ids=[cid(code) for code in codes], summary=summary)
    node('eligibility', 'minor', 'Eligibility and enrollment preparation', summary='Available to Iowa undergraduate degree-seeking students. Course prerequisites may be additional work that does not count toward the minor. Declare and request a minor audit through MyUI.')
    node('academic-policy', 'minor', 'Grades, grading mode, and transfer', summary=f'Minor work requires a GPA of at least {gpa:.2f}; pass/nonpass work is not allowed. At most {transfer:g} transfer semester hours may count with ECE Undergraduate Committee approval.')
    edition = re.search(r'(20\d{2})[–-](20\d{2}) Edition', text)
    return dict(id=PROGRAM_ID, title='Artificial Intelligence: Theory, Methods, and Applications', program_kind='minor', award_level='minor', curriculum_status='partial', catalog_year='-'.join(edition.groups()) if edition else None, courses=list(courses.values()), requirements=req, observed_policy_digest=hashlib.sha256(text.encode()).hexdigest())
