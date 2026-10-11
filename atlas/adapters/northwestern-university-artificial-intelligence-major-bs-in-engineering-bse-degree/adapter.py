"""Source-specific AI major curriculum observations; degree-wide coverage is partial."""
from atlas.adapters.northwestern_ai_degree import parse_northwestern

PROGRAM_ID = 'northwestern-university-artificial-intelligence-major-bs-in-engineering-bse-degree'
SOURCES = ('https://catalogs.northwestern.edu/undergraduate/engineering-applied-science/artificial-intelligence/artificial-intelligence-major/',)

def parse(html):
    return parse_northwestern(html, PROGRAM_ID, SOURCES[0])

from atlas.adapters import northwestern_degree_policies as policies

parse_original = parse

def parse(html):
    result = parse_original(html)
    extra = policies.parse_major_exceptions(html, SOURCES[0])
    known = {c['id'] for c in result['courses']}
    result['courses'].extend(c for c in extra['courses'] if c['id'] not in known)
    result['requirements'].extend(extra['requirements'])
    return result

SOURCES += (policies.COLLEGE_URL, policies.URR_URL, policies.THEME_URL, policies.FAQ_URL,
            policies.REGISTRATION_URL, policies.TRANSFER_URL, policies.PN_URL,
            policies.DUPLICATES_URL, policies.REGISTRAR_TRANSFER_URL, policies.PN_PDF_URL)
SOURCE_PARSERS = {SOURCES[0]: parse, policies.COLLEGE_URL: policies.parse_college,
                  policies.URR_URL: policies.parse_urr, policies.THEME_URL: policies.parse_theme,
                  policies.DUPLICATES_URL: policies.parse_duplicate_sets,
                  policies.REGISTRAR_TRANSFER_URL: policies.parse_registrar_transfer}
for _key, _url in [('theme-faq', policies.FAQ_URL), ('registration', policies.REGISTRATION_URL),
                   ('transfer-public', policies.TRANSFER_URL), ('pn-public', policies.PN_URL)]:
    SOURCE_PARSERS[_url] = lambda html, key=_key: policies.parse_public(html, key)

from atlas.adapters import northwestern_degree_courses
SOURCES = northwestern_degree_courses.register(PROGRAM_ID, SOURCES, SOURCE_PARSERS)

from atlas.adapters import northwestern_degree_metadata
SOURCES = northwestern_degree_metadata.register(PROGRAM_ID, SOURCES, SOURCE_PARSERS)
