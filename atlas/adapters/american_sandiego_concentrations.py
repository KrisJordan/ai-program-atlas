"""Visible catalog HTML observations, including manually rendered public pages.

No browser automation or hidden Coursedog/Acalog data is consumed here. A shell
without the actual visible requirement section fails, rather than replaying seeds.
"""
import hashlib
import re

from bs4 import BeautifulSoup

from atlas.adapters.reviewed_minors_2026 import clean, slug
from atlas.adapters.vt_duke_minors import rule


def _course(prefix, code, name, credits, unit, source, url):
    return dict(id=prefix+'-'+slug(code), code=code, name=name,
                description=None, prerequisites=None, credits=credits,
                credit_unit=unit, category='ai_ml', source_id=source, url=url,
                public_site=None, syllabus=None)


def _observation(pid, text, courses, requirements):
    return dict(id=pid, program_kind='concentration', award_level='concentration',
                curriculum_status='partial', courses=courses, requirements=requirements,
                observed_policy_digest=hashlib.sha256(text.encode()).hexdigest())


def parse_american(html, pid, source, url):
    soup = BeautifulSoup(html, 'html.parser')
    identity = soup.find(class_='acalog-program-name')
    heading = next((h for h in soup.find_all('h3')
                    if re.fullmatch(r'Concentration \(\d+ credit hours\)', clean(h.get_text()))), None)
    ai = next((h for h in soup.find_all('h4') if clean(h.get_text()) == 'Artificial Intelligence'), None)
    if not identity or clean(identity.get_text()) != 'Computer Science (BS)' or not heading or not ai:
        raise ValueError('American BS concentration identity/visible section missing')
    # AI must occur inside this concentration group, not an unrelated elective bucket.
    if ai.find_parent(class_='acalog-program-core') not in heading.parent.find_all(class_='acalog-program-core'):
        raise ValueError('American AI section is not a concentration child')
    section = ai.parent
    policy = section.find(class_='acalog-program-core-description')
    text = clean(policy.get_text(' ', strip=True)) if policy else ''
    total = re.fullmatch(r'Complete (\d+) credit hours from the following if not taken to fulfill Breadth of Knowledge:', text)
    if not total or int(total[1]) != int(re.search(r'\d+', heading.get_text())[0]):
        raise ValueError('American selection/overlap rule changed; review required')
    courses = []
    for anchor in section.find_all('a', class_='acalog-program-core-course-link'):
        m = re.fullmatch(r'(CSC-\d+[A-Z]*) (.+) \((\d+(?:\.\d+)?)\)', clean(anchor.get_text()))
        if not m or not anchor.get('href', '').startswith('https://catalog.american.edu/'):
            raise ValueError('American course row/link changed')
        courses.append(_course('american', m[1], m[2], float(m[3]), 'unknown', source, anchor['href']))
    if not courses or len({c['id'] for c in courses}) != len(courses):
        raise ValueError('American empty/duplicate course pool')
    req = [rule('american-ai-local', 'Artificial Intelligence concentration within Computer Science BS', source, kind='all'),
           rule('american-ai-choice', 'Concentration selections; no Breadth of Knowledge reuse', source,
                kind='note', parent='american-ai-local', credits=int(total[1]),
                ids=[c['id'] for c in courses], summary=text)]
    for label, key in [('Admission to the Program', 'admission'), ('Major Requirements', 'major-context')]:
        h = next((h for h in soup.find_all(class_='acalog-program-core-name') if clean(h.get_text()) == label), None)
        body = h.parent.find(class_='acalog-program-core-description') if h else None
        if not body:
            raise ValueError('American '+label+' policy context missing')
        req.append(rule('american-ai-'+key, label+' (host major context)', source,
                        parent='american-ai-local', summary=clean(body.get_text(' ', strip=True))))
    return _observation(pid, ' '.join(r['summary'] for r in req), courses, req)


