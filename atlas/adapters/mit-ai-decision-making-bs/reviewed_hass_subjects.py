"""Source observations for manual HASS judgments; never classify from a course code.

This disjoint contribution does not register source parsers or change degree roles.
The primary MIT adapter integrates only explicitly reviewed, unchanged observations.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def clean(value):
    return ' '.join((value.get_text(' ', strip=True) if hasattr(value, 'get_text') else value or '').split())


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest() if value else None


def observation_digest(observation):
    return digest(json.dumps(observation, sort_keys=True, ensure_ascii=False, separators=(',', ':')))


def unit_total(units_text, notation_html):
    """Sum an observed numeric triplet only under MIT's published unit convention."""
    text = clean(BeautifulSoup(notation_html, 'html.parser'))
    if 'The total unit credit for a subject is obtained by adding together all the units shown.' not in text:
        raise ValueError('MIT unit convention changed or missing')
    match = re.match(r'^(\d+)-(\d+)-(\d+)(?:\s|;|$)', units_text or '')
    return sum(map(int, match.groups())) if match else None


def _field(node, name):
    field = node.select_one('.field--name-field-' + name)
    if field is None:
        return None
    return clean(field.select_one('.field__item') or field) or None


def observe_architecture(html):
    soup = BeautifulSoup(html, 'html.parser')
    if not soup.find('h1') or clean(soup.find('h1')) != 'Classes':
        raise ValueError('Architecture class directory heading changed')
    rows = []
    for node in soup.select('.expcol-wrap'):
        code = _field(node, 'subject-number')
        if not code:
            continue
        title = clean(node.select_one('.faux-full-title'))
        if not title:
            raise ValueError('Architecture subject lost its title')
        rows.append(dict(
            code=code, name=title, description=_field(node, 'subject-description'),
            prerequisites=_field(node, 'prerequisites'), units=_field(node, 'course-units'),
            term=clean(' '.join(filter(None, [_field(node, 'semester'), _field(node, 'year')]))),
            enrollment=_field(node, 'enrollment'), preference=_field(node, 'preference-given-to'),
            required_of=_field(node, 'required-of'), restricted_elective=_field(node, 'restricted-elective'),
            repeated=_field(node, 'can-be-repeated-for-credit'),
        ))
    return rows


def observe_anthropology_titles(html):
    """Keep the current directory's literal codes, meeting clauses and level labels."""
    soup = BeautifulSoup(html, 'html.parser')
    if not any(clean(h) == 'MIT Anthropology Subjects' for h in soup.find_all('h1')):
        raise ValueError('Anthropology subject heading changed')
    rows = []
    for table in soup.select('table.subjects-table'):
        for node in table.find_all('tr'):
            cells = node.find_all('td', recursive=False)
            if len(cells) < 2:
                continue
            label = clean(cells[0])
            match = re.match(r'(21A\.[\w]+)(?:\s|/|$)', label)
            if match is None:
                continue
            name = clean(cells[1])
            link = cells[1].find('a')
            if not name or link is None:
                raise ValueError('Anthropology subject lost paired title/link')
            rows.append(dict(code=match[1], name=name, course_label=label,
                             linked_url=link.get('href'), description=None,
                             prerequisites=None, units=None, term=None))
    if not rows:
        raise ValueError('Anthropology subject tables missing')
    return rows


def observe_economics_titles(html):
    """Observe the two concentration lists, excluding the adjacent minor pool."""
    from importlib import import_module
    # Existing source-specific policy guards also withdraw changed list context.
    module = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_departments')
    module.parse_economics(html)
    soup = BeautifulSoup(html, 'html.parser')
    rows = []
    for title in ['Concentration in Economics', 'Concentration in Development Economics']:
        heading = soup.find(lambda node: node.name == 'h3' and clean(node) == title)
        if heading is None:
            raise ValueError('Economics concentration title missing')
        for node in heading.parent.find_all('li'):
            if node.find('ul'):
                continue
            text = clean(node)
            match = re.fullmatch(r'(14\.[A-Z0-9]+(?:\[J\])?) (.+)', text)
            if match is None:
                raise ValueError('Economics concentration subject row changed')
            prerequisite = re.search(r'\(Prereq\. ([^)]+)\)', match[2])
            name = re.split(r'\s*\(', match[2])[0].replace('*', '').removesuffix(' and/or').strip()
            rows.append(dict(code=match[1], name=name, description=None,
                             prerequisites=prerequisite[1] if prerequisite else None,
                             units=None, term=None, source_annotation=text, list_heading=title))
    return rows


def observe_shass_field_titles(key, html):
    """Reuse guarded literal field-list parsing, discarding its legacy taxonomy."""
    from importlib import import_module
    module = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_fields')
    parsed = module.parse_field(key, html)
    return [dict(listed_id=row['id'], code=row['code'], name=row.get('name'),
                 description=None, prerequisites=None, units=None, term=None,
                 field=module.FIELDS[key]['title']) for row in parsed.get('courses', [])]


def observe_remaining_list_titles(kind, html):
    """Literal observations from named, guarded source lists; no category defaults."""
    from importlib import import_module
    parsers = {
        'computing': ('supplement', 'parse_hass'),
        'ethics': ('hass_departments', 'parse_philosophy'),
        'linguistics': ('hass_open_fields', 'parse_linguistics'),
        'urban': ('hass_open_fields', 'parse_urban'),
        'education': ('hass_cmsw', 'parse_education'),
        'cms_pool': ('hass_cmsw', 'parse_pool'),
        'language_placement': ('hass_languages', 'parse_placement'),
        'music': ('hass_music_theater', 'parse_music'),
    }
    if kind not in parsers:
        raise ValueError('Unknown reviewed subject-list source')
    module, name = parsers[kind]
    parser = getattr(import_module('atlas.adapters.mit-ai-decision-making-bs.' + module), name)
    return [dict(listed_id=row['id'], code=row['code'], name=row.get('name'),
                 description=None, prerequisites=None, units=None, term=None,
                 source_kind=kind) for row in parser(html).get('courses', [])]


