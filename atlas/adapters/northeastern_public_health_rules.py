"""Observe the two explicitly one-hour, home-aligned Public Health pools."""
from bs4 import BeautifulSoup
from atlas.adapters.northeastern_courseleaf import clean

PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-public-health-bs-boston-bs-degree'
POOLS = {
    'introduction-to-college': ('Introduction to College', ['CS 1200', 'HSCI 1000', 'INPR 1000']),
    'professional-development': ('Professional Development', ['CS 1210', 'HSCI 2000']),
}


def apply_home_aligned_choices(result, html):
    soup = BeautifulSoup(html, 'html.parser')
    heading = soup.select_one('#site-title h1')
    panel = soup.select_one('#programrequirementstextcontainer')
    if result.get('id') != PROGRAM_ID or not heading or clean(heading) != 'Artificial Intelligence and Public Health, BS (Boston)' or panel is None or '2026-2027' not in soup.get_text(' ', strip=True):
        raise ValueError('Expected Public Health degree and catalog version missing')
    rules = {r['id']: r for r in result['requirements']}
    selected = {}
    for tr in panel.select('tr'):
        comment = tr.select_one('.courselistcomment')
        if not comment or clean(comment) != 'Complete the following in alignment with your home college:':
            continue
        title_row = tr.find_previous_sibling('tr')
        title = clean(title_row) if title_row else ''
        match = next(((key, codes) for key, (label, codes) in POOLS.items() if title == label), None)
        hours = tr.select_one('.hourscol')
        if match is None or not hours or clean(hours) != '1':
            raise ValueError('Home-aligned section or one-hour requirement changed')
        key, codes = match
        if key in selected:
            raise ValueError('Duplicate home-aligned pool')
        observed = []
        for row in tr.find_next_siblings('tr'):
            links = row.select('a.code')
            if not links:
                break
            observed.extend(clean(link) for link in links)
        if observed != codes:
            raise ValueError('Home-aligned course pool changed')
        selected[key] = codes
    if set(selected) != set(POOLS):
        raise ValueError('Both home-aligned one-hour pools are required')
    for key, codes in selected.items():
        parent = PROGRAM_ID + '-req-' + key
        choice = parent + '-rule'
        rule = rules[choice]
        if rule['kind'] != 'note' or rule['parent_id'] != parent:
            raise ValueError('Expected uncorrected home-aligned condition node')
        members = [rules[PROGRAM_ID + '-req-' + code.lower().replace(' ', '-')] for code in codes]
        if any(r['parent_id'] != parent or r['kind'] != 'all' or r['course_ids'] != [PROGRAM_ID + '-' + code.lower().replace(' ', '-')] for r, code in zip(members, codes)):
            raise ValueError('Home-aligned original course ancestry changed')
        rule.update(kind='choose_credits', credits=1,
                    summary='Complete 1 semester hour from these courses in alignment with the student’s actual home college. The catalog does not assign that college or require all listed courses.')
        for member in members:
            member['parent_id'] = choice
    return result
