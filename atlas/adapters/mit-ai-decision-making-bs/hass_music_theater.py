"""Current Music/Theater concentration tabs; other credentials stay out of scope."""
from importlib import import_module
import re

from atlas.adapters.national_curriculum_common import clean, content, course, require_phrases, rule

optional = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_departments').optional
PID = 'mit-ai-decision-making-bs'
MUSIC = 'https://music.mit.edu/program/degree-requirements/'
THEATER = 'https://theater.mit.edu/program/degree-requirements/'


def concentration_tab(html, label):
    root = content(html, 'Degree Requirements')
    panes = []
    for pane in root.find_all('div', class_='b-tabs__entry-content'):
        first = pane.find('p')
        if first and clean(first.get_text(' ', strip=True)) == label:
            panes.append(pane)
    if len(panes) != 1:
        raise ValueError('Unique concentration tab missing: ' + label)
    return panes[0]


def parse_music(html):
    pane = concentration_tab(html, 'Music Concentration')
    require_phrases(pane, [
        'A Humanities concentration in music requires four subjects',
        'may start with one or more of our introductory subjects',
        'encouraged to begin at whatever level is appropriate to their experience',
        'two semesters of two different music ensembles',
        'three semesters of performance ensembles (two of one ensemble and one of a different ensemble)',
        'another half-term or six-unit subject from the curriculum',
        'Most 9- or 12-unit Music subjects', 'Distribution Component',
        'Two 6-unit performance subjects can also be combined',
        'following classes fulfill the Communication Requirement as CI-H subjects',
        'also fulfills both a music concentration and CI-H requirement',
        'schedule a meeting before filling out your concentration proposal',
    ])
    sid, prefix = PID + '-hass-music-current', 'mit-ai-hass-music'
    lists = pane.find_all('ul')
    if len(lists) != 2:
        raise ValueError('Music introductory/CI-H lists changed structure')
    courses, intro, ci = {}, [], []
    for index, ul in enumerate(lists):
        for li in ul.find_all('li', recursive=False):
            match = re.fullmatch(r'(21M\.[A-Z0-9]+):\s*(.+?)(?:\s*\(HASS Arts\))?(?:\s*\(CI-H\))?', clean(li.get_text(' ', strip=True)))
            if not match:
                raise ValueError('Music named-subject row changed')
            c = course(prefix, match[1], match[2], sid, MUSIC, unit='units', category='human_context')
            if c['id'] in courses and courses[c['id']]['name'] != c['name']:
                raise ValueError('Conflicting Music subject names')
            courses[c['id']] = c
            (intro if index == 0 else ci).append(c['id'])
    if not intro or not ci:
        raise ValueError('Music subject lists empty')
    match = re.search(r'The seminar joint listed with Music, (21M\.[A-Z0-9]+), also fulfills', clean(pane.get_text(' ', strip=True)))
    if not match:
        raise ValueError('Music joint seminar evidence missing')
    seminar = course(prefix, match[1], None, sid, MUSIC, unit='units', category='human_context')
    courses[seminar['id']] = seminar
    return dict(id=PID, courses=list(courses.values()), requirements=[
        optional(prefix, 'Music', sid),
        rule(prefix + '-four', 'Four-subject Music concentration', sid, parent=prefix, kind='choose_courses', count=4,
             summary='Select four Music subjects with the concentration advisor. Meet the surname-assigned advisor before submitting the proposal. The introductory suggestions are not a closed concentration pool or a mandatory introductory sequence; experienced students may begin at an appropriate level.'),
        rule(prefix + '-introductory', 'Suggested Music introductions', sid, intro, parent=prefix, kind='note',
             summary='Students with little or no previous music experience may start with one or more listed introductions. These examples do not impose an introductory-subject minimum.'),
        rule(prefix + '-performance', 'Optional ensemble combinations', sid, parent=prefix, kind='note',
             summary='The concentration section permits performance study described as two semesters of two different ensembles. For three semesters (two of one ensemble and one of another), the odd term may pair with another half-term or six-unit curriculum subject. Preserve the stated combination criteria; do not treat every six-unit performance enrollment as a full concentration subject or infer an additional mandatory ensemble load.'),
        rule(prefix + '-hass-ci', 'Music HASS Arts and CI-H context', sid, ci + [seminar['id']], parent=prefix, kind='note',
             summary='Most 9/12-unit Music subjects can meet HASS Arts Distribution; two six-unit performance subjects may combine for HASS Arts. The listed introductory CI-H subjects and the joint-listed seminar can meet communication requirements; the seminar also qualifies for the concentration. Its title is not stated on this page. These designations do not waive registrar concentration overlap or approval rules.'),
    ])


def parse_theater(html):
    pane = concentration_tab(html, 'The Concentration in Theater Arts')
    require_phrases(pane, [
        'three to four 9-to-12-unit courses', 'minimum of 36 credits in the Theater Arts curriculum',
        'Up to nine units of theater practicum (acting, directing, or design)',
        'in Theater Arts productions can be counted toward the concentration',
        'current Concentration Advisor',
    ])
    sid, prefix = PID + '-hass-theater-current', 'mit-ai-hass-theater'
    return dict(id=PID, requirements=[
        optional(prefix, 'Theater Arts', sid),
        rule(prefix + '-selection', 'Theater Arts three-to-four-course plan and stated minimum', sid,
             parent=prefix, kind='note', credits=36,
             summary='Complete three to four 9–12-unit courses in the Theater Arts curriculum, with the concentration advisor and general HASS approval rules. The page states a minimum of 36 credits; this source-stated amount remains in unknown normalized units rather than assuming a credits-to-units conversion. Course count is a range, not exactly three or exactly four. This is an open departmental curriculum criterion, not a fabricated closed course pool.'),
        rule(prefix + '-practicum', 'Theater production practicum limit', sid, parent=prefix, kind='note',
             summary='Up to nine units of acting, directing or design practicum in Theater Arts productions may count toward this concentration. This is a permitted contribution within the plan, not an additional nine-unit requirement. The major’s CI-M/thesis structure and the minor’s separate curriculum are not concentration obligations.'),
    ])


SOURCE_PARSERS = {MUSIC: parse_music, THEATER: parse_theater}
