"""Observe rendered RIT immersion tables for a named, separately reviewed route.

This observer preserves table rows and repeated course-code appearances, because
VIP credit accumulation and required/elective overlap are not duplicate courses.
It never manufactures a finite pool from prose or emits seed requirements/audits.
"""
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean


def parse(html, *, title, catalog_year='2026-2027'):
    soup = BeautifulSoup(html, 'html.parser')
    if soup.select('input[type="password"]'):
        raise ValueError('Login page is not curriculum evidence')
    main = soup.find('main')
    if not main or not any(clean(h.get_text(' ', strip=True)) == title for h in main.find_all('h1')):
        raise ValueError('Immersion identity missing')
    expected = 'Curriculum for ' + catalog_year + ' for ' + title
    if not any(clean(h.get_text(' ', strip=True)) == expected for h in main.find_all('h2')):
        raise ValueError('Rendered catalog version missing')
    tables = main.select('table.sc_courselist')
    if not tables:
        raise ValueError('HTTP shell lacks rendered curriculum tables')
    inventories = []
    for table in tables:
        rows = []
        for tr in table.select('tbody tr'):
            codes = [clean(c.get_text(' ', strip=True)) for c in tr.select('.code_bubble')]
            if any(not re.fullmatch(r'[A-Z]+(?:/[A-Z]+)*-\d+[A-Z]?', c) for c in codes):
                raise ValueError('Unrecognized exact course code')
            cells = [clean(c.get_text(' ', strip=True)) for c in tr.find_all(['td','th'])]
            if cells:
                rows.append({'course_codes': codes, 'cells': cells})
        if not rows:
            raise ValueError('Empty curriculum table')
        inventories.append({'rows': rows})
    return {'observed_title': title, 'observed_catalog_year': catalog_year,
            'observed_tables': inventories,
            'observed_policy_text': clean(main.get_text(' ', strip=True)),
            'requirements': [], 'courses': []}
