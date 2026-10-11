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
