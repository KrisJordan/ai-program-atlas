"""Local AI concentration distributions and applicable WPI policies.

Reuse observed catalog section parsing, but give a selected concentration its own
all-root scope. The total selection constraint includes fixed courses; it is not
an additional elective requirement. Neither parser emits a completeness audit.
"""
import importlib
from atlas.adapters.cmu_bs.common import requirement, text
from atlas.adapters.confirmed_depth3 import parse_wpi

catalog = importlib.import_module('atlas.adapters.wpi-ai-bs.concentrations')
policies = importlib.import_module('atlas.adapters.wpi-ai-bs.degree_policies')
common = importlib.import_module('atlas.adapters.wpi-ai-bs.common')
STYLESHEET = 'https://wpi.cleancatalog.net/sites/default/files/css/css_-sXQU_kB0auQ6BjlX02vsjw7FVeDqgoz5YTYcXUwjwY.css?delta=2&language=en&theme=wpi21&include=eJxVjlEOwyAMQy9EG23SzoMCZAUtBZTApt5-8FF1-7P9EsveW_-ikFqRB_gfYzlps9oOJjUD1PC0rRR2KPBvJ22RdoJTXEnP6U2iyMYXIQjSK_KaGu3L7DcVBTfBGvVkV7L2XLsbZ5GC0UPHEzhUMp-a7jfYuDjkZS5MefsCh6BNdw'
PARENT = 'https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major'
KEYS = {
    'built-natural-environment': 'environment', 'business-applications': 'business',
    'electrical-computer-engineering': 'ece', 'experience-design': 'experience',
    'life-sciences-biotechnology': 'biotechnology',
    'life-sciences-molecular-biochemistry': 'biochemistry',
    'optimization-decision-theory': 'optimization', 'robotics-engineering': 'robotics',
    'social-science-policy': 'social-policy', 'sustainable-chemical-production': 'chemical',
}
GAPS = {
    'business': 'The three published category minima total four of six courses. The page does not expressly identify the allocation rule for the remaining two; no extra free-elective pool or exact bin count is inferred.',
    'social-policy': 'Two required courses plus at least three listed/suitable special-topic choices leave the sixth-course allocation unstated. The page does not expressly state whether it must be another listed option or a separately approved course.',
}


def identity(pid, key):
    title = 'Artificial Intelligence Major with Concentration in ' + catalog.CONCENTRATIONS[key][0]
    return title, catalog.BASE + catalog.CONCENTRATIONS[key][1]


def parse(html, pid, key):
    title, url = identity(pid, key)
    # This separately validates the explicit Concentration award/AI-major host.
    parse_wpi(html, pid, title, url)
    result = catalog.parse(html, key)
    old_prefix = 'wpi-ai-bs-concentration-' + key
    for course in result['courses']:
        course['source_id'] = pid + '-catalog'
        course['category'] = 'applications'
    for row in result['requirements']:
        row['id'] = row['id'].replace(old_prefix, pid, 1)
        if row['parent_id']:
            row['parent_id'] = row['parent_id'].replace(old_prefix, pid, 1)
        row['source_id'] = pid + '-catalog'
        row['category'] = 'applications'
    root = result['requirements'][0]
    options = list(dict.fromkeys(root['course_ids']))
    root.update(kind='all', count=None, credits=None, course_ids=[],
                summary='Complete this selected concentration’s local distribution. Host BS degree requirements remain outside this local inventory.')
    result['requirements'].insert(1, requirement(
        pid, 'selection-total', 'Total concentration selection — includes fixed courses',
        pid + '-catalog', parent=root['id'], kind='choose_courses', count=6,
        course_ids=options, category='applications',
        summary='Six distinct courses in total, including all fixed courses and selections satisfying the following bins. This is not six additional electives; do not add this total to its component choices. Observed options do not close separately stated open or unresolved routes.'))
    # The catalog marks these subtotal fields as hidden. The separately
    # verified linked stylesheet suppresses them; they are not published loads.
    if key in ('experience', 'optimization'):
        _, detail = common.document(html, title)
        expected = '2/2' if key == 'experience' else '1/3'
        matches = [n for n in detail.select('.degree-row-subtotal')
                   if n.select_one('.col-2') and text(n.select_one('.col-2')) == expected]
        if not matches or any(not n.find_parent(class_='hide-subtotal') for n in matches):
            raise ValueError('WPI subtotal visibility/field changed; review the new source')
        result['requirements'].append(requirement(
            pid, 'hidden-subtotal', 'Suppressed catalog subtotal field', pid + '-catalog',
            parent=root['id'], kind='note', category='applications',
            summary='The raw '+expected+' subtotal occurs inside a hide-subtotal section. The independently inspected linked stylesheet hides this field; it is not treated as a visible requirement conflicting with the explicit local course distribution. Review if source visibility changes.'))
    elif key in GAPS:
        result['requirements'].append(requirement(
            pid, 'remaining-allocation', 'Unresolved remaining-course allocation', pid + '-catalog',
            parent=root['id'], kind='note', category='applications', summary=GAPS[key]))
    result.update(id=pid, title=title, award_level='concentration', program_kind='concentration',
                  notes=['Local concentration component only. Total selections include fixed courses; source choice descriptors are not additive. Parent degree is a separate record.'])
    return result


