"""Scoped CourseLeaf requirement observations for reviewed Northeastern BS pages.

No seed files are read. Major tables are observed; external graduation policies,
open course ranges and conditional substitutions remain explicitly partial.
"""
from __future__ import annotations

import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def clean(value):
    return re.sub(r'\s+', ' ', value.get_text(' ', strip=True) if hasattr(value, 'get_text') else value).strip()


def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')


def category(code, name):
    """Editorial taxonomy, not a university designation."""
    subject = code.split()[0]
    if subject in {'MATH', 'ECON', 'MGSC'} or 'Statistics' in name: return 'mathematics'
    if subject in {'PHIL', 'POLS', 'AFCS', 'ENGW'}: return 'human_context'
    if any(x in name.lower() for x in ('machine learning', 'neural network', 'artificial intelligence')): return 'ai_ml'
    if subject in {'CS', 'DS'}:
        return 'systems' if any(x in name.lower() for x in ('database', 'storage', 'retrieval')) else 'foundations'
    if subject in {'BIOL', 'CHEM', 'EEMB', 'BINF', 'MKTG', 'ACCT', 'FINA', 'ORGB', 'INTB', 'INNO', 'MISM', 'SCHM', 'STRT'}: return 'applications'
    return 'other'


def numeric(text):
    return float(text) if re.fullmatch(r'\d+(?:\.\d+)?', text) else None


def summarize_rule(text):
    """Keep concise rule facts; do not reproduce explanatory catalog paragraphs."""
    if 'self-assessment' in text:
        match = re.search(r'(\d+\s*-\s*\d+) semester hours?', text)
        if not match or '3000' not in text: raise ValueError('Changed placement substitution requires review')
        return f'Placement may replace CS 2000/2001 with {match[1]} semester hours of otherwise unused CS/CY/DS courses at level 3000 or above.'
    if text.startswith('With advisor approval'):
        return 'Advisor approval can allow directed study, research, projects and suitable graduate courses in upper-division electives.'
    if 'home college' in text: return 'Seminar and professional-development choices depend on the home college.'
    if text.startswith('Complete all courses'): return 'Required courses include specified corequisites; additional credits may be needed to reach the degree minimum.'
    if 'All undergraduate students' in text: return 'Separate university policy applies; its full requirements are not expanded here.'
    if 'Marketing Analytics concentration' in text: return 'Selecting Marketing Analytics also requires an additional general elective.'
    if 'Integrating Knowledge' in text: return 'Co-op fulfills the experiential NUpath category.'
    return re.sub(r'^Complete\s+', 'Required: ', text)