def observe_french_spotlights(html):
    """Read the actual prose spotlights separately from the title-only schedule."""
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('main')
    if main is None or clean(main.find('h1')) != 'French & Francophone Studies':
        raise ValueError('French program heading changed')
    rows = []
    for heading in main.find_all('strong'):
        match = re.fullmatch(r'(21G\.\d+)\s+(.+)', clean(heading))
        if match is None:
            continue
        body = heading.find_parent('p').find_next('p')
        if body is None or body.find('strong') is not None or not clean(body):
            raise ValueError('French spotlight description missing')
        term = next((clean(v) for v in heading.find_all_previous('div', class_='value')
                     if re.fullmatch(r'(Fall|Spring|IAP) \d{4}', clean(v))), None)
        if term is None:
            raise ValueError('French spotlight term missing')
        note = heading.find_parent('div', class_='value')
        enrollment = next((clean(p) for p in note.find_all('p')
                           if clean(p).startswith('A note regarding the enrollment policy')), None) if note else None
        rows.append(dict(code=match[1], name=match[2], description=clean(body),
                         prerequisites=None, units=None, term=term, enrollment=enrollment))
    if not rows:
        raise ValueError('French spotlight subjects missing')
    return rows


def observe_literature(html):
    soup = BeautifulSoup(html, 'html.parser')
    selected = soup.find('select', attrs={'name': 'semester'})
    if selected is None:
        raise ValueError('Literature term selector missing')
    term = selected.find('option', selected=True) or selected.find('option')
    rows = []
    for node in soup.select('.parentrow'):
        link = node.select_one('.description-link')
        if link is None:
            continue
        body = soup.find('div', class_='description-row', attrs={'data-course': link.get('data-course')})
        if body is None:
            raise ValueError('Literature subject lost its paired description panel')
        meta = clean(body.find('p', recursive=False))
        pre = re.search(r'Prereq:\s*(.*?)\s*Units:', meta)
        rows.append(dict(
            code=clean(link), name=clean(node.select_one('span')),
            description=clean(body.select_one('.et-l--post')) or None,
            prerequisites=pre.group(1) if pre else None,
            units=meta.split('Units:', 1)[1].strip() if 'Units:' in meta else None,
            term=clean(term), locator=link.get('data-course'),
        ))
    return rows


def observe_literature_aliases(html):
    """Retain explicit same-subject and meets-with clauses without merging IDs.

    A separate observer keeps earlier primary-code observation digests stable.
    Only manually approved, exact source clauses can support an alias review.
    """
    soup = BeautifulSoup(html, 'html.parser')
    rows = []
    for row in observe_literature(html):
        body = soup.find('div', class_='description-row', attrs={'data-course': row['locator']})
        meta = clean(body.find('p', recursive=False))
        same = re.search(r'Same subject as:\s*(.*?)(?:Meets with:|Prereq:|Units:|$)', meta)
        meets = re.search(r'Meets with:\s*(.*?)(?:Prereq:|Units:|$)', meta)
        if same is not None:
            rows.append({**row, 'same_subject_as': same[1].strip(),
                         'meets_with': meets[1].strip() if meets else None})
    return rows


def observe_history(html):
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('main')
    if main is None or main.find('h1') is None:
        raise ValueError('History subject main heading missing')
    heading = clean(main.find('h1'))
    match = re.match(r'(21H\.[\w]+(?:\[J\])?)\s+(.+)', heading)
    codes = [clean(a) for a in main.select('.cp-subject-catalog-field a')]
    if match is None and (not codes or not re.fullmatch(r'21H\.[\w]+', codes[0])):
        raise ValueError('History subject code/title format changed')
    term = main.select_one('.taxonomy-subject-term')
    return dict(code=match[1] if match else codes[0], name=match[2] if match else heading,
                description=' '.join(clean(x) for x in main.select('p.wp-block-paragraph')) or None,
                catalog_codes=codes, prerequisites=None, units=None,
                term=clean(term).removeprefix('Term ').strip() if term else None)


def observe_wgs(html):
    soup = BeautifulSoup(html, 'html.parser')
    if not any(clean(h) == 'Subjects' for h in soup.find_all('h1')):
        raise ValueError('WGS subject directory heading changed')
    rows = []
    for node in soup.select('.summary-item'):
        link = node.select_one('.summary-title-link')
        if link is None:
            continue
        match = re.match(r'(WGS\.[\w]+)\s+(.+)', clean(link))
        if match is None:
            continue
        rows.append(dict(code=match[1], name=match[2],
                         description=clean(node.select_one('.summary-excerpt')) or None,
                         source_url=urljoin('http://wgs.mit.edu/subjects', link['href']),
                         prerequisites=None, units=None, term=None))
    return rows


def matched_review(course, observation, source_url, manifest=None):
    """Return a saved decision only on an exact listed identity and observed payload.

    This is reuse of a dated manual judgment, not a new review. It does not mutate
    the course, sum MIT unit triplets, merge identities, or infer a required role.
    """
    if manifest is None:
        manifest = json.loads(Path(__file__).with_name('reviewed_hass_subjects.json').read_text())
    reviewed = manifest['courses'].get(course['id'])
    if reviewed is None or reviewed.get('review_status') != 'reviewed':
        return None
    if (course.get('code'), course.get('name'), course.get('source_id')) != (reviewed['listed_code'], reviewed['listed_name'], reviewed['listed_source_id']):
        return None
    for evidence in reviewed.get('observations', []):
        if evidence.get('approved_for_integration') and evidence.get('source_url') == source_url and evidence.get('observation_digest') == observation_digest(observation):
            return evidence
    return None


