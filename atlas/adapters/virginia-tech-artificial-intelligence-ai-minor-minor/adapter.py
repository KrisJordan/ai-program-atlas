"""Actual local-minor observations; refresh never certifies completeness."""
from atlas.adapters.vt_duke_minors import parse_vt, policy_observation

PROGRAM_ID = 'virginia-tech-artificial-intelligence-ai-minor-minor'
SOURCE_ID = 'vt-ai-department'
SOURCES = ('https://website.cs.vt.edu/academic/undergraduate/ai-minor.html', 'https://eng.vt.edu/undergraduate/minors.html')

def parse(html: str) -> dict:
    return parse_vt(html, PROGRAM_ID, SOURCE_ID, SOURCES[0])

def parse_policy_0(html: str) -> dict:
    return policy_observation(html, PROGRAM_ID, 'vt-engineering-minors', 'vt')

SOURCE_PARSERS = {'https://eng.vt.edu/undergraduate/minors.html': parse_policy_0}


CHECKSHEETS_URL = 'https://www.registrar.vt.edu/graduation-multi-brief/checksheets.html'
SOURCES += (CHECKSHEETS_URL,)

def parse_catalog_authority(html):
    from atlas.adapters.national_curriculum_common import content, require_phrases, rule
    root = content(html, 'Checksheets are the legacy documents')
    require_phrases(root, ['For the 2024-2025 catalog year and beyond', 'University Catalog for all official course and programmatic curricula information', '2021-2023 degree requirements', 'top right of your DARS audit'])
    return dict(id=PROGRAM_ID, requirements=[rule('vt-ai-catalog-authority', 'Applicable curriculum source and catalog year', 'vt-ai-registrar-checksheets', kind='note', summary='The registrar directs catalog years 2024–25 onward to the University Catalog, while these legacy checksheets cover 2021–23 requirements. Confirm the applicable catalog year in DARS with an advisor. Historical checksheets do not verify this new minor’s current courses.')])

SOURCE_PARSERS[CHECKSHEETS_URL] = parse_catalog_authority