def parse_catalog(html, *, program_id, title, url, required_sections, outcome_claims=()):
    soup = BeautifulSoup(html, 'html.parser')
    heading = soup.find(id='site-title')
    h1 = heading.find('h1') if heading else None
    if not h1 or clean(h1) != title: raise ValueError('Expected program-specific catalog heading missing')
    panel = soup.find(id='programrequirementstextcontainer')
    if not panel: raise ValueError('Program requirements panel missing')
    if 'semester hours' not in clean(panel) or 'quarter hours' in clean(panel):
        raise ValueError('Expected explicit semester-hour unit missing or changed')
    for marker in panel.find_all('sup'):
        marker.decompose()
    headings = {clean(x) for x in panel.find_all('h2')}
    if not set(required_sections) <= headings: raise ValueError('Expected curriculum sections missing')
    year = re.search(r'Academic Catalog\s+(20\d{2})[–-](\d{2,4})', clean(soup))
    catalog_year = f'{year[1]}-{year[2]}' if year else None
    sid = program_id + '-catalog'
    courses, rules, ids = {}, [], set()

    def rule(label, parent=None, kind='all', credits=None, count=None, summary='', course_ids=None):
        base = program_id + '-req-' + slug(label)
        rid, n = base, 2
        while rid in ids:
            rid = f'{base}-{n}'; n += 1
        ids.add(rid)
        value = dict(id=rid, parent_id=parent, title=label, kind=kind, count=count,
                     credits=credits, credit_unit='semester_hours', category='other', source_id=sid,
                     source_text=None, summary=summary, course_ids=course_ids or [])
        rules.append(value)
        return value

    root = rule('Published program requirements', summary='Major-page requirements; external policies and open elective inventories remain partial.')
    section = root
    for element in panel.find_all(['h2', 'table', 'p', 'ul', 'dl'], recursive=False):
        if element.name == 'h2':
            section = rule(clean(element), root['id']); continue
        if element.name in {'p', 'ul', 'dl'}:
            text = clean(element)
            if text:
                # Preserve only concise policy facts, not NUpath marketing descriptions.
                summary = ('Catalog lists NUpath categories fulfilled by the major; applicability must be checked against the separate NUpath policy.'
                           if section['title'] == 'NUpath Requirements Satisfied' and element.name == 'ul'
                           else ('Choose a business concentration from the linked catalog options; individual concentration curricula remain unexpanded.'
                                 if section['title'] == 'Business Concentration' and element.name == 'ul' else summarize_rule(text)))
                rule(section['title'] + ' policy', section['id'], kind='note', summary=summary)
            continue
        if 'sc_courselist' not in element.get('class', []): continue
        area, parent, previous, choice = section, section, None, None
        option_choice = None
        for row in element.find_all('tr'):
            cells = row.find_all('td', recursive=False)
            if not cells: continue
            classes = row.get('class', [])
            text = clean(cells[0])
            hours = row.find('td', class_='hourscol')
            hour_text = clean(hours) if hours else ''
            credit = numeric(hour_text)
            if hour_text and credit is None and not re.fullmatch(r'\d+\s*[-–]\s*\d+', hour_text):
                raise ValueError('Unrecognized credit expression')
            range_note = f' Published row range: {hour_text} semester hours.' if hour_text and credit is None else ''
            if 'listsum' in classes:
                rule(section['title'] + ' published subtotal', section['id'], kind='note', credits=credit,
                     summary='Published section subtotal; overlapping courses and choices are not summed by this parser.')
                continue
            if 'areaheader' in classes:
                area = rule(text, (option_choice or section)['id']); parent, previous, choice = area, None, None; continue
            if 'areasubheader' in classes:
                if choice:
                    rule(text, choice['id'], kind='note', summary='Subgroup within the preceding elective choice.'); continue
                parent = rule(text, area['id']); previous = None; continue
            codecell = row.find('td', class_='codecol')
            if codecell is None:
                number = re.search(r'(?:Complete|Choose)\s+(?:at least\s+)?(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b', text, re.I)
                unitmatch = re.search(r'(one|two|three|four|five|six|seven|eight|nine|ten|\d+) semester hours', text, re.I)
                numbers = dict(one=1,two=2,three=3,four=4,five=5,six=6,seven=7,eight=8,nine=9,ten=10)
                amount = (numbers.get(unitmatch[1].lower(), int(unitmatch[1]) if unitmatch[1].isdigit() else None) if unitmatch else None)
                if unitmatch and text.startswith('Complete'):
                    if credit is not None and credit != amount:
                        raise ValueError('Conflicting credit-choice amounts')
                    choice = rule(area['title'] + ' credit choice', parent['id'], 'choose_credits', credits=amount, summary=summarize_rule(text) + range_note)
                elif number:
                    word = number[1].lower(); count = numbers.get(word, int(word) if word.isdigit() else None)
                    # A course+lab combination is one alternative, not two independently selectable courses.
                    bundled = 'corresponding lab' in text or 'following options' in text and count == 1
                    choice = rule(area['title'] + ' course choice', parent['id'], 'alternative' if bundled else 'choose_courses', credits=credit, count=None if bundled else count, summary=summarize_rule(text) + range_note)
                    if 'following options' in text and count == 1:
                        option_choice = choice
                else:
                    if text.startswith(('Complete', 'Choose')) and any(word in text for word in ('following', 'courses', 'semester hours')) and 'home college' not in text:
                        raise ValueError('Unsupported choice count requires review')
                    rule(area['title'] + ' rule', (choice or parent)['id'], kind='note', summary=summarize_rule(text) + range_note)
                previous = None; continue
            links = codecell.find_all('a', class_='code')
            if not links or len(cells) < 2: raise ValueError('Unrecognized course row')
            codes = [clean(a) for a in links]
            if choice and choice['kind'] == 'choose_courses' and choice['count'] == 1 and len(codes) > 1:
                choice['kind'], choice['count'] = 'alternative', None
            if any(not re.fullmatch(r'[A-Z]+ \d+[A-Z]?', x) for x in codes): raise ValueError('Unrecognized course code')
            titlecell = BeautifulSoup(str(cells[1]), 'html.parser')
            for br in titlecell.find_all('br'):
                br.replace_with('|||')
            names = [clean(x) for x in titlecell.get_text(' ', strip=True).split('|||') if clean(x)]
            names = [re.sub(r'^and\s+', '', x) for x in names]
            if len(codes) > 1 and len(names) != len(codes): raise ValueError('Course bundle titles changed')
            course_ids, annotations = [], []
            for index, code in enumerate(codes):
                name = names[index] if len(codes) > 1 else clean(cells[1])
                # Parenthetical concurrency instructions are rule evidence, not the course title.
                if '(' in name:
                    base, annotation = name.split('(', 1)
                    annotations.append((code, annotation.rstrip(')')))
                    name = base.strip()
                cid = program_id + '-' + slug(code)
                course_ids.append(cid)
                observed_credit = credit if len(codes) == 1 else None
                if cid not in courses:
                    courses[cid] = dict(id=cid, code=code, name=name, description=None, prerequisites=None,
                        credits=observed_credit, credit_unit='semester_hours', category=category(code, name),
                        source_id=sid, url=urljoin(url, links[index]['href']), public_site=None, syllabus=None)
                elif observed_credit is not None:
                    old = courses[cid]['credits']
                    if old is not None and old != observed_credit: raise ValueError('Conflicting course credits')
                    courses[cid]['credits'] = observed_credit
            rowparent = choice or parent
            if 'orclass' in classes:
                if previous is None: raise ValueError('Or row without preceding requirement')
                if previous['kind'] != 'alternative':
                    alt = rule(' / '.join(courses[x]['code'] for x in previous['course_ids']) + ' alternatives', previous['parent_id'], 'alternative', summary='Choose one listed course or course bundle.')
                    previous['parent_id'] = alt['id']; previous = alt
                rowparent = previous
            item = rule(' + '.join(codes), rowparent['id'], credits=credit, course_ids=course_ids,
                        summary=('Take this course bundle together.' if len(codes)>1 else 'Listed course.') + range_note)
            for code, annotation in annotations:
                rule(code + ' condition', item['id'], kind='note', summary=annotation)
                concurrent = re.search(r'concurrent with ([A-Z]+ \d+) or ([A-Z]+ \d+)', annotation)
                if concurrent:
                    related = [program_id + '-' + slug(value) for value in concurrent.groups()]
                    if all(cid in courses for cid in related):
                        alternative = rule(code + ' concurrent research', item['id'], 'alternative', summary='Take one of these research courses concurrently with this capstone.')
                        for cid in related:
                            rule(code + ' concurrent ' + courses[cid]['code'], alternative['id'], course_ids=[cid], summary='Concurrent research option.')
            if 'orclass' not in classes: previous = item
    if not courses: raise ValueError('No scoped curriculum courses found')
    overview = soup.find(id='textcontainer')
    overview_text = clean(overview) if overview else ''
    outcomes = [dict(text=summary, kind='source_stated', source_id=sid, locator='Program overview')
                for phrase, summary in outcome_claims if phrase in overview_text]
    return dict(id=program_id, title=title, award_level='BS', program_kind='degree',
                catalog_year=catalog_year, curriculum_status='partial', courses=list(courses.values()),
                requirements=rules, outcomes=outcomes)
