"""MIT Course 6-4 chart: local choices and explicitly incomplete degree-wide scope."""
from atlas.adapters.national_curriculum_common import content, clean, require_phrases, rule
from atlas.adapters.degree_table_observations import Tables

PROGRAM_ID = 'mit-ai-decision-making-bs'
SOURCES = ['https://catalog.mit.edu/degree-charts/artifical-intelligence-decision-making-course-6-4/', 'https://catalog.mit.edu/degree-charts/', 'https://catalog.mit.edu/degree-charts/eecs-subject-groupings/']
SOURCE_ID = PROGRAM_ID + '-identity'


def parse(html):
    root = content(html, 'Bachelor of Science in Artificial Intelligence and Decision Making')
    require_phrases(root, ['Choose 12 units of the following:', 'Select five subjects, including one from each area:', "department's CIM2 list", 'The units for any subject that counts as one of the 17 GIR subjects cannot also be counted as units required beyond the GIRs.', 'Swimming requirement, plus four physical education courses for eight points.', 'Credit cannot be awarded without completion of a 6-unit disciplinary module.', 'Units in Major 168-177', 'Units in Major That Also Satisfy the GIRs (36)', 'Total Units Beyond the GIRs Required for SB Degree 180-189', 'Science Requirement 6', 'Total GIR Subjects Required for SB Degree 17', 'at least two of these subjects', 'One subject that satisfies a degree requirement in Course 6 or Course 18', 'One subject from the list of AI+D Advanced Undergraduate Subjects', 'Students must satisfy at least one program requirement or elective with a subject from the SERC-qualified subjects listed below.'])
    tables = root.find_all('table', class_='sc_courselist')
    if len(tables) != 3:
        raise ValueError('Degree chart table structure changed')
    for heading, table in zip(['AI+D Advanced Undergraduate Subjects', 'Social and Ethical Responsibilities of Computing (SERC) Subjects'], tables[1:]):
        if clean(table.find_previous('h4').get_text(' ', strip=True)) != heading:
            raise ValueError('Degree option-pool heading changed')
    # MIT abbreviates 6.C011 visually as C011; its explicit link title supplies the full code.
    for a in root.find_all('a', class_='code'):
        if a.get('title') and clean(a.get_text()) == 'C011':
            a.string = a['title']
    for sup in root.find_all('sup'):
        sup.decompose()
    t = Tables('mit-ai', SOURCE_ID, SOURCES[0], unit='units')
    fundamentals = t.group('Fundamentals')
    programming = t.group('Programming preparation: 12 units', parent=fundamentals['id'], kind='alternative', credits=12, summary='Choose the 12-unit single-subject route or one listed two-subject bundle; individual component units are not inferred.')
    centers = t.group('Five centers: five subjects including one from each area', credits=60, summary='Complete five subjects, including one from every center. A course appearing in multiple areas is one course; the combined module row is one listed option.')
    current = programming
    stage = 'programming'
    area_names = ['Data-centric', 'Model-centric', 'Decision-centric', 'Computation-centric', 'Human-centric']
    areas = []
    last_required = None
    probability = application = None
    for row in tables[0].find_all('tr'):
        cells = row.find_all('td', recursive=False)
        if not cells:
            continue
        text = clean(cells[0].get_text(' ', strip=True))
        obs = t.row(row)
        if obs is None:
            if text == 'Select one of the following:':
                probability = t.group('Probability or inference', parent=fundamentals['id'], kind='alternative', credits=12)
                current, stage = probability, 'probability'
            elif text in area_names:
                current = t.group(text, parent=centers['id'], kind='alternative', summary='Select one listed subject option. Complete every component of a bundled option.')
                areas.append(text)
                stage = 'centers'
            elif text == 'Select one of the following Application CI-M subjects:':
                application = t.group('Application CI-M: one subject', kind='alternative', summary='Select one of the listed application CI-M subjects; the chart gives a 12–15-unit range.')
                current, stage = application, 'application'
            elif text == 'Electives':
                stage = 'notes'
            elif text == 'Unrestricted Electives':
                value = clean(cells[-1].get_text())
                if not value.isdigit():
                    raise ValueError('Unrestricted elective amount changed format')
                t.group('Unrestricted electives', kind='choose_credits', credits=int(value), summary='Complete the published unrestricted elective units; no finite approved pool is supplied by this chart.')
            continue
        if stage == 'programming' and not row.find('div', style='margin-left: 20px;'):
            current, stage = fundamentals, 'required'
        if stage == 'notes':
            raise ValueError('Unexpected course row outside reviewed choice sections')
        if 'orclass' in row.get('class', []):
            if stage != 'required' or last_required is None:
                raise ValueError('Unrecognized alternative course row')
            alt = t.group('Linear algebra alternative', parent=fundamentals['id'], kind='alternative')
            last_required['parent_id'] = alt['id']
            t.group(obs['title'], parent=alt['id'], ids=obs['ids'])
        else:
            node = t.group(obs['title'], parent=current['id'], ids=obs['ids'])
            if stage == 'required':
                last_required = node
    if areas != area_names or probability is None or application is None:
        raise ValueError('Required center or CI-M selection missing')
    pools = []
    for table in tables[1:]:
        ids = []
        for row in table.find_all('tr'):
            obs = t.row(row)
            if obs:
                ids.extend(obs['ids'])
        if not ids:
            raise ValueError('Finite option pool missing')
        pools.append(ids)
    t.group('AI+D advanced undergraduate elective', kind='choose_courses', count=1, ids=pools[0], summary='Choose one listed advanced subject; the chart gives 12–15 units for this slot.')
    t.group('Social and ethical responsibilities of computing', kind='choose_courses', count=1, ids=pools[1], summary='Satisfy at least one program requirement or elective using a listed SERC-qualified subject; this is an overlay, not necessarily an additional course.')
    policies = [
        ('course6-18', 'Additional Course 6 or 18 elective', 'Complete one subject satisfying a degree requirement in Course 6 or Course 18; the slot carries 12–15 units. The applicable full subject inventory remains unreviewed.'),
        ('cim2', 'Second CI-M subject', 'At least one requirement or elective must use a second CI-M subject from the department CIM2 list, beyond the application CI-M requirement. The linked general CI-M list has been inspected, but its exact CIM2 applicability remains unresolved.'),
        ('serc-module', 'SERC module credit condition', 'Credit for 6.C01 requires completion of a 6-unit disciplinary module; consult an advisor. Do not treat its listed 6 units as sufficient by itself.'),
        ('gir', 'General Institute Requirements', 'The chart summarizes 17 GIR subjects: six science, eight HASS (at least two CI-H), two REST (identified as 6.1200 and 18.C06), and one laboratory requirement (identified as 6.1010, 12 units). Detailed distributions and choice pools remain unreviewed.'),
        ('pe', 'Physical education and swimming', 'Complete the swimming requirement and four physical education courses totaling eight points. Points are not academic units.'),
        ('unit-accounting', 'Major, GIR overlap and degree accounting', 'The chart reports 168–177 major units, 36 major units also satisfying GIRs, and 180–189 units beyond the GIRs. Units for any of the 17 GIR subjects cannot also count toward units required beyond the GIRs. Ranges are preserved, not replaced with a fabricated single total.')]
    for suffix, title, summary in policies:
        t.rules.append(rule('mit-ai-policy-' + suffix, title, SOURCE_ID, kind='note', summary=summary))
    return dict(id=PROGRAM_ID, title='Artificial Intelligence and Decision Making', award_level='BS', program_kind='degree', courses=list(t.courses.values()), requirements=t.rules)


