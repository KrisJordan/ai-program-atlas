"""Observe current, source-bound statistics cards without replaying manual reviews."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course
from atlas.adapters.rit_immersion_rule_observer import parse as observe_rules
from atlas.adapters.rit_writing_closure import PID

URL = 'https://www.rit.edu/study/applied-statistics-immersion'
SID = 'rit-applied-statistics-course-cards-2026-2027'
TITLE = 'Applied Statistics Immersion'


def parse(html):
    observation = observe_rules(html, title=TITLE)
    bound = {c for t in observation['observed_tables'] for r in t['rows'] for c in r['course_codes']}
    soup = BeautifulSoup(html, 'html.parser')
    courses = []
    for card in soup.select('.courseblock'):
        def value(selector):
            node = card.select_one(selector)
            return clean(node.get_text(' ', strip=True)) if node else None
        code, name = value('.detail-code'), value('.detail-title')
        if not code or code not in bound or not re.fullmatch(r'STAT-\d{3}', code) or not name:
            raise ValueError('Unbound statistics course card')
        amount = value('.detail-hours_html') or ''
        m = re.fullmatch(r'\((\d+(?:\.\d+)?) Credits?\)', amount)
        if not m:
            raise ValueError('Unknown statistics credit format')
        description = value('.courseblockextra')
        if not description:
            raise ValueError('Settled course description required')
        item = course(PID, code, name, SID, URL, float(m[1]))
        item.update(description=description, prerequisites=value('.detail-requisites'))
        courses.append(item)
    if not courses:
        raise ValueError('No rendered statistics cards')
    if len({c['id'] for c in courses}) != len(courses):
        raise ValueError('Duplicate statistics cards')
    return {'id':PID,'courses':courses,'requirements':[],
            'observed_immersion_tables':observation['observed_tables']}


def register(sources, parsers):
    if URL not in sources:
        sources.append(URL)
    parsers[URL] = parse
