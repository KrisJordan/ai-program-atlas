"""Current Boston BSChE catalog; no unverified family or college-policy inheritance."""
from atlas.adapters.northeastern_courseleaf import parse_catalog
PROGRAM_ID = 'northeastern-chemical-engineering-ai-bsche'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/engineering/chemical/chemical-engineering-artificial-intelligence-bsche-bos/',)
TITLE = 'Chemical Engineering and Artificial Intelligence, BSChE (Boston)'
SECTIONS = ['Universitywide Requirements', 'NUpath Requirements', 'Engineering Requirements', 'Artificial Intelligence Courses', 'Supporting Courses: Mathematics/Science', 'Professional Development', 'Writing Requirements', 'Integrative Course', 'Required General Electives', 'Major GPA Requirement', 'Program Requirement']
def parse(html):
    result = parse_catalog(html, program_id=PROGRAM_ID, title=TITLE, url=SOURCES[0], required_sections=SECTIONS, award_level='other', outcome_claims=[('development of predictive models, optimization of processes, and the design of experiments', 'The program aims to apply AI to chemical-engineering prediction, process optimization and experimental design.')])
    # This BSChE paragraph says co-op MAY satisfy EX; preserve its conditionality.
    from bs4 import BeautifulSoup
    from atlas.adapters.northeastern_courseleaf import clean
    panel = BeautifulSoup(html, 'html.parser').find(id='programrequirementstextcontainer')
    policy = next((clean(p) for p in panel.find_all('p') if 'not explicitly satisfied by required engineering coursework' in clean(p)), None)
    if not policy or not all(token in policy for token in ('(IC)', '(SI)', '(DD)', '(EX)', 'may fulfill the EX requirement')):
        raise ValueError('Changed BSChE NUpath applicability policy')
    for requirement in result['requirements']:
        if requirement['summary'] == 'Co-op fulfills the experiential NUpath category.':
            requirement['summary'] = 'Required engineering coursework does not explicitly satisfy NUpath IC, SI, DD or EX. A successful co-op may fulfill EX; students must cover remaining categories with general electives.'
    apply_cornerstone_alternative(result, panel)
    for outcome in result['outcomes']: outcome['statement_type'] = 'program_aim'
    return result


def apply_cornerstone_alternative(result, panel):
    """Footnote 1 permits two complete bundles; repeated rows allocate credits."""
    from atlas.adapters.northeastern_courseleaf import clean
    footnotes = [clean(x) for x in panel.find_all('dd')]
    expected = ('Students can substitute Engineering Design (GE 1110) and '
                'Engineering Problem Solving and Computation (GE 1111) for '
                'Cornerstone of Engineering 1 (GE 1501) and Cornerstone of Engineering 2 (GE 1502).')
    import re
    normalize = lambda text: re.sub(r'\s*([().])\s*', r'\1', text)
    if normalize(expected) not in [normalize(x) for x in footnotes]:
        raise ValueError('Changed introductory engineering substitution requires review')
    old_ids = {PROGRAM_ID+'-ge-1501', PROGRAM_ID+'-ge-1502'}
    allocations = [r for r in result['requirements'] if old_ids.intersection(r['course_ids'])]
    if len(allocations) != 5 or any(not set(r['course_ids']) <= old_ids for r in allocations):
        raise ValueError('Changed engineering credit allocation rows')
    for r in allocations:
        r['kind'] = 'note'
        r['summary'] = 'Credit allocation for the Cornerstone bundle; the footnote permits the complete GE 1110/1111 substitute bundle. This row is not an additional enrollment obligation.'
    parent = PROGRAM_ID+'-req-engineering-requirements'
    template = dict(count=None, credits=None, credit_unit='semester_hours', category='other',
                    source_id=PROGRAM_ID+'-catalog', source_text=None)
    choice = PROGRAM_ID+'-req-introductory-engineering-bundle'
    result['requirements'].append(dict(template, id=choice, parent_id=parent,
        title='Introductory engineering bundle', kind='alternative', course_ids=[],
        summary='Take GE 1501 and GE 1502, or substitute both GE 1110 and GE 1111 (footnote 1).'))
    for label, codes in [('Cornerstone', ['GE 1501','GE 1502']),
                         ('Substitute', ['GE 1110','GE 1111'])]:
        result['requirements'].append(dict(template, id=choice+'-'+label.lower(), parent_id=choice,
            title=label+' course pair', kind='all', course_ids=[PROGRAM_ID+'-'+c.lower().replace(' ','-') for c in codes],
            summary='Both courses in the chosen pair are required.'))
    for code, name in [('GE 1110','Engineering Design'), ('GE 1111','Engineering Problem Solving and Computation')]:
        result['courses'].append(dict(id=PROGRAM_ID+'-'+code.lower().replace(' ','-'), code=code, name=name,
            description=None, prerequisites=None, credits=None, credit_unit='semester_hours', category='other',
            source_id=PROGRAM_ID+'-catalog', url=SOURCES[0], public_site=None, syllabus=None))

# Exact independently reviewed course-description observations from the degree audit.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_AUDIT_METADATA = register_subject_sources(PROGRAM_ID, {'GE': ['GE 1501', 'GE 1502', 'GE 1000', 'GE 1110', 'GE 1111'], 'CS': ['CS 1800', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200'], 'DS': ['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400'], 'MATH': ['MATH 1341', 'MATH 1342', 'MATH 2321', 'MATH 2341', 'MATH 3081', 'MATH 3082']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_AUDIT_METADATA)))
SOURCE_PARSERS = {**globals().get("SOURCE_PARSERS", {}), **_AUDIT_METADATA}