def observe_performing_arts(html):
    soup = BeautifulSoup(html, 'html.parser')
    term = soup.select_one('.b-class-schedule__semester-select option[selected]')
    if term is None:
        raise ValueError('Performing arts selected term missing')
    rows = []
    for button in soup.select('.b-class-schedule__course-toggle'):
        code = clean(button.select_one('.b-class-schedule__class-number'))
        title = clean(button.select_one('.b-class-schedule__class-title'))
        body = soup.find(id=button.get('aria-controls'))
        if not code or body is None:
            raise ValueError('Performing arts paired description missing')
        paragraphs = [clean(p) for p in body.find_all('p')]
        match = re.match(r'^(\d+-\d+-\d+)\s+units', paragraphs[0] if paragraphs else '')
        rows.append(dict(code=code, name=title, description=' '.join(paragraphs[1:] if match else paragraphs) or None,
                         units=match[1] if match else None, source_unit_line=paragraphs[0] if match else None,
                         prerequisites=None, term=clean(term), locator=button.get('aria-controls')))
    return rows


def observe_wgs_detail(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = clean(soup.select_one('h1.entry-title'))
    match = re.match(r'(WGS\.[\w]+)\s+(.+)', title)
    body = soup.select_one('.blog-item-content .sqs-html-content')
    if match is None or body is None:
        raise ValueError('WGS course-detail heading/body changed')
    paragraphs = [clean(p) for p in body.find_all('p', recursive=False)]
    if len(paragraphs) < 2 or 'Units:' not in paragraphs[0]:
        raise ValueError('WGS detail metadata/description changed')
    units = re.search(r'Units:\s*(\d+-\d+-\d+)', paragraphs[0])
    return dict(code=match[1], name=match[2], description=paragraphs[1],
                units=units[1] if units else None, source_metadata=paragraphs[0],
                prerequisites=None, term='Fall 2026-2027')


def observe_cmsw(html):
    """Observe the public expanded term directory, including explicit alias labels."""
    soup = BeautifulSoup(html, 'html.parser')
    panel = soup.find('section', id='mit-subject-list')
    if panel is None or panel.find('h2') is None:
        raise ValueError('CMS/W public term directory missing')
    term = clean(panel.find('h2'))
    if not re.fullmatch(r'(Fall|Spring|IAP) \d{4}', term):
        raise ValueError('CMS/W term label changed')
    rows = []
    for node in panel.select('.academic_term_tier__subject'):
        code = clean(node.select_one('.academic_term_tier__subject-course-number'))
        title = clean(node.select_one('.academic_term_tier__subject-course-title'))
        body = node.select_one('.academic-term-tier__subject-description')
        if not code or not title or body is None:
            raise ValueError('CMS/W subject lost paired identity/description')
        metadata = {}
        for field in body.select('li'):
            label = field.find('strong')
            if label is not None:
                key = clean(label).rstrip(':')
                metadata[key] = clean(field)[len(clean(label)):].strip()
        description = clean(' '.join(clean(p) for p in body.find_all('p', recursive=False))) or None
        rows.append(dict(code=code, name=title, description=description,
                         prerequisites=metadata.get('Prereq'), units=metadata.get('Units'),
                         term=term, same_subject_as=metadata.get('Same subject as'),
                         meets_with=metadata.get('Meets with'), designation=metadata.get('Designation')))
    if not rows:
        raise ValueError('CMS/W public subject rows missing')
    return rows


def observe_language_titles(html):
    """Literal public language schedule labels, not descriptions or alias merges."""
    soup=BeautifulSoup(html,'html.parser')
    main=soup.find('main')
    if main is None or main.find('h1') is None:
        raise ValueError('Global Languages page heading missing')
    heading=clean(main.find('h1'))
    if not heading.endswith('Studies'):
        raise ValueError('Global Languages program heading changed')
    rows=[]
    for codes in main.select('.credit-section-wrap'):
        row=codes.parent
        title_node=codes.find_next_sibling('div')
        title=clean(title_node.select_one('.value')) if title_node else None
        prefix=codes.select_one('.value')
        prefix=clean(prefix)
        suffixes=[clean(x.select_one('.value')) for x in codes.select('.semester-section-titile')]
        term=next((clean(v) for v in row.find_all_previous('div',class_='value')
                   if re.fullmatch(r'(Fall|Spring|IAP) \d{4}',clean(v))),None)
        if not prefix or not suffixes or not title or term is None:
            raise ValueError('Global Languages schedule identity/term missing')
        for suffix in suffixes:
            rows.append(dict(code=prefix+'.'+suffix,name=title,term=term,
                             description=None,prerequisites=None,units=None,
                             heading=heading,printed_companion_codes=[prefix+'.'+x for x in suffixes],
                             linked_urls=[a['href'] for a in codes.find_all('a',href=True)]))
    if not rows:
        raise ValueError('Global Languages schedule rows missing')
    return rows


def observe_political_pdf_titles(text):
    """Re-observe the dated, public PDF titles without inheriting pool taxonomy."""
    import importlib.util
    path=Path(__file__).with_name('political_pdf.py')
    spec=importlib.util.spec_from_file_location('mit_political_title_source',path)
    source=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    parsed=source.parse_text(text)
    rows=[]
    for c in parsed['courses']:
        restrictions=[n['summary'] for n in parsed['requirements']
                      if n.get('title','').startswith('Conditional enrollment:') and c['id'] in n.get('course_ids',[])]
        rows.append(dict(code=c['code'],name=c['name'],description=None,prerequisites=None,
                         credits=c['credits'],units='9 unit IAP version' if c['credits']==9 else None,
                         term='Dated reference; URL says Updated July10 2024; no printed document date',
                         restrictions=restrictions))
    return rows


def observe_sts_titles(html):
    soup=BeautifulSoup(html,'html.parser')
    headings=[clean(h) for h in soup.find_all(['h1','h2'])]
    tiers=[h for h in headings if h in ['Tier I Subjects','Tier II Subjects']]
    if len(tiers)!=1:
        raise ValueError('STS tier source heading changed')
    rows=[]
    for link in soup.find_all('a',href=True):
        match=re.fullmatch(r'(STS\.\d{3}J?)\s+(.+)',clean(link))
        if match:
            rows.append(dict(code=match[1],name=match[2],description=None,prerequisites=None,
                             units=None,term=None,tier=tiers[0],linked_url=link['href']))
    if not rows:
        raise ValueError('STS tier subject list missing')
    return rows


def observe_ocw_syllabus(html):
    """Read dated public OCW prose; never turn its schedule into current catalog rules."""
    soup = BeautifulSoup(html, 'html.parser')
    banner = soup.select_one('#course-banner')
    main = soup.select_one('#course-main-content')
    if banner is None or main is None:
        raise ValueError('OCW course identity/content container missing')
    parts = clean(banner.select_one('.course-number-term-detail')).split(' | ')
    name = clean(banner.find('h1'))
    if len(parts) != 3 or not re.fullmatch(r'(Fall|Spring|Summer|IAP) \d{4}', parts[1]) or not name:
        raise ValueError('OCW code, term or title changed')
    sections = {}
    for heading in main.find_all(['h2', 'h3', 'h4', 'h5']):
        title = clean(heading).rstrip(':')
        if title == 'Prerequisites / Requisitos Previos':
            title = 'Prerequisites'
        if title not in ['Description', 'Course Description', 'Course Overview', 'Course Summary', 'Overview', 'Class Objectives', 'Objectives and Organization', 'Purpose', 'Introduction', 'Goals for the Class', 'Course Goals and Organization', 'Class Overview', 'Course Aims', 'Course Description and Learning Objectives', 'Course Description (HASS-D Language Option)', 'Course Objectives and Procedures', 'コースの目標 (もくひょう) Course Objectives', 'Course Objectives', 'General Description', 'El propósito', 'Course Description and Goals', 'Course Description / Descripción Del Curso', 'Contenido', 'Films', 'Prerequisites', 'Prerequisite']:
            continue
        content = []
        for sibling in heading.next_siblings:
            if getattr(sibling, 'name', None) in ['h2', 'h3', 'h4', 'h5']:
                break
            if hasattr(sibling, 'get_text'):
                content.append(clean(sibling))
        sections[title] = clean(' '.join(content)) or None
    description = next((sections[k] for k in ['Description', 'Course Description', 'Course Overview', 'Course Summary', 'Overview', 'Class Objectives', 'Objectives and Organization', 'Purpose', 'Introduction', 'Goals for the Class', 'Course Goals and Organization', 'Class Overview', 'Course Aims', 'Course Description and Learning Objectives', 'Course Description (HASS-D Language Option)', 'Course Objectives and Procedures', 'コースの目標 (もくひょう) Course Objectives', 'Course Objectives', 'General Description', 'El propósito', 'Course Description and Goals', 'Course Description / Descripción Del Curso', 'Contenido', 'Films'] if sections.get(k)), None)
    if not description:
        raise ValueError('OCW syllabus actual description section missing')
    prerequisites = sections.get('Prerequisites', sections.get('Prerequisite'))
    if prerequisites is None and parts[0] == '14.20':
        embedded = re.search(r'Students must have completed .+? before enrolling in 14\.20\.', description)
        if embedded:
            prerequisites = embedded.group(0)
    unit_match = re.search(r'(?:^|[.!?] )This (\d+)-unit (?:subject|undergraduate-level course)\b', description)
    return [dict(code=parts[0], name=name, term=parts[1], level=parts[2],
                 description=description,
                 prerequisites=prerequisites,
                 units=(unit_match[1] + ' units') if unit_match else None)]


def observe_minds_machines(html):
    """Exact instructor page linked by MIT Philosophy's Spring2020 history."""
    soup = BeautifulSoup(html, 'html.parser')
    if clean(soup.find('h1')) != 'Minds and Machines (Spring 2020)':
        raise ValueError('Minds and Machines dated course heading changed')
    identity = soup.find('a', href='https://learning-modules.mit.edu/class/index.html?uuid=/course/24/sp20/24.09')
    paragraph = next((p for p in soup.find_all('p') if clean(p).startswith('This course is an introduction to the central questions in philosophy of mind.')), None)
    if identity is None or paragraph is None:
        raise ValueError('Minds and Machines explicit code link or description changed')
    return [dict(code='24.09', name='Minds and Machines', term='Spring 2020',
                 description=clean(paragraph), prerequisites=None, units=None,
                 identity_link=identity['href'])]


def observe_ocw_course(html):
    """Actual OCW home description when the linked syllabus has no prose section."""
    soup = BeautifulSoup(html, 'html.parser')
    banner = soup.select_one('#course-banner')
    body = soup.select_one('#expanded-description') or soup.select_one('#full-description')
    if banner is None or body is None:
        raise ValueError('OCW course identity or complete description missing')
    parts = clean(banner.select_one('.course-number-term-detail')).split(' | ')
    title = clean(banner.find('h1'))
    if len(parts) != 3 or not re.fullmatch(r'(Fall|Spring|Summer|IAP) \d{4}', parts[1]) or not title:
        raise ValueError('OCW course code, term or title changed')
    # The publisher separates a related MITx offering from the archived class.
    # Do not fold enrollment marketing for that distinct course into this one.
    for heading in list(body.find_all(['p', 'h2', 'h3', 'h4'])):
        if clean(heading) == 'MITx Online Version':
            for sibling in list(heading.next_siblings):
                sibling.extract()
            heading.decompose()
            break
    for button in body.find_all('button'):
        button.decompose()
    if not clean(body):
        raise ValueError('OCW complete description is empty')
    return [dict(code=parts[0], name=title, term=parts[1], level=parts[2],
                 description=clean(body), prerequisites=None, units=None)]


def observe_ocw_language_syllabus(html):
    """Pin dated language placement/registration sections independently of prerequisites."""
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.select_one('#course-main-content')
    try:
        observation = observe_ocw_syllabus(html)[0]
    except ValueError:
        # This dated syllabus puts the actual Spanish description in an
        # unheaded paragraph; require its exact banner and introductory clause.
        banner = soup.select_one('#course-banner')
        if banner is None or main is None:
            raise
        parts = clean(banner.select_one('.course-number-term-detail')).split(' | ')
        name = clean(banner.find('h1'))
        paragraph = next((p for p in main.find_all('p') if clean(p).startswith('Esta asignatura está destinada a aquellos alumnos que hayan terminado')), None)
        if parts != ['21G.712', 'Fall 2003', 'Undergraduate'] or name != 'Spanish Conversation and Composition' or paragraph is None:
            raise
        description = clean(paragraph)
        prerequisite = re.match(r'Esta asignatura .+?curso equivalente\.', description)
        if prerequisite is None:
            raise ValueError('Spanish conversation preparation clause changed')
        observation = dict(code=parts[0], name=name, term=parts[1], level=parts[2], description=description, prerequisites=prerequisite.group(0), units=None)
    policy = {}
    for heading in main.find_all(['h2', 'h3', 'h4', 'h5']):
        title = clean(heading).rstrip(':')
        if title not in ['Selection Criteria of Registration', 'Sign up for', 'Sign Up For', 'Nivel', 'Enrollment Limits', 'Note Regarding Course Number 21G.592 (The Japanese Language Option)', 'Writing and Speaking Assignments for a Communication Intensive Course', 'Writing and Speaking Assignments as a Communication Intensive Course']:
            continue
        parts = []
        for sibling in heading.next_siblings:
            if getattr(sibling, 'name', None) in ['h2', 'h3', 'h4', 'h5']:
                break
            if hasattr(sibling, 'get_text'):
                parts.append(clean(sibling))
        policy[title] = clean(' '.join(parts))
    observation['registration_policy'] = policy
    # These statements are explicitly printed in the description, not inferred
    # from the course sequence number or from a student's eligibility.
    preparation = {
        '21G.101': 'The course presupposes no prior background in the language.',
        '21G.111': 'No prior knowledge of the Chinese language is required.',
    }.get(observation['code'])
    if observation['prerequisites'] is None and preparation and preparation in observation['description']:
        observation['prerequisites'] = preparation
    if observation['code'] == '21G.030' and observation['term'] == 'Spring 2015':
        explicit = re.search(r'This (\d+)-unit class .+?requires no Asian language background nor any other prerequisites\.', observation['description'])
        if explicit:
            observation['units'] = explicit.group(1) + ' units'
            observation['prerequisites'] = explicit.group(0)
    return [observation]


def observe_music_semester_capture(payload):
    """Read a public selected-term DOM transcript, never a cached-fact substitute.

    The schedule keeps one URL while its visible semester changes. An ordinary
    HTTP HTML response is not this dated browser observation and must fail.
    """
    try:
        capture = json.loads(payload)
    except (ValueError, TypeError) as exc:
        raise ValueError('Music selected-term browser capture required; default HTTP page does not identify this snapshot') from exc
    if not isinstance(capture, dict) or capture.get('capture_kind') != 'public_music_semester_dom' or not re.fullmatch(r'(Fall|Spring) \d{4}', capture.get('semester', '')):
        raise ValueError('Music visible semester identity missing')
    rows=[]
    for course in capture.get('courses', []):
        paragraphs=course.get('paragraphs', [])
        if not re.fullmatch(r'21M\.[0-9]{3}J?', course.get('code','')) or not course.get('name') or len(paragraphs)<2:
            raise ValueError('Music visible code/title/description missing')
        units=re.fullmatch(r'(\d+-\d+-\d+) units\. HASS-A', clean(paragraphs[0]))
        if units is None or not all(isinstance(p,str) and clean(p) for p in paragraphs):
            raise ValueError('Music visible unit line or paragraph structure changed')
        rows.append(dict(code=course['code'],name=clean(course['name']),term=capture['semester'],description=clean(' '.join(paragraphs[1:])),units=units[1],source_unit_line=clean(paragraphs[0]),prerequisites=None,locator='Visible semester selection / expanded '+course['code']+' course panel'))
    if not rows:
        raise ValueError('Music visible course panels missing')
    return rows


def observe_theater_semester_capture(payload):
    """Actual selected Theater panels; reject default HTTP or invented code aliases."""
    try:
        capture=json.loads(payload)
    except (ValueError,TypeError) as exc:
        raise ValueError('Theater selected-term browser capture required') from exc
    if not isinstance(capture,dict) or capture.get('capture_kind')!='public_theater_semester_dom' or not re.fullmatch(r'(Fall|Spring) \d{4}',capture.get('semester','')):
        raise ValueError('Theater visible semester identity missing')
    rows=[]
    for course in capture.get('courses',[]):
        paragraphs=course.get('paragraphs',[])
        if not re.fullmatch(r'21T\.[0-9]{3}J?',course.get('code','')) or not course.get('name') or len(paragraphs)<2:
            raise ValueError('Theater visible code/title/description missing')
        metadata=re.fullmatch(r'Prereq: (.+?)\n(\d+-\d+-\d+) units\. HASS-A; CI-H',paragraphs[0])
        if metadata is None or not all(isinstance(p,str) and clean(p) for p in paragraphs):
            raise ValueError('Theater visible prerequisite/unit line changed')
        rows.append(dict(code=course['code'],name=clean(course['name']),term=capture['semester'],description=clean(' '.join(paragraphs[1:])),units=metadata[2],source_unit_line=clean(paragraphs[0]),prerequisites=metadata[1],locator='Visible semester selection / expanded '+course['code']+' course panel'))
    if not rows:raise ValueError('Theater visible course panels missing')
    return rows


def observe_concourse_subject(html):
    """Read public Concourse detail fields, without assigning a catalog year."""
    soup = BeautifulSoup(html, 'html.parser')
    if not any(clean(h) == 'Core Concourse Classes' for h in soup.find_all('h2')):
        raise ValueError('Concourse detail heading missing')
    block = soup.select_one('.class')
    top = block.select_one('.top') if block else None
    title = block.select_one('.title') if block else None
    body = block.select_one('.teaser .text') if block else None
    if top is None or title is None or body is None:
        raise ValueError('Concourse identity or description fields missing')
    for flag in top.find_all('span'):
        flag.decompose()
    code = clean(top)
    if not re.fullmatch(r'(?:CC|21H)\.\d+(?:/(?:\d+|CC|21H)\.\d+)?', code):
        raise ValueError('Concourse printed course label changed')
    text = clean(body)
    start = re.search(r'\b(?:Explores (?:the question|questions|the ambitions)|Students read early modern|This course surveys)\b', text)
    if start is None:
        raise ValueError('Concourse subject description missing or changed')
    description = text[start.start():]
    if description.endswith(' L. Rabieh'):
        description = description[:-len(' L. Rabieh')]
    metadata = text[:start.start()]
    prep = re.search(r'Prereq:\s*(.+?)(?=\s+Units:|$)', metadata)
    units = re.search(r'Units:\s*(\d+-\d+-\d+)(?:\s|$)', metadata)
    return [dict(code=code, name=clean(title), term=None, description=description,
                 prerequisites=prep.group(1).strip() if prep else None,
                 units=units.group(1) if units else None, source_text=text)]


def observe_wgs_archive_detail(html):
    """Read historical WGS details from visible year/term labels, not URL slugs."""
    soup = BeautifulSoup(html, 'html.parser')
    title = clean(soup.select_one('h1.entry-title'))
    match = re.fullmatch(r'(WGS\.[\w]+)\s+(.+)', title)
    blocks = soup.select('.blog-item-content .sqs-html-content')
    years = {clean(a) for a in soup.find_all('a', href=True)
             if '/wgs-courses/category/' in a['href'] and re.fullmatch(r'\d{4}-\d{4}', clean(a))}
    terms = {clean(a) for a in soup.find_all('a', href=True)
             if '/wgs-courses/tag/' in a['href'] and clean(a) in ['Fall', 'Spring', 'IAP', 'Summer']}
    if match is None or not blocks or len(years) != 1 or len(terms) != 1:
        raise ValueError('WGS archive identity, body or visible year/term changed')
    source_text = ' '.join(clean(b) for b in blocks)
    topic_context = [clean(h) for b in blocks for h in b.find_all(['h2', 'h3'])]
    metadata_blocks = [em for b in blocks for em in b.find_all('em') if 'Units:' in clean(em)]
    if len(metadata_blocks) != 1:
        raise ValueError('WGS archive metadata structure changed')
    metadata = clean(metadata_blocks[0])
    units = re.search(r'Units:\s*(\d+-\d+-\d+)', metadata)
    if units is None:
        raise ValueError('WGS archive numeric unit statement missing')
    prep = re.search(r'Prereq:\s*(.+?)(?=\s+Units:|$)', metadata)
    metadata_blocks[0].decompose()
    # Reviewed pages place metadata in italics and instructor credits in strong.
    # Retain the entire original text in the pinned observation so no change to
    # exclusions, attribution or ancillary fields silently reuses this review.
    paragraphs = []
    for b in blocks:
        for p in b.find_all('p'):
            for node in p.find_all(['em', 'strong']):
                node.decompose()
            if clean(p):
                paragraphs.append(clean(p))
    description = ' '.join(paragraphs)
    if len(description) < 100:
        raise ValueError('WGS archive substantial description missing')
    return [dict(code=match[1], name=match[2], term=next(iter(terms))+' '+next(iter(years)),
                 description=description, units=units[1], source_text=source_text,
                 source_metadata=metadata, topic_context=topic_context,
                 prerequisites=prep[1].strip() if prep else None)]


def observe_dlab_course(html):
    """Read course-specific D-Lab fields without turning page anecdotes into dates."""
    soup = BeautifulSoup(html, 'html.parser')
    title = clean(soup.select_one('h1.page-header'))
    article = soup.select_one('article.course')
    body = article.select_one('.field--name-body') if article else None
    info = article.select_one('.course-information') if article else None
    if not title.startswith('D-Lab:') or body is None or info is None:
        raise ValueError('D-Lab course identity or content missing')
    fields = {}
    for field in info.select('.field'):
        label = field.select_one('.field--label')
        value = field.select_one('.field--item')
        if label is not None and value is not None:
            fields[clean(label)] = clean(value)
    if not fields.get('Course #') or not re.fullmatch(r'\d+-\d+-\d+', fields.get('Units (credit hours)', '')):
        raise ValueError('D-Lab course number or unit statement changed')
    prep_heading = next((p for p in body.find_all('p') if clean(p) == 'Prerequisites'), None)
    prep = prep_heading.find_next_sibling('p') if prep_heading else None
    if prep is None:
        raise ValueError('D-Lab explicit prerequisite section missing')
    description = clean(body)
    if len(description) < 100:
        raise ValueError('D-Lab actual description missing')
    return [dict(code=fields['Course #'], name=title, term=None,
                 description=description, prerequisites=clean(prep),
                 units=fields['Units (credit hours)'], source_fields=fields)]


def observe_sts_department_detail(html):
    """Read actual STS descriptions; a schedule/eligibility-only entry is insufficient."""
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.select_one('article.sts_subject .academic-content .entry-content')
    paragraphs = [clean(p) for p in body.find_all('p') if clean(p)] if body else []
    match = re.fullmatch(r'(STS\.\d{3}J?)\s+(.+)', paragraphs[0]) if paragraphs else None
    if match is None or len(paragraphs) < 3:
        raise ValueError('STS detail subject/description fields missing')
    term = re.search(r'\b(Spring|Fall|IAP|Summer) \d{4}\b', paragraphs[1])
    units = re.search(r'(\d+-\d+-\d+) [Uu]nits', paragraphs[1])
    description = ' '.join(paragraphs[2:])
    if term is None or units is None or not re.search(r'This course will focus|Develops students[’\u0027] abilities', description):
        raise ValueError('STS dated actual description missing; schedule or eligibility only')
    return [dict(code=match[1], name=match[2], term=term[0], units=units[1],
                 prerequisites=None, description=description, source_text=clean(body))]


def observe_urban_project_course(html):
    """Read explicitly identified course/project evidence, not generic project titles."""
    soup = BeautifulSoup(html, 'html.parser')
    project = soup.select_one('.field--name-field-project-summary')
    if project is not None:
        paragraphs = [clean(p) for p in project.find_all('p')]
        matched = [p for p in paragraphs if p.startswith('The 11.171/11.172 Indigenous Environmental Planning MIT course')]
        if len(matched) != 1:
            raise ValueError('DUSP explicit course identity missing')
        return [dict(code='11.171/11.172', name='Indigenous Environmental Planning', term=None,
                     description=matched[0], units=None, prerequisites=None,
                     source_context=' '.join(paragraphs[:3]))]
    title = soup.select_one('.title h1 .typed')
    subtitle = soup.select_one('.subtitle h2')
    about = soup.select_one('.modal-content')
    match = re.fullmatch(r'Course (11\.154/11\.454) \| (Fall \d{4})', clean(subtitle))
    if title is None or title.get('data-typed-items') != 'Big Data, Visualization, and Society' or match is None or about is None or clean(about.find('h2')) != 'About':
        raise ValueError('Urban course showcase identity, term or About description missing')
    description = ' '.join(clean(p) for p in about.find_all('p'))
    if not description.startswith('Each year, the class works') or 'Students used data collected' not in description:
        raise ValueError('Urban dated course/project description changed')
    return [dict(code=match[1], name=title['data-typed-items'], term=match[2],
                 description=description, units=None, prerequisites=None,
                 topic=clean(soup.select_one('.title h2')))]


def observe_common_ground_subject(html):
    """Read published Common Ground descriptions and actual offered-under numbers."""
    soup = BeautifulSoup(html, 'html.parser')
    title = clean(soup.find('h1'))
    heading = re.fullmatch(r'C\d+\s+(.+)', title)
    metadata_node = next((n for n in soup.find_all(['li', 'p']) if clean(n).startswith('Offered under:')), None)
    if heading is None or metadata_node is None:
        raise ValueError('Common Ground subject title or identity fields missing')
    container = metadata_node.find_parent('div', class_='col')
    divider = container.find('hr', recursive=False) if container else None
    if divider is None:
        raise ValueError('Common Ground metadata/description divider missing')
    metadata = clean(metadata_node.parent) if metadata_node.name == 'li' else clean(metadata_node)
    fields = {}
    for key in ['Offered under', 'Term(s)', 'Level', 'Units', 'Prerequisite', 'Instructors']:
        match = re.search(re.escape(key)+r':\s*(.*?)(?=\s+(?:Offered under|Term\(s\)|Level|Units|Prerequisite|Instructors):|$)', metadata)
        if match:
            fields[key] = match[1].strip()
    if not fields.get('Offered under') or not re.fullmatch(r'\d+', fields.get('Units', '')):
        raise ValueError('Common Ground printed course numbers or units changed')
    paragraphs = []
    for sibling in divider.find_next_siblings():
        if sibling.name == 'p':
            paragraphs.append(clean(sibling))
    description = ' '.join(paragraphs)
    if len(description) < 100:
        raise ValueError('Common Ground actual description missing')
    return [dict(code=fields['Offered under'], name=heading[1], term=None,
                 availability=fields.get('Term(s)'), description=description,
                 prerequisites=fields.get('Prerequisite'), units=fields['Units'], source_fields=fields)]


def observe_political_methods_syllabus(text):
    """Observe actual dated faculty syllabus text; never borrow preparation from HTML."""
    text = clean(text)
    identity = re.match(r'(17\.835): (Machine Learning and Data Science in Politics) (Fall \d{4}) Instructor: Professor In Song Kim', text)
    if identity is None:
        raise ValueError('Political methods syllabus identity or dated instructor missing')
    def section(start, end):
        match = re.search(re.escape(start) + r' (.*?) ' + re.escape(end), text)
        if match is None:
            raise ValueError('Political methods syllabus section changed: ' + start)
        return match[1]
    description = section('3 Course Description', '4 Prerequisites')
    preparation = section('4 Prerequisites', '5 Notes on Computing')
    computing = section('5 Notes on Computing', '6 Policy on the Use of Generative AI')
    outline = text.split('11 Tentative Course Outline ', 1)
    if len(description) < 100 or len(outline) != 2 or '6.100A' not in preparation:
        raise ValueError('Political methods description, preparation or outline missing')
    return [dict(code=identity[1], name=identity[2], term=identity[3], units=None,
                 description=description, prerequisites=preparation, computing=computing,
                 outline=outline[1], syllabus_digest=digest(text))]


def observe_political_data_news(html):
    """Read the exact institutional teaching feature, excluding unrelated news cards."""
    soup = BeautifulSoup(html, 'html.parser')
    title = clean(soup.find('h1'))
    date = soup.find('time')
    body = soup.select_one('.paragraph--type--content-block-text')
    text = clean(body)
    if title != 'Exploring data and its influence on political behavior' or date is None or body is None:
        raise ValueError('Political data teaching feature identity missing')
    if 'In class 17.831 (Data and Politics)' not in text or 'redesigned the course for the spring 2025 semester' not in text:
        raise ValueError('Political data exact course identity or teaching term changed')
    return [dict(code='17.831', name='Data and Politics', term='Spring 2025',
                 description=text, prerequisites=None, units=None,
                 publication_date=date.get('datetime'), article_title=title)]


def observe_sts_archive_description(html):
    """Observe read STS archive panels; require actual content beyond logistics."""
    soup = BeautifulSoup(html, 'html.parser')
    title = clean(soup.find('h1'))
    body = soup.select_one('article.sts_subject .academic-content .entry-content')
    text = clean(body)
    identity = re.match(r'(STS\.\d{3}J?)(?:/44[34])?[:\s]+(.+)', title)
    starts = {
        'STS.051': 'Students will research the history and culture of East Campus',
        'STS.053': 'This problem-solving course is located at the intersection',
        'STS.044': 'Explores emotional and intellectual impact of objects.',
        'STS.086J': '“Cultures of Computing” is an interdisciplinary course',
        'STS.040': 'Do you want to know why the dietary proteins',
        'STS.014': 'A growing body of scientific and educational research',
        'STS.041': 'From efforts by the American Medical Association',
        'STS.043': 'Focuses on the memoir as a window',
        'STS.008': 'How have computers changed the way',
        'STS.011': 'We are in the midst of an explosion',
        'STS.035': 'STS.035 is a making class',
        'STS.012': 'When controversies about science and technology emerge',
        'STS.056': 'Examines the linked histories of science',
        'STS.049': 'Cancer is, in the words of one recent author',
        'STS.088': 'The aim of this course is to immerse students',
    }
    if identity is None or identity[1] not in starts or starts[identity[1]] not in text:
        raise ValueError('STS archive exact subject or substantive description missing')
    term = re.search(r'\b(Fall|Spring) \d{4}\b', text)
    if term is None and identity[1] not in {'STS.011', 'STS.012'}:
        raise ValueError('STS archive teaching term missing')
    code = identity[1]
    name = identity[2].split(' – ')[0]
    if code == 'STS.086J':
        headings = [clean(h) for h in body.find_all('h2') if clean(h)]
        if headings != ['Cultures of Computing']:
            raise ValueError('STS computing actual subject title changed')
        name = headings[0]
    metadata = text.split(starts[code], 1)[0]
    units = re.search(r'\b\d+-\d+-\d+\b', metadata)
    prep = re.search(r'Prereq:\s*(None)\b', metadata)
    return [dict(code=code, name=name, term=term[0] if term else None,
                 description=starts[code]+text.split(starts[code],1)[1],
                 prerequisites=prep[1] if prep else None, units=units[0] if units else None,
                 source_text=text, source_heading=title)]


def observe_eecs_economics_annotations(html):
    """Read explicit department annotations; chart revision is not annotation edition."""
    soup = BeautifulSoup(html, 'html.parser')
    heading = clean(soup.find('h3'))
    if heading != 'Degree Requirements for 6-P14_2022 MNG in Computer Science, Economics, and Data Science':
        raise ValueError('EECS Economics chart context changed')
    codes = {'14.05','14.06','14.11','14.17','14.18','14.19','14.26','14.27','14.45','14.76','14.78'}
    observed = {}
    for block in soup.select('div.annotation'):
        title = clean(block.find('b'))
        match = re.fullmatch(r'(14\.\d+) (.+)', title)
        if match is None or match[1] not in codes:
            continue
        text = clean(block)
        prep = re.search(r'Prereqs:\s*(.*?)\s+Units:', text)
        units = re.search(r'Units:\s*(\d+-\d+-\d+)', text)
        description = ' '.join(clean(p) for p in block.find_all('p'))
        if prep is None or units is None or not description:
            raise ValueError('EECS Economics annotation description or metadata missing')
        row = dict(code=match[1], name=match[2], description=description,
                   prerequisites=prep[1], units=units[1], term=None,
                   chart_context=heading, source_text=text,
                   symbols=[i.get('src') for i in block.find_all('img')])
        if row['code'] in observed and observed[row['code']] != row:
            raise ValueError('Conflicting repeated Economics annotations: ' + row['code'])
        observed[row['code']] = row
    if set(observed) != codes:
        raise ValueError('Reviewed Economics annotation inventory changed')
    return list(observed.values())


def observe_anthropology_faculty(html):
    """Observe explicit teaching panels, keeping printed companions and unknown dates."""
    soup = BeautifulSoup(html, 'html.parser')
    faculty = clean(soup.find('h1'))
    heading = next((h for h in soup.find_all('h2') if clean(h) == 'Teaching'), None)
    if not faculty or heading is None:
        raise ValueError('Anthropology faculty teaching context missing')
    rows = []
    for node in heading.next_siblings:
        if getattr(node, 'name', None) == 'h2':
            break
        if getattr(node, 'name', None) != 'h4' or node.find('br') is None:
            continue
        lines = [clean(x) for x in node.get_text('\n', strip=True).split('\n') if clean(x)]
        label, title = lines[0], ' '.join(lines[1:])
        codes = re.findall(r'(?:21A|21G|24|STS|WGS|HST|11|15|17|7|4)\.\s*[A-Z]?\d+[A-Z]*', label)
        codes = [re.sub(r'\s+', '', code) for code in codes]
        paragraphs = []
        for sibling in node.next_siblings:
            if getattr(sibling, 'name', None) in {'h2', 'h4'}:
                break
            if getattr(sibling, 'name', None) == 'p' and clean(sibling):
                paragraphs.append(clean(sibling))
        if not codes or not title or not paragraphs:
            continue
        rows.append(dict(code=codes[0], name=title, description=' '.join(paragraphs),
                         prerequisites=None, units=None, term=None,
                         faculty=faculty, printed_code_label=label, offered_codes=codes,
                         source_heading=clean(node)))
    if not rows:
        raise ValueError('Anthropology teaching descriptions missing')
    return rows
