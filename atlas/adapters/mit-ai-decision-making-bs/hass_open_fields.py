"""Conditional HASS plans with published open-subject criteria and local policies."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import content, clean, course, rule, require_phrases
from importlib import import_module
optional = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_departments').optional
PID = 'mit-ai-decision-making-bs'
ANTHRO = 'https://anthropology.mit.edu/undergraduate/requirements'
HISTORY = 'https://history.mit.edu/academics/undergraduate-studies/'
LING = 'https://web.mit.edu/linguistics/undergraduate/LingConcentration.html'
WGS = 'http://wgs.mit.edu/degree-requirements'
LIT = 'https://lit.mit.edu/academics/students/'
URBAN = 'https://dusp.mit.edu/undergraduate'
STS = 'https://sts-program.mit.edu/academics/undergraduate/concentration/'


def wrapped(nodes):
    return BeautifulSoup('<main>' + ''.join(str(n) for n in nodes) + '</main>', 'html.parser').main


def parse_anthropology(html):
    root = content(html, 'MIT Anthropology Requirements')
    label = root.find('u', string='Concentration')
    if label is None:
        raise ValueError('Anthropology concentration section missing')
    first = label.find_parent('p')
    nodes = [first]
    for n in first.find_next_siblings():
        if n.name == 'hr':
            break
        nodes.append(n)
    pane = wrapped(nodes)
    require_phrases(pane, ['Three subjects (minimum of 33 credits)', 'One of the following:', 'Two additional Anthropology subjects'])
    sid, prefix = PID + '-hass-anthropology', 'mit-ai-hass-anthropology'
    cs = []
    for li in pane.find_all('li'):
        if li.find('ul'):
            continue
        match = re.fullmatch(r'(21A\.[A-Z0-9]+) (.+)', clean(li.get_text(' ', strip=True)))
        if match:
            cs.append(course(prefix, match[1], match[2], sid, ANTHRO, unit='units', category='human_context'))
    if not cs:
        raise ValueError('Anthropology foundation pool missing')
    return dict(id=PID, courses=cs, requirements=[optional(prefix, 'Anthropology', sid),
        rule(prefix + '-foundation', 'One introductory anthropology choice', sid, [c['id'] for c in cs], parent=prefix, kind='choose_courses', count=1),
        rule(prefix + '-additional', 'Two additional Anthropology subjects', sid, parent=prefix, kind='choose_courses', count=2, summary='The source permits two additional Anthropology subjects as an open criterion; the three named introductory options are not asserted to be the full additional-subject pool.'),
        rule(prefix + '-minimum', 'Three subjects and minimum stated credit amount', sid, parent=prefix, kind='note', credits=33, summary='The concentration requires three subjects and a minimum of 33 source-stated credits. This page uses credits, not an explicit normalized unit definition; the amount is not converted. The linked MIT HASS approval/grading rules remain applicable.')])


def parse_history(html):
    root = content(html, 'Undergraduate Studies')
    heading = root.find(lambda n: n.name == 'summary' and clean(n.get_text(' ', strip=True)) == 'History Concentration')
    if heading is None:
        raise ValueError('History concentration heading missing')
    pane = heading.find_parent('details')
    require_phrases(pane, ['A History concentration consists of three subjects', 'At most two may be an introductory level course', 'There are no geographical distribution requirements', 'At least two of these subjects must be taken at MIT', 'may apply their History concentration subjects to a History minor'])
    sid, prefix = PID + '-hass-history', 'mit-ai-hass-history'
    return dict(id=PID, requirements=[optional(prefix, 'History', sid),
        rule(prefix + '-three', 'Three History subjects', sid, parent=prefix, kind='choose_courses', count=3, summary='Select three History subjects, no more than two introductory. At least two must be taken at MIT. There is no geographical distribution requirement; students may focus on a place, period or theme or range across the field.'),
        rule(prefix + '-minor-overlap', 'History concentration/minor overlap', sid, parent=prefix, kind='note', summary='History concentration subjects may also count toward a History minor. The minor’s separate seminar, historical-methods and period-distribution rules are not concentration requirements.')])


def parse_linguistics(html):
    root = content(html, 'Undergraduate HASS Concentration in Linguistics')
    require_phrases(root, ['Three subjects, which must include', '24.900 (Introduction to Linguistics)', '24.9000 (How Language Works)', 'one subject chosen from', 'one other subject in linguistics', 'only HASS classes can fulfill'])
    sid, prefix = PID + '-hass-linguistics', 'mit-ai-hass-linguistics'
    text = clean(root.get_text(' ', strip=True))
    cs = []
    for code, name in re.findall(r'(24\.\d+) \(([^)]+)\)', text):
        if code not in {c['code'] for c in cs}:
            cs.append(course(prefix, code, name, sid, LING, unit='units', category='human_context'))
    by = {c['code']: c['id'] for c in cs}
    if not {'24.900', '24.9000', '24.901', '24.902', '24.903'} <= by.keys():
        raise ValueError('Linguistics subject-choice structure changed')
    return dict(id=PID, courses=cs, requirements=[optional(prefix, 'Linguistics', sid),
        rule(prefix + '-intro', 'One introductory linguistics subject', sid, [by[c] for c in ['24.900', '24.9000']], parent=prefix, kind='choose_courses', count=1),
        rule(prefix + '-field', 'One phonology, syntax or semantics subject', sid, [by[c] for c in ['24.901', '24.902', '24.903']], parent=prefix, kind='choose_courses', count=1),
        rule(prefix + '-other', 'One other HASS linguistics subject', sid, parent=prefix, kind='choose_courses', count=1, summary='Choose one other linguistics subject; the open choice may include but is not limited to the listed options. All three concentration subjects must be HASS classes.')])


def parse_wgs(html):
    root = content(html, 'Degree Requirements')
    h = root.find(lambda n: n.name == 'h2' and clean(n.get_text(' ', strip=True)) == 'Concentration')
    pane = h.find_parent('li', class_='accordion-item') if h else None
    if pane is None:
        raise ValueError('WGS concentration accordion missing')
    require_phrases(pane, ["at least three Women's & Gender Studies subjects", 'WGS.101', 'is required', 'Two additional courses', 'Only one of these subjects can be counted towards the HASS-Distribution', 'second semester of their junior year', 'should consult'])
    require_phrases(root, ['Students who minor in Women\'s & Gender Studies do not have to complete a separate concentration', 'must still fill out concentration proposal and completion forms'])
    match = re.search(r'WGS\.101 (.+?) \(HASS-H, CI-H\)', clean(pane.get_text(' ', strip=True)))
    if not match:
        raise ValueError('WGS required subject label missing')
    sid, prefix = PID + '-hass-wgs', 'mit-ai-hass-wgs'
    c = course(prefix, 'WGS.101', match[1], sid, WGS, unit='units', category='human_context')
    return dict(id=PID, courses=[c], requirements=[optional(prefix, "Women's and Gender Studies", sid),
        rule(prefix + '-required', 'Required WGS introduction', sid, [c['id']], parent=prefix, kind='all'),
        rule(prefix + '-additional', 'Two additional WGS subjects', sid, parent=prefix, kind='choose_courses', count=2, summary='At least three WGS subjects in total, with the required introduction plus two additional WGS subjects of the student’s choice. This is an open departmental subject criterion.'),
        rule(prefix + '-approval', 'Distribution overlap and proposal/completion', sid, parent=prefix, kind='note', summary='Only one subject may also count toward HASS Distribution. Consult the WGS program manager and submit the proposal by the second semester of junior year; proposal and completion forms remain required. Completing the WGS minor removes the need for a separate concentration, but does not waive those forms.')])


def parse_literature(html):
    root = content(html, 'Concentration')
    panes = [n for n in root.find_all('div', class_='et_pb_text_inner') if n.find(lambda h: h.name in ('h1', 'h2', 'h3') and clean(h.get_text(' ', strip=True)) == 'Concentration') and 'intermediate tier' in n.get_text()]
    if not panes or len({clean(p.get_text(' ', strip=True)) for p in panes}) != 1:
        raise ValueError('Literature concentration content missing or conflicting')
    pane = panes[0]
    require_phrases(pane, ['three subjects', 'intermediate tier (400-, 500-, 600-)', 'seminar (700-) tier', 'Two six-unit samplings courses', '300 and 600- tier', 'combined by petition', 'permission of the instructor', 'must meet with a concentration advisor'])
    require_phrases(root, ['at most one such subject toward a concentration in Literature', 'considered the equivalent of a particular subject', 'General Elective Credit', 'do not count toward', 'HASS-Elective Credit'])
    sid, prefix = PID + '-hass-literature', 'mit-ai-hass-literature'
    return dict(id=PID, requirements=[optional(prefix, 'Literature', sid),
        rule(prefix + '-three', 'Three-subject Literature plan', sid, parent=prefix, kind='choose_courses', count=3, summary='Select three subjects with a concentration advisor, including at least one intermediate-tier (400/500/600) and one seminar-tier (700) subject. These tier minima are within the three, not additional subjects.'),
        rule(prefix + '-substitutions', 'Sampling combination and outside-subject approval', sid, parent=prefix, kind='note', summary='Two six-unit sampling subjects from the 300/600 tiers may combine by petition as one intermediate-tier subject. Certain outside-Literature subjects may count with instructor permission; the source does not publish a closed approved list.'),
        rule(prefix + '-transfer', 'Literature transfer-credit distinctions', sid, parent=prefix, kind='note', summary='The Literature transfer examiner determines credit after reviewing description/syllabus, writing assignments, student work or exam, and transcript. General elective transfer credit does not satisfy HASS. At most one nonspecific HASS-elective transfer subject may count toward the concentration; subject-equivalent credit instead counts as the specified Literature subject, with its units and HASS status. The separate minor and major distribution requirements do not apply to this concentration.')])


URBAN_GROUPS = ['Climate Change and Environmental Planning', 'Designing the Urban Environment', 'Energy and Infrastructure', 'Housing, Land Use Law, and Social Change', 'International Development and Human Rights', 'Negotiation and Leadership', 'Policy Analysis and Urban Problem-Solving', 'Public Interest Technology', 'Urban History']


def parse_urban(html):
    root = content(html, 'Undergraduate')
    h = root.find(id='hass-concentrations')
    if h is None:
        raise ValueError('Urban HASS section missing')
    pane = h.parent.parent
    require_phrases(pane, ['list suggests some of the most popular combinations', 'individually-crafted HASS concentration', 'selecting three HASS subjects', 'Subject offerings change on an annual basis'])
    sid, prefix = PID + '-hass-urban', 'mit-ai-hass-urban'
    cs, groups = {}, {}
    for ul in pane.find_all('ul'):
        label = clean(ul.find_previous('p').get_text(' ', strip=True))
        groups[label] = []
        for li in ul.find_all('li', recursive=False):
            match = re.fullmatch(r'(11\.[A-Z0-9]+(?:\[J\])?) (.+)', clean(li.get_text(' ', strip=True)))
            if not match:
                raise ValueError('Urban suggested-subject row changed')
            c = course(prefix, match[1], match[2].rstrip('*'), sid, URBAN, unit='units', category='human_context')
            cs[c['id']] = c
            groups[label].append(c['id'])
    if list(groups) != URBAN_GROUPS:
        raise ValueError('Urban suggested topic structure changed')
    rules = [optional(prefix, 'Urban Studies', sid),
        rule(prefix + '-three', 'Three HASS subjects selected with the department', sid, parent=prefix, kind='choose_courses', count=3, summary='The department helps choose three HASS subjects suited to the student’s interests and background. The named combinations are suggestions, not nine mandatory tracks or a closed approved-course list. Individually crafted plans may follow Institute guidelines. Offerings change annually; consult the department.')]
    for i, (name, ids) in enumerate(groups.items()):
        rules.append(rule(prefix + '-suggestion-' + str(i + 1), name + ': suggested combination', sid, ids, parent=prefix, kind='note', summary='Illustrative source grouping under the department-approved three-subject rule. This is not an additive requirement or an assertion that every member must be taken.'))
    rules.append(rule(prefix + '-annotation', 'Unexplained clinic annotation', sid, parent=prefix, kind='note', summary='The source marks 11.074 Cybersecurity Clinic with an asterisk without explaining it in this section. Its inclusion is a suggested option, not evidence of an additional requirement, current offering or unrestricted eligibility. Confirm any special condition with the department.'))
    return dict(id=PID, courses=list(cs.values()), requirements=rules)


def parse_sts(html):
    root = content(html, 'Concentration')
    require_phrases(root, ['any three STS Tier I or Tier II Subjects', 'Approval of the online concentration proposal form requires an in-person meeting', 'changes to your approved proposal', 'submit the change online', 'approved and has no changes', 'on paper before AY2015'])
    sid, prefix = PID + '-hass-sts', 'mit-ai-hass-sts'
    return dict(id=PID, requirements=[optional(prefix, 'Science, Technology, and Society', sid),
        rule(prefix + '-three', 'Three STS Tier I or Tier II subjects', sid, parent=prefix, kind='choose_courses', count=3, summary='Choose any three subjects in the published STS Tier I/Tier II classifications. The separate minor’s additional three subjects and required STS.004 are not concentration requirements.'),
        rule(prefix + '-approval', 'Required advising and proposal revision', sid, parent=prefix, kind='note', summary='Proposal approval requires an in-person meeting with the STS concentration advisor. Before submitting completion, changes to an approved plan must be reported to the undergraduate officer and revised online. An unchanged approved plan may be completed online directly. Students with paper proposals from before AY2015 should ask the HASS office which completion process applies.')])


SOURCE_PARSERS = {ANTHRO: parse_anthropology, HISTORY: parse_history, LING: parse_linguistics, WGS: parse_wgs, LIT: parse_literature, URBAN: parse_urban, STS: parse_sts}

from functools import partial
STS_TIERS = {1: 'https://sts-program.mit.edu/academics/undergraduate/tier-i-subjects/', 2: 'https://sts-program.mit.edu/academics/undergraduate/tier-ii-subjects/'}
STS_TRANSFER = 'https://sts-program.mit.edu/academics/undergraduate/transfer-credit-undergraduates/'


def parse_sts_tier(tier, html):
    title = 'Tier ' + ('I' if tier == 1 else 'II') + ' Subjects'
    root = content(html, title)
    if tier == 1:
        require_phrases(root, ['suggest that you start', 'may also take more than one Tier I subject'])
    else:
        require_phrases(root, ['recommended that students take at least one Tier I subject', 'but not required'])
    sid, prefix = PID + '-hass-sts-tier-' + str(tier), 'mit-ai-hass-sts-tier-' + str(tier)
    cs = {}
    for a in root.find_all('a'):
        match = re.fullmatch(r'(STS\.[A-Z0-9]+) (.+)', clean(a.get_text(' ', strip=True)))
        if match:
            c = course(prefix, match[1], match[2], sid, STS_TIERS[tier], unit='units', category='human_context')
            cs[c['id']] = c
    if not cs:
        raise ValueError('STS classified subject list missing')
    return dict(id=PID, courses=list(cs.values()), requirements=[rule(prefix, title + ': eligible concentration pool', sid, list(cs), parent='mit-ai-hass-sts', kind='note', summary='Any three distinct Tier I or Tier II subjects satisfy the STS concentration selection rule. Starting with Tier I is recommended, not mandatory for a concentrator. Duplicate subject codes across tiers remain one subject; these source-specific observations do not allow double counting.')])


def parse_sts_transfer(html):
    root = content(html, 'Transfer Credit for Undergraduates')
    require_phrases(root, ['strongly recommended', 'preliminary approval before taking the class', 'B- or better', 'Advanced Placement (AP) credit may not be used', 'secondary school', 'unaccredited and/or non-degree-granting', 'final say', 'STS concentrators can use only one non-MIT subject', 'Harvard University and Wellesley College', 'do not need to request transfer credit', 'HASS Education Office'])
    sid = PID + '-hass-sts-transfer'
    return dict(id=PID, requirements=[rule('mit-ai-hass-sts-transfer', 'External STS coursework: grade, limit and approval', sid, parent='mit-ai-hass-sts', kind='note', summary='Concentrators may use at most one non-MIT subject. STS’s undergraduate academic officer has final approval after reviewing course/syllabus, work samples and transcript; preliminary approval is strongly recommended, not stated mandatory. The outside grade must be B− or better. AP, secondary-school and unaccredited/non-degree institution coursework cannot supply HASS transfer credit. Harvard/Wellesley cross-registration does not need a transfer request, but requests to count those subjects toward HASS go to the HASS Education Office. The broader abroad exceptions stated for majors/minors are not extended to concentrators.')])


SOURCE_PARSERS.update({url: partial(parse_sts_tier, tier) for tier, url in STS_TIERS.items()})
SOURCE_PARSERS[STS_TRANSFER] = parse_sts_transfer