def parse_cim_reference(html):
    """Observe the linked general CI-M list without asserting CIM2 eligibility."""
    root = content(html, 'Communication-Intensive in the Major Subjects')
    pane = root.find(id='cimtextcontainer')
    if pane is None:
        raise ValueError('Linked CI-M pane missing')
    table = pane.find('table', class_='sc_courselist')
    if table is None:
        raise ValueError('Linked CI-M table missing')
    sid = PROGRAM_ID + '-cim-reference'
    t = Tables('mit-ai', sid, SOURCES[2], unit='units')
    ids = []
    for row in table.find_all('tr'):
        obs = t.row(row)
        if obs:
            ids.extend(obs['ids'])
    if not ids:
        raise ValueError('Linked CI-M list empty')
    note = rule('mit-ai-cim-reference', 'Linked general CI-M reference list', sid, ids, kind='note', summary='The degree chart links this general EECS CI-M list, but the page does not identify a CIM2 subset. These course observations are a reference pool, not a verified set of second-CI-M choices for Course 6-4.')
    return dict(id=PROGRAM_ID, courses=list(t.courses.values()), requirements=[note])


SOURCE_PARSERS = {SOURCES[2]: parse_cim_reference}

from importlib import import_module

policies = import_module('atlas.adapters.mit-ai-decision-making-bs.policies')
versioned = import_module('atlas.adapters.mit-ai-decision-making-bs.versioned')

SOURCES.extend([policies.GIR, policies.GRADES, policies.GRADUATION,
                policies.DEPARTMENT, policies.PETITIONS, policies.EMBEDDED])
SOURCE_PARSERS.update({
    policies.GIR: policies.parse_gir,
    policies.GRADES: policies.parse_grades,
    policies.GRADUATION: policies.parse_graduation,
    policies.DEPARTMENT: policies.parse_department,
    policies.PETITIONS: policies.parse_petitions,
    policies.EMBEDDED: versioned.parse,
})

registrar = import_module('atlas.adapters.mit-ai-decision-making-bs.registrar')
supplement = import_module('atlas.adapters.mit-ai-decision-making-bs.supplement')
for module in (registrar, supplement):
    SOURCES.extend(module.SOURCE_PARSERS)
    SOURCE_PARSERS.update(module.SOURCE_PARSERS)

# These field plans are optional degree-wide HASS branches, not AI-major slots.
hass_fields = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_fields')
SOURCES.extend(hass_fields.SOURCE_PARSERS)
SOURCE_PARSERS.update(hass_fields.SOURCE_PARSERS)

hass_departments = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_departments')
SOURCES.extend(hass_departments.SOURCE_PARSERS)
SOURCE_PARSERS.update(hass_departments.SOURCE_PARSERS)

hass_open_fields = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_open_fields')
SOURCES.extend(hass_open_fields.SOURCE_PARSERS)
SOURCE_PARSERS.update(hass_open_fields.SOURCE_PARSERS)

hass_languages = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_languages')
SOURCES.extend(hass_languages.SOURCE_PARSERS)
SOURCE_PARSERS.update(hass_languages.SOURCE_PARSERS)

hass_architecture = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_architecture')
hass_access_review = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_access_review')
for module in (hass_architecture, hass_access_review):
    SOURCES.extend(module.SOURCE_PARSERS)
    SOURCE_PARSERS.update(module.SOURCE_PARSERS)

hass_cmsw = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_cmsw')
SOURCES.extend(hass_cmsw.SOURCE_PARSERS)
SOURCE_PARSERS.update(hass_cmsw.SOURCE_PARSERS)

hass_music_theater = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_music_theater')
SOURCES.extend(hass_music_theater.SOURCE_PARSERS)
SOURCE_PARSERS.update(hass_music_theater.SOURCE_PARSERS)
