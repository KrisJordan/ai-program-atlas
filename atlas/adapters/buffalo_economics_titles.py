"""Observe binding uncoded Economics course titles; never invent catalog codes."""
import re
from bs4 import BeautifulSoup

PROGRAM_ID = 'university-at-buffalo-suny-ai-and-quantitative-economics-bs-degree'
URL = 'https://arts-sciences.buffalo.edu/economics/undergraduate/bs-ai-and-quantitative-economics.html'
SOURCE_ID = PROGRAM_ID + '-department-required-titles'
# Reviewed exact membership guards. A changed title/menu/quantity requires review;
# parser observations carry no independent audit or category review.
COMPONENTS = [
    ('Math Core', 8, ['Precalculus'], ('Choose one of the following Math Electives below:', 1, ['Survey of Calculus and Its Applications I', 'Mathematical Analysis for Management', 'College Calculus I'])),
    ('AI & Society Core', 15, ['AI & Society', 'AI & Ethics', 'Technological Disruption and Diffusion'], ('Choose two of the following AI & Society Electives below:', 2, ['AI & Policy', 'AI and Social Structures', 'AI & The Information Environment'])),
    ('AI & Technology Core', 16, ['Applied Linear Algebra and Probability for AI', 'Applied Machine Learning', 'Introduction to Computer Science I', 'Introduction to Computer Science II'], None),
    ('Bridge Courses', 6, ['Artificial Intelligence and Economic Policy', 'Big Data and Application of Machine Learning in Economics'], None),
    ('AI in Quantitative Economics Core', 38, ['Introduction to Macroeconomics', 'Introduction to Microeconomics', 'Economic Statistics and Data Analysis', 'Microeconomic Theory 1', 'Macroeconomic Theory', 'Time Series Analysis and Forecasting', 'Econometrics I', 'Econometrics II'], ('Choose four of the following ECO Advanced Electives below:', 4, ['Health Economics', 'Environmental Economics', 'Economic Development', 'Urban Economics', 'Financial Economics', 'International Finance', 'Economics of Education', 'Labor Economics', 'Public Economics', 'Industrial Organization'])),
    ('AI & Society Capstone', 3, ['AI and Society Capstone'], None),
]


def text(node):
    return ' '.join(node.get_text(' ', strip=True).split())


def slug(value):
    return re.sub('[^a-z0-9]+', '-', value.lower()).strip('-')


def title_id(value):
    return 'buffalo-ai-qe-title-' + slug(value)


def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    if not soup.title or not text(soup.title).startswith('BS in AI and Quantitative Economics'):
        raise ValueError('Expected Economics department AI BS identity')
    heading = soup.find(lambda n: n.name == 'h2' and text(n) == 'Required Courses')
    if heading is None:
        raise ValueError('Expected binding Required Courses heading')
    observed = []
    for node in heading.find_all_next():
        if node.name == 'h2':
            break
        if node.name in ('h3', 'p', 'ul'):
            observed.append((node.name, [text(li) for li in node.find_all('li', recursive=False)] if node.name == 'ul' else text(node)))
    expected = []
    for label, credits, fixed, choice in COMPONENTS:
        expected.extend([('h3', f'{label} ({credits} credits)'), ('ul', fixed)])
        if choice:
            expected.extend([('p', choice[0]), ('ul', choice[2])])
    if observed != expected:
        raise ValueError('Economics title membership, credit amount or choice rule changed; review required')
    courses, requirements = [], []
    for label, credits, fixed, choice in COMPONENTS:
        rid = PROGRAM_ID + '-department-' + slug(label)
        requirements.append({'id': rid, 'parent_id': None, 'title': label, 'kind': 'all', 'count': None, 'credits': credits, 'credit_unit': 'unknown', 'category': 'other', 'source_id': SOURCE_ID, 'source_text': None, 'summary': 'Department Required Courses title inventory; codes and catalog/cohort applicability remain unknown. Component credits are source-stated, not normalized semester hours.', 'course_ids': [title_id(t) for t in fixed]})
        if choice:
            requirements.append({'id': rid + '-choices', 'parent_id': rid, 'title': choice[0], 'kind': 'choose_courses', 'count': choice[1], 'credits': None, 'credit_unit': 'unknown', 'category': 'other', 'source_id': SOURCE_ID, 'source_text': choice[0], 'summary': 'Exact named department title pool. Missing codes are not inferred from another major or catalog snippet.', 'course_ids': [title_id(t) for t in choice[2]]})
        for title in fixed + (choice[2] if choice else []):
            courses.append({'id': title_id(title), 'code': None, 'name': title, 'description': None, 'prerequisites': None, 'credits': None, 'credit_unit': 'unknown', 'category': 'other', 'source_id': SOURCE_ID, 'url': URL, 'public_site': None, 'syllabus': None, 'notes': ['Official department binding title only; exact catalog course code and edition are unverified. No cross-list/title alias equivalence is assumed.']})
    return {'id': PROGRAM_ID, 'courses': courses, 'requirements': requirements, 'curriculum_status': 'partial'}
