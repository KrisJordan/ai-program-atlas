"""Reviewed CS 1800 concurrency only; no general prerequisite expansion.

The degree observation verifies the degree's explicit corequisite direction and
fixed CS 1800 ancestry. A separate live CS observation supplies the reciprocal
corequisite evidence and CS 1802 course facts. Its child rule inherits CS 1800's
parent context rather than creating a top-level obligation.
"""
from bs4 import BeautifulSoup
from atlas.adapters.northeastern_courseleaf import clean
from atlas.adapters.northeastern_course_metadata import parse_subject

URL = 'https://catalog.northeastern.edu/course-descriptions/cs/'


def guard_degree(parse, program_id):
    def observe(html):
        result = parse(html)
        panel = BeautifulSoup(html, 'html.parser').find(id='programrequirementstextcontainer')
        policy = 'Also complete any corequisite labs, recitations, clinicals, or tools courses where specified'
        if panel is None or policy not in clean(panel):
            raise ValueError('Degree corequisite applicability changed')
        groups = {r['id']:r for r in result['requirements']}
        gid = program_id+'-req-cs-1800'
        node = groups.get(gid)
        if not node or node['course_ids'] != [program_id+'-cs-1800']:
            raise ValueError('CS 1800 requirement identity changed')
        while node:
            if node['kind'] != 'all':
                raise ValueError('CS 1800 conditional ancestry requires new review')
            node = groups.get(node['parent_id']) if node.get('parent_id') else None
        return result
    return observe


def observe_cs1802(html, program_id, existing_parser):
    result = existing_parser(html)
    soup = BeautifulSoup(html, 'html.parser')
    blocks = {clean(b.find(class_='courseblocktitle')).split('.',1)[0]:b
              for b in soup.select('#textcontainer .courseblock') if b.find(class_='courseblocktitle')}
    for code, expected in [('CS 1800','Corequisite(s): CS 1802'), ('CS 1802','Corequisite(s): CS 1800')]:
        block = blocks.get(code)
        if block is None or expected not in [clean(x) for x in block.find_all(class_='courseblockextra')]:
            raise ValueError('Changed CS 1800/1802 concurrent condition')
    extra = parse_subject(html, program_id=program_id, subject='CS', heading='Computer Science (CS)',
                          codes=['CS 1802'], url=URL)
    course = extra['courses'][0]
    if course['name'] != 'Seminar for CS 1800' or course['credits'] != 1:
        raise ValueError('Changed CS 1802 seminar identity or hours')
    result['courses'] += extra['courses']
    result['notes'] += extra['notes']
    result['requirements'].append(dict(id=program_id+'-req-cs-1802-concurrent',
        parent_id=program_id+'-req-cs-1800', title='CS 1802 concurrent seminar', kind='all',
        count=None, credits=1, credit_unit='semester_hours', category='other',
        source_id=program_id+'-cs-courses', source_text=None,
        summary='CS 1800 requires concurrent CS 1802. The degree preamble requires specified corequisite recitations/tools; this seminar inherits the CS 1800 requirement context.',
        course_ids=[course['id']]))
    return result


def register_cs1802(parse, parsers, program_id):
    existing = parsers[URL]
    def observe(html):
        return observe_cs1802(html, program_id, existing)
    return guard_degree(parse, program_id), {**parsers, URL: observe}
