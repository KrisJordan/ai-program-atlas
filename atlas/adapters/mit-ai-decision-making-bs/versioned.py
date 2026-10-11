"""Public EECS 6-4_2025 subject slots and overlapping designation lists.

These observations deliberately use their own course IDs. The unversioned
catalog chart is another source view, not a second set of cumulative demands.
"""
import re
from importlib import import_module
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import content, clean, course, rule, require_phrases

policies = import_module('atlas.adapters.mit-ai-decision-making-bs.policies')
PID, URL = policies.PID, policies.EMBEDDED
SID = PID + '-versioned'
core_subjects = import_module('atlas.adapters.mit-ai-decision-making-bs.core_subjects')
reviewed_subjects = import_module('atlas.adapters.mit-ai-decision-making-bs.reviewed_subjects')
ROOT_ID = 'mit-ai-version-required'
LISTS = ['AI+D_AUS', 'AI+D_SERC', 'Application_CIM', 'CIM2',
         'Computation-centric', 'Data-centric', 'Decision-centric', 'EECS',
         'Human-centric', 'MATH', 'Model-centric', 'grad_AI+D_AUS', 'grad_AUS2', 'grad_II']


def slug(text):
    return re.sub('[^a-z0-9]+', '-', text.lower()).strip('-')


def lines(node):
    """Split only structural line breaks; nested annotations are not choices."""
    line = []
    for child in node.children:
        if getattr(child, 'name', None) == 'br':
            if clean(''.join(map(str, line))):
                yield BeautifulSoup(''.join(map(str, line)), 'html.parser')
            line = []
        else:
            line.append(child)
    if clean(''.join(map(str, line))):
        yield BeautifulSoup(''.join(map(str, line)), 'html.parser')