def parse_sandiego(html, pid, source, url, award):
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find('main') or soup
    heading = soup.find('h1')
    if award not in ('BA', 'BS') or not heading or clean(heading.get_text()) != 'Computer Science '+award:
        raise ValueError('USD concrete host award identity missing/mismatched')
    context = next((h for h in soup.find_all('h3') if clean(h.get_text()).startswith('Concentrations in Computer Science (')), None)
    policy = context.find_next_sibling('p') if context else None
    text = clean(policy.get_text(' ', strip=True)) if policy else ''
    if not all(s in text for s in ['Courses taken toward a concentration may also apply', 'Concentrations are optional']):
        raise ValueError('USD concentration overlap/optional policy changed')
    tables = [t for t in soup.find_all('table') if t.find('tr') and
              clean(t.find('tr').get_text(' ', strip=True)) == 'Concentration in Data Science and Artificial Intelligence']
    if len(tables) != 1:
        raise ValueError('USD AI concentration table missing/ambiguous')
    courses, core, options = [], [], []
    choice_units = total = None
    in_choice = False
    rows = tables[0].find_all('tr')[1:]
    for row in rows:
        cells = [clean(c.get_text(' ', strip=True)) for c in row.find_all('td', recursive=False)]
        if not cells:
            continue
        if cells[0] == 'One of the following courses:':
            if in_choice or len(cells) != 2 or not re.fullmatch(r'\d+(?:\.\d+)?', cells[1]):
                raise ValueError('USD option group changed')
            in_choice, choice_units = True, float(cells[1])
        elif cells[0] == 'Total Units':
            if total is not None or len(cells) != 2 or not re.fullmatch(r'\d+(?:\.\d+)?', cells[1]):
                raise ValueError('USD total row changed')
            total = float(cells[1])
        elif len(cells) == 3 and re.fullmatch(r'[A-Z]+ \d+[A-Z]*', cells[0]) and cells[1]:
            if total is not None or (cells[2] and not re.fullmatch(r'\d+(?:\.\d+)?', cells[2])):
                raise ValueError('USD course credit/position changed')
            c = _course('sandiego', cells[0], cells[1], float(cells[2]) if cells[2] else None, 'units', source, url)
            # Reviewed exact identities; an unfamiliar course is not automatically
            # classified as AI just because it appears in this elective pool.
            c['category'] = {'COMP 351': 'ai_ml', 'COMP 352': 'foundations',
                             'COMP 333': 'applications', 'COMP 380': 'ai_ml',
                             'COMP 382': 'ai_ml', 'GENG 430': 'applications'}.get(cells[0], 'other')
            courses.append(c)
            (options if in_choice else core).append(c['id'])
        else:
            raise ValueError('Unrecognized USD concentration row: '+str(cells))
    if not core or not options or total is None or choice_units is None or len({c['id'] for c in courses}) != len(courses):
        raise ValueError('USD requirement inventory incomplete')
    known_core = [c['credits'] for c in courses if c['id'] in core]
    if any(v is None for v in known_core) or sum(known_core)+choice_units != total:
        raise ValueError('USD component and total units disagree')
    req = [rule('sandiego-ai-local', 'Data Science and Artificial Intelligence concentration within Computer Science '+award,
                source, kind='all', credits=total, unit='units'),
           rule('sandiego-ai-core', 'Required concentration courses', source, kind='all',
                parent='sandiego-ai-local', ids=core, unit='units'),
           rule('sandiego-ai-option', 'One concentration elective', source, kind='choose_courses', number=1,
                parent='sandiego-ai-local', credits=choice_units, unit='units', ids=options,
                summary='Choose one listed option for the stated group units; blank individual course credits remain unverified.'),
           rule('sandiego-ai-policy', 'Optional concentration and host-major overlap', source,
                parent='sandiego-ai-local', summary=text)]
    return _observation(pid, text+' '+clean(tables[0].get_text(' ', strip=True)), courses, req)
