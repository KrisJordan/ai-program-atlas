"""Observed program identities and bounded course inventories, never seed replay."""
import re
from fractions import Fraction
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, requirement, text


def parse_wpi(html, pid, expected_title, url):
    s = BeautifulSoup(html, 'html.parser')
    root = s.find('article', class_='node--type-degree')
    if root is None or text(root.find('h1')) != expected_title:
        raise ValueError('WPI concentration heading missing')
    kind = root.select_one('.field--name-field-degree-type .field__item')
    parent = root.select_one('.concentration-usage')
    if kind is None or text(kind) != 'Concentration' or parent is None or text(parent) != 'Artificial Intelligence Major':
        raise ValueError('WPI concentration/parent relationship missing')
    courses = {}
    for row in root.select('article.node--type-class'):
        code, name = row.select_one('.col-3 a'), row.select_one('.col-7')
        if code is None or name is None:
            raise ValueError('WPI course row changed')
        amount = row.select_one('.field--name-field-credits')
        raw = text(amount) if amount else ''
        credits = float(Fraction(raw)) if re.fullmatch(r'\d+(?:/\d+)?', raw) else None
        c = course(text(code), text(name), pid+'-catalog', urljoin(url, code['href']),
                   institution='wpi', unit='units', credits=credits, category='applications')
        courses[c['id']] = c
    if not courses:
        raise ValueError('No concentration course rows')
    return dict(id=pid, title=expected_title, award_level='concentration', program_kind='concentration',
                curriculum_status='partial', courses=list(courses.values()), requirements=[requirement(
                    pid, 'observed-options', 'Observed local concentration course inventory', pid+'-catalog',
                    kind='note', unit='units', category='applications', course_ids=list(courses),
                    summary='Course rows observed in this named concentration catalog. This inventory is not an all-required list. Selection minima, nested alternatives, open pools and policy conditions require the separate reviewed notes; parent BS requirements are outside this local inventory.')])


def parse_psu(html, pid, expected_title, plan):
    s = BeautifulSoup(html, 'html.parser')
    h = s.find('h1')
    root = s.find(id='programrequirementstextcontainer')
    if h is None or text(h) != expected_title or root is None:
        raise ValueError('Penn State degree heading/requirements missing')
    if 'Plan Code: '+plan not in text(s) or 'University Park' not in text(s):
        raise ValueError('Penn State plan/campus evidence missing')
    v = text(root)
    m = re.search(r'For the Bachelor of Science degree in (.+?), a minimum of (\d+) credits is required', v)
    if not m or not expected_title.startswith(m[1]+', B.S.'):
        raise ValueError('Explicit BS minimum-credit statement missing')
    return dict(id=pid, title=expected_title, award_level='BS', program_kind='degree',
                curriculum_status='partial', requirements=[requirement(pid, 'degree-minimum',
                    'Published degree credit minimum', pid+'-catalog', kind='note', unit='semester_hours',
                    credits=int(m[2]), category='other', summary='Published Bachelor of Science minimum: '+m[2]+
                    ' credits. This degreewide total is not a sum of the currently extracted course inventory. Detailed major alternatives, general education, overlap and university rules still need structured review.')])


def parse_delaware(html):
    s = BeautifulSoup(html, 'html.parser')
    for node in s.find_all(['nav', 'footer', 'script', 'style']):
        node.decompose()
    heading = 'BS Computer Science with Concentration in Artificial Intelligence and Robotics'
    if not any(text(h) == heading for h in s.find_all('h4')):
        raise ValueError('Delaware AI/Robotics concentration heading missing')
    if not any('official University credential' in text(p) and 'student transcript' in text(p) for p in s.find_all('p')):
        raise ValueError('Formal concentration statement missing')
    return dict(id='delaware-cs-ai-robotics-concentration', title=heading,
                award_level='concentration', program_kind='concentration')


def parse_rit_immersion(html):
    s = BeautifulSoup(html, 'html.parser')
    for node in s.find_all(['nav', 'footer', 'script', 'style']):
        node.decompose()
    if not any(text(h) == 'AI in Society Immersion' for h in s.find_all('h1')):
        raise ValueError('RIT immersion heading missing')
    if not any('The plan code for AI in Society Immersion is AISTS-IM.' in text(p) for p in s.find_all('p')):
        raise ValueError('RIT formal immersion plan code missing')
    return dict(id='rit-ai-society-immersion', title='AI in Society Immersion',
                award_level='concentration', program_kind='concentration')