def parse_parent(html, pid, key):
    title, _ = identity(pid, key)
    _, detail = common.document(html, 'Artificial Intelligence Major')
    body = text(detail)
    guards = ['one and only one concentration', '6 distinct courses', "student's chosen concentration",
              'sole advisor', 'co-advised', '10 units program requirements', 'at least 4/3 units']
    if any(g not in body for g in guards):
        raise ValueError('AI parent concentration/overlap/MQP clause changed')
    specs = [
        ('parent-scope', 'AI host relationship and concentration total', 'The AI BS requires exactly one concentration with six distinct courses (6/3 units). This is the total including fixed requirements and local choices, not an extra elective block. The host degree remains separately audited.'),
        ('parent-mqp', 'Concentration-related MQP and advising', 'The AI MQP is 3/3 units and applies AI knowledge and techniques within the selected concentration. A sole adviser must be AI core/collaborative faculty within that discipline; otherwise an AI core/collaborative faculty member and a faculty member with disciplinary knowledge co-advise. This is the host MQP applied to the concentration, not a second additional MQP.'),
        ('parent-overlap', 'Science overlap and degree-level advanced floor', 'If a course overlaps the natural/engineering-science requirement and concentration or disciplinary electives, add other BS-AI distribution courses to retain ten program units. The host degree’s 4/3-unit floor at 4000 level or above can be met across core, concentration and other distribution work; it is not an extra four-course local concentration minimum.'),
    ]
    return dict(id=pid, title=title, award_level='concentration', program_kind='concentration',
                curriculum_status='partial', requirements=[requirement(pid, rid, label, pid+'-parent',
                kind='note', summary=summary, category='other') for rid,label,summary in specs])


def parse_policy(html, pid, key, policy):
    title, _ = identity(pid, key)
    result = policies.parse(html, pid, title, policy)
    result.update(award_level='concentration', program_kind='concentration')
    if policy == 'options':
        result['requirements'] = [r for r in result['requirements']
                                  if r['id'].endswith(('-concentration', '-overlap'))]
    return result


def attach(namespace, key):
    pid = namespace['PROGRAM_ID']
    namespace['SOURCES'] = [identity(pid, key)[1], PARENT]
    namespace['SOURCE_PARSERS'] = {
        namespace['SOURCES'][0]: namespace['parse'],
        PARENT: lambda html: parse_parent(html, pid, key),
    }
    if key in ('experience', 'optimization'):
        namespace['SOURCES'].append(STYLESHEET)
        namespace['SOURCE_PARSERS'][STYLESHEET] = lambda css: parse_stylesheet(css, pid)
    for policy in ['options', 'grading', 'graduate']:
        url = policies.BASE + policies.POLICIES[policy][0]
        namespace['SOURCES'].append(url)
        namespace['SOURCE_PARSERS'][url] = lambda html, policy=policy: parse_policy(html, pid, key, policy)


def parse_stylesheet(css, pid):
    compact = ''.join(css.split())
    # Remove only insignificant whitespace while preserving both descendant selectors.
    expected = '.hide-subtotal .degree-row-subtotal,.hide-subtotal .subtotal-row-wrapper{display:none !important}'
    if ''.join(expected.split()) not in compact:
        raise ValueError('WPI subtotal display rule changed')
    return dict(id=pid, curriculum_status='partial', requirements=[requirement(
        pid, 'subtotal-display-policy', 'Catalog subtotal display policy', pid+'-catalog-stylesheet',
        kind='note', category='other', summary='The stylesheet linked by the inspected catalog explicitly hides degree subtotal rows within hide-subtotal sections. Suppressed machine subtotal values are not promoted to visible student requirements; visible course-distribution prose remains represented.')])