def parse(html):
    prior = policies.parse_versioned(html)
    root = content(html, 'Degree Requirements for 6-4_2025')
    reqlist, lists = root.find(id='reqlist'), root.find(id='subject_lists')
    if reqlist is None:
        raise ValueError('Versioned required-subject section missing')
    courses = {}
    core_digests = {}

    def observe(link):
        nobr = link.find('nobr')
        code = clean(' '.join(nobr.find_all(string=True, recursive=False))) if nobr else ''
        if not re.fullmatch(r'[A-Z0-9]+\.[A-Z0-9]+(?:@\d{4}[A-Z]{2})?', code):
            raise ValueError('Unrecognized versioned subject code: ' + code)
        c = course('mit-ai-v2025', code, None, SID, URL, unit='units')
        annotation = link.find('div', class_='annotation')
        if annotation and annotation.find('b'):
            title = clean(annotation.find('b').get_text(' ', strip=True))
            # Term-qualified special offerings may show the base code in the title.
            base = code.split('@')[0]
            if not title.startswith(base + ' '):
                raise ValueError('Versioned annotation identity mismatch: ' + code)
            c['name'] = title[len(base) + 1:]
            text = clean(annotation.get_text(' ', strip=True))
            prereq = re.search(r'(Prereqs(?:/\[Coreqs\])?:.*?)\s+Units:', text)
            c['prerequisites'] = prereq[1] if prereq else None
        if annotation:
            digest = core_subjects.classify_annotation(c, clean(annotation.get_text(' ', strip=True)))
            if digest: core_digests[c['id']] = digest
        reviewed_digest = reviewed_subjects.classify(c, clean(annotation.get_text(' ', strip=True)) if annotation else None)
        if reviewed_digest: core_digests[c['id']] = reviewed_digest
        # Unit triplets, ranges and arranged units are not silently summed.
        if c['id'] in courses and courses[c['id']] != c:
            raise ValueError('Conflicting versioned annotations: ' + code)
        courses[c['id']] = c
        return c['id']

    def options(node):
        """Every printed line is one option; an ampersand is an all-of bundle."""
        result = []
        cells = node.find_all('td') if node.name == 'table' else [node]
        for cell in cells:
            for line in lines(cell):
                links = line.find_all('a', class_='annotated-link')
                if not links:
                    continue
                ids = [observe(a) for a in links]
                if len(ids) != len(set(ids)):
                    raise ValueError('Duplicate component inside one versioned option')
                visible = BeautifulSoup(str(line), 'html.parser')
                for n in visible.find_all(class_='annotation') + visible.find_all(class_='old'):
                    n.decompose()
                if len(ids) > 1 and '&' not in visible.get_text(' ', strip=True):
                    raise ValueError('Multiple subjects without explicit bundle connector')
                result.append(ids)
        if not result:
            raise ValueError('Versioned option list empty')
        return result

    pool = {}
    anchors = lists.find_all('a', attrs={'name': True})
    if [a['name'] for a in anchors] != LISTS:
        raise ValueError('Versioned subject-list inventory changed')
    for anchor in anchors:
        if anchor['name'] == 'MATH':
            continue
        table = anchor.find_next('table')
        if (table is None or table.find_parent(id='subject_lists') is None
                or table.find_previous('a', attrs={'name': True}) != anchor):
            raise ValueError('Versioned subject-list table missing')
        pool[anchor['name']] = options(table)
    require_phrases(lists, ['excluding subjects that are 6 units or less'])

    rules = [rule(ROOT_ID, '6-4_2025: departmental requirements for Fall 2025+ entrants', SID,
                  summary='Conditional source view: follow this version for its stated entry cohort. Its lists are labeled Fall 2026; term-qualified special offerings retain their exact source suffix. This is not cumulative with the separately labeled unversioned catalog chart.')]

    def add_options(key, title, opts, parent, *, count=1, overlay=False):
        gid = 'mit-ai-v2025-' + slug(key)
        summary = ('At least ' + str(count) + ' completed option(s) must have this designation; this is an overlay, not additional required slots.' if overlay else
                   'Select ' + str(count) + ' printed option(s). Complete every component of any bundled option; joint listings are retained as published alternatives.')
        rules.append(rule(gid, title, SID, parent=parent,
                          kind='note' if overlay or count != 1 else 'alternative', summary=summary))
        for index, ids in enumerate(opts, 1):
            codes = [courses[c]['code'] for c in ids]
            rules.append(rule(gid + '-' + str(index), ' + '.join(codes), SID, ids,
                              parent=gid, summary='Complete all components of this option.' if len(ids) > 1 else 'One listed subject option.'))
        return gid

    sections = reqlist.find_all('li', class_='section')
    if [clean(s.find('b').get_text()) for s in sections] != ['programming skills', 'math', 'foundation', 'Center', 'elective']:
        raise ValueError('Versioned required-subject sections changed')
    for section, marker in zip(sections, ['One programming skills subject', 'Three math subjects', 'Two foundation subjects', 'Five Center subjects', 'Three elective subjects']):
        require_phrases(section, [marker])
    add_options('programming', 'One programming-skills option', options(sections[0].find('table')), ROOT_ID)
    math_lines = list(lines(sections[1].find('div')))
    if len(math_lines) != 3 or not all(clean(n.get_text()).startswith('One of') for n in math_lines[1:]):
        raise ValueError('Versioned math slot structure changed')
    for index, line in enumerate(math_lines, 1):
        ids = [observe(a) for a in line.find_all('a', class_='annotated-link')]
        if not ids:
            raise ValueError('Versioned math slot empty')
        add_options('math-' + str(index), ['Discrete mathematics', 'Linear algebra', 'Probability or inference'][index-1], [[c] for c in ids], ROOT_ID)
    foundation = options(sections[2].find('div'))
    if len(foundation) != 2 or any(len(o) != 1 for o in foundation):
        raise ValueError('Versioned foundation slot structure changed')
    rules.append(rule('mit-ai-v2025-foundation', 'Both foundation subjects', SID,
                      [o[0] for o in foundation], parent=ROOT_ID))
    add_options('centers', 'Five Center subject options', options(sections[3].find('table')), ROOT_ID, count=5)
    elective_lines = list(lines(sections[4].find('div')))
    expected = [['Application_CIM'], ['AI+D_AUS', 'grad_AI+D_AUS'], ['EECS', 'grad_AI+D_AUS', 'grad_AUS2', 'grad_II', 'MATH']]
    actual = [[a.get('href', '')[1:] for a in n.find_all('a')] for n in elective_lines]
    if actual != expected:
        raise ValueError('Versioned elective eligibility routes changed')
    for i, names in enumerate(expected, 1):
        gid = 'mit-ai-v2025-elective-' + str(i)
        rules.append(rule(gid, ['Application CI-M elective', 'Advanced AI+D elective', 'Additional EECS, graduate or mathematics elective'][i-1], SID, parent=ROOT_ID, kind='alternative', summary='Complete one option from one of these published eligibility routes.'))
        for name in names:
            if name == 'MATH':
                rules.append(rule('mit-ai-v2025-math-open', 'Open Course 18 eligibility', SID, parent=gid, kind='note', summary=prior['requirements'][-1]['summary']))
            else:
                add_options('elective-' + str(i) + '-' + name, name, pool[name], gid)
    constraints = reqlist.find_all('ul', recursive=False)[1]
    expected_constraints = ['CIM2', 'AI+D_SERC', 'Data-centric', 'Model-centric', 'Decision-centric', 'Computation-centric', 'Human-centric']
    rows = constraints.find_all('li', recursive=False)
    if [r.find('a')['href'][1:] for r in rows] != expected_constraints:
        raise ValueError('Versioned additional-constraint inventory changed')
    for index, row in enumerate(rows):
        amount = 2 if index == 0 else 1
        require_phrases(row, ['At least ' + ('two' if amount == 2 else 'one') + ' of your completed subjects'])
        name = expected_constraints[index]
        add_options('overlay-' + name, name + ' designation overlay', pool[name], ROOT_ID, count=amount, overlay=True)
    for r in prior['requirements']:
        if r['id'] == 'mit-ai-version-cim2':
            continue  # full, bundle-aware overlay above replaces the earlier flat reference
        r['parent_id'] = ROOT_ID
        rules.append(r)
    rules.append(rule('mit-ai-v2025-eecs-eligibility', 'EECS option-pool eligibility', SID, parent=ROOT_ID, kind='note', summary='The EECS list describes subjects meeting departmental undergraduate requirements in Courses 6-1 through 6-5, excluding subjects of six units or fewer. Printed bundles remain whole options. Separate graduate lists supply additional expressly allowed routes; listing does not waive subject prerequisites.'))
    return dict(id=PID, courses=list(courses.values()), requirements=rules, observed_core_description_digests=core_digests)
