"""Observers for public AU regulations and USD rendered policy tabs.

These expose selected published clauses as review candidates. Curated notes are
separately paraphrased; observing a policy never certifies a curriculum audit.
"""
import hashlib
import re

from bs4 import BeautifulSoup

from atlas.adapters.reviewed_minors_2026 import clean
from atlas.adapters.vt_duke_minors import rule

AU_SECTIONS = ('1. Credit Hours', '7.1. In-Residence Courses',
               '7.2. Study at Another Institution',
               '7.3. Permit to Study at an International Institution',
               '9.1. Minimum Requirements for Majors',
               '9.3. Declaration of Majors and Minors',
               '9.4. Changes in Major, Academic Unit Affiliation', '9.6. Double Majors')


def _sections(soup, names):
    result = {}
    for name in names:
        h = next((h for h in soup.find_all(['h2', 'h3']) if clean(h.get_text()) == name), None)
        if h is None:
            raise ValueError('Policy section missing: '+name)
        parts = []
        for tag in h.next_siblings:
            if getattr(tag, 'name', None) in ('h1', 'h2', 'h3'):
                break
            if getattr(tag, 'get_text', None):
                parts.append(clean(tag.get_text(' ', strip=True)))
        result[name] = ' '.join(parts)
        if not result[name]:
            raise ValueError('Policy section empty: '+name)
    return result


def _result(pid, clauses, source, unit=None):
    text = '\n'.join(clauses.values())
    return dict(id=pid, program_kind='concentration', curriculum_status='partial',
                courses=[], requirements=[rule(key, title, source, summary=value)
                for (key, title), value in clauses.items()],
                observed_policy_digest=hashlib.sha256(text.encode()).hexdigest(),
                observed_credit_unit=unit)


def parse_american_regulations(html, pid, source):
    soup = BeautifulSoup(html, 'html.parser')
    if not any('Undergraduate Academic Rules and Regulations' in h.get_text() for h in soup.find_all(['h1', 'h2'])):
        raise ValueError('American current regulation identity missing')
    parts = _sections(soup, AU_SECTIONS)
    credit = parts[AU_SECTIONS[0]]
    if 'credit hour' not in credit or not re.search(r'fifteen-week semester|15-week semester', credit):
        raise ValueError('American semester credit definition changed')
    major = parts['9.1. Minimum Requirements for Majors']
    if not all(t in major for t in ['in-residence', 'Pass/Fail', '9.1.1.e.']):
        raise ValueError('American major grading/residence clauses missing')
    # Numeric values are retained from the observed text; changed rules are not
    # replaced with hard-coded thresholds from the existing curated record.
    clauses = {(f'american-policy-{i}', name): value for i, (name, value) in enumerate(parts.items())}
    return _result(pid, clauses, source, 'semester_hours')


def parse_american_declaration(html, pid, source):
    soup = BeautifulSoup(html, 'html.parser')
    if not any('Declaring a Major' in h.get_text() for h in soup.find_all(['h1', 'h2'])):
        raise ValueError('American CAS declaration heading missing')
    headings = ('First Major', 'Second Major')
    parts = _sections(soup, headings)
    if any('GPA' not in text for text in parts.values()) or 'first/primary major declared' not in parts['Second Major']:
        raise ValueError('American CAS declaration conditions missing')
    introductions = [clean(p.get_text(' ', strip=True)) for p in soup.find_all('p')
                     if 'semester' in p.get_text() and 'GPA' in p.get_text()]
    if not introductions:
        raise ValueError('American CAS introductory declaration eligibility missing')
    parts['Introductory declaration eligibility'] = ' '.join(dict.fromkeys(introductions))
    return _result(pid, {('american-cas-'+str(i), name): value for i, (name, value) in enumerate(parts.items())}, source)


USD_TABS = {
    'credit': ('Academic Regulations', 'Credit Hour Policy'),
    'grading': ('Academic Regulations', 'Credit and Grading System'),
    'declaration': ('Academic Regulations', 'Declaring the Major'),
    'residence': ('Academic Regulations', 'Residence Requirement'),
    'major-grades': ('Academic Programs', "General Requirements for Bachelor's Degree"),
    'overlap': ('Academic Programs', 'Requirements for Major and Minor'),
    'school': ('Shiley-Marcos School of Engineering', 'Requirements'),
}


def parse_usd_policy(html, pid, source, kind):
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('main') or soup
    h = main.find('h1')
    tab = main.find(attrs={'role': 'tab', 'aria-selected': 'true'})
    panel = main.find(attrs={'role': 'tabpanel'})
    page, label = USD_TABS[kind]
    if not h or clean(h.get_text()) != page or not tab or clean(tab.get_text()) != label or not panel:
        raise ValueError('USD policy page/active tab identity missing')
    text = clean(panel.get_text(' ', strip=True))
    if kind == 'credit':
        parts = _sections(panel, ('Standard Undergraduate Courses',))
        if 'One unit of credit' not in parts['Standard Undergraduate Courses'] or 'one semester' not in parts['Standard Undergraduate Courses']:
            raise ValueError('USD semester unit definition changed')
    elif kind == 'school':
        parts = _sections(panel, ('Special Restrictions on the Use of the Pass/Fail Option', 'Residency Requirement'))
        if 'Computer Science degrees' not in parts['Residency Requirement']:
            raise ValueError('USD computer science residence distinction missing')
    elif kind == 'grading':
        parts = _sections(panel, ('Transfer of Credit', 'Pass/Fail Option', 'Duplication of Credit'))
        if not all(t in parts['Transfer of Credit'] for t in ['C-', 'major or minor', '18 units', 'Covid']):
            # The numeric ceiling is reviewed rather than inferred if its source
            # wording changes. This conservative guard does not hide the change.
            raise ValueError('USD transfer policy structure changed; review required')
    elif kind == 'overlap':
        parts = _sections(panel, ('Majors', 'Minors'))
    else:
        markers = {'declaration': ('April 15', 'appropriate processes'),
                   'residence': ('final', 'semester units', 'dean'),
                   'major-grades': ('upper-division courses in the major', 'C– or better')}
        if not all(t in text for t in markers[kind]):
            raise ValueError('USD '+kind+' policy clauses missing')
        if kind == 'major-grades':
            items = [clean(t.get_text(' ', strip=True)) for t in panel.find_all(['li', 'p'])]
            relevant = [t for t in items if 'upper-division courses in the major' in t]
            if not relevant:
                raise ValueError('USD major GPA clause missing')
            parts = {'Host-major grades': ' '.join(dict.fromkeys(relevant))}
        else:
            parts = {label: text}
    return _result(pid, {(f'sandiego-policy-{kind}-{i}', name): value for i, (name, value) in enumerate(parts.items())},
                   source, 'semester_hours' if kind == 'credit' else None)
