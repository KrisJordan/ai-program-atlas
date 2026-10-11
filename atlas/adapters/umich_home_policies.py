"""Conditional home-college observations for Michigan HCAI.

Only Ross accepts raw HTML. Other functions accept manually reviewed public-reader
or PDF text, never an HTTP denial, login page or PDF bytes. Pinned observations
fail closed when text changes. They do not certify complete home-college coverage.
"""
import hashlib
import re
from atlas.adapters.national_curriculum_common import clean, content, rule

PROGRAM_ID = 'university-of-michigan-ann-arbor-human-centered-artificial-intelligence-minor-minor'

SOURCE_INFO = {'ross': {'id': 'umich-hcai-home-ross', 'url': 'https://rossweb.bus.umich.edu/academics/dual-degrees-minors-special-programs/bba-minors/', 'title': 'BBA Minors', 'catalog_year': None, 'locator': 'BBA minor eligibility, credit sharing and declaration/release', 'input_format': 'html', 'source_date': None}, 'ross-bulletin': {'id': 'umich-hcai-home-ross-bulletin', 'url': 'https://rossweb.bus.umich.edu/academics/wp-content/uploads/sites/2/2026/09/bbabulletin-2026-2027.pdf', 'title': 'Ross BBA Student Bulletin 2026–2027', 'catalog_year': '2026-2027', 'locator': 'Printed pp.25–27, Minors Available to BBA Students and Credit Sharing; printed August 2026', 'input_format': 'reviewed_pdf_text', 'source_date': None}, 'ford': {'id': 'umich-hcai-home-ford', 'url': 'https://fordschool.umich.edu/ba/faqs', 'title': 'BA FAQs', 'catalog_year': None, 'locator': 'Can I pursue a minor?; Can I pursue a dual-degree?; What is the process for completing a minor?', 'input_format': 'reviewed_public_reader', 'source_date': None}, 'kinesiology': {'id': 'umich-hcai-home-kinesiology', 'url': 'https://www.kines.umich.edu/sites/default/files/2026-04/2025-2026%20Undergraduate%20Bulletin.pdf', 'title': 'Kinesiology Undergraduate Bulletin 2025–2026', 'catalog_year': '2025-2026', 'locator': 'Printed p.39, Academic Minors', 'input_format': 'reviewed_pdf_text', 'source_date': None}, 'stamps': {'id': 'umich-hcai-home-stamps', 'url': 'https://stamps.umich.edu/undergraduate-programs/minors-for-stamps-students', 'title': 'Minors for Stamps Students', 'catalog_year': None, 'locator': 'Eligibility and Steps in Pursuing a Minor', 'input_format': 'reviewed_public_reader', 'source_date': None}, 'public-health': {'id': 'umich-hcai-home-public-health', 'url': 'https://sph.umich.edu/undergrad/faqs.html', 'title': 'Undergraduate Program FAQs', 'catalog_year': None, 'locator': 'Can I pursue a minor?', 'input_format': 'reviewed_public_reader', 'source_date': None}}

SOURCES = [s["url"] for s in SOURCE_INFO.values()]

POLICIES = {'ross': [('eligibility', 'Ross BBA students: approved minors', 'Ross explicitly lists HCAI as an approved minor. Individually designed minors are unavailable; multiple minors are allowed when they are not in the same department or program. Students need the minor requirements, not the other school’s entire degree curriculum.'), ('overlap', 'Ross BBA students: business-credit overlap', 'Required BBA business credits may be shared with only one minor. For HCAI, at most three of those business credits may be shared; this is not a blanket cap on all nonbusiness coursework. No courses may be shared between multiple minors.'), ('planning', 'Ross BBA students: advisor planning', 'Coordinate a minor plan with the minor advisor and the Ross advisor. Courses exceeding three credits need careful allocation under the sharing limit; the dated BBA bulletin supplies the partial-credit procedure.'), ('release', 'Ross BBA students: declaration and release', 'Declare through the host department and have the declaration recorded by the Ross Registrar. Declaration and the host department’s minor release must reach Ross before the end of the final term. Exceptions to the approved plan require documentation.')], 'ross-bulletin': [('allocation', 'Ross BBA students: 2026–27 partial-credit procedure', 'The 2026–27 bulletin illustrates a four-credit course used in a minor: either take an additional business credit beyond the applicable BBA minimum to offset excess overlap, or obtain written confirmation that the minor will apply only three credits. This does not establish that HCAI accepts partial-course credit. An unverified minor at final audit requires dropping the minor or postponing graduation.')], 'ford': [('overlap', 'Ford BA students: focus-area overlap', 'Up to two courses used for a U-M minor may also satisfy the public-policy focus area. This is a focus-area rule, not a verified blanket allowance for sharing with every public-policy major requirement. More than one minor is allowed when graduation remains on track; the FAQ does not permit a dual degree.'), ('process', 'Ford BA students: declaration process', 'Follow the minor’s home department instructions. Contact the Ford Registrar when minor classes do not display correctly in Wolverine Access. Relevant minor courses may also serve the focus area, subject to the two-course limit.')], 'kinesiology': [('overlap', 'Kinesiology students: 2025–26 major overlap', 'The 2025–26 bulletin permits only one course in common between major requirements and a minor. Distribution courses can also count toward a minor when they are not also major requirements. Movement Science cognates count as electives and can overlap with a minor unless also used for a required Movement Science class. Applicability to later bulletin cohorts is unverified.'), ('planning', 'Kinesiology students: 2025–26 advising', 'Consult both the minor unit’s advisor and a Kinesiology advisor about fitting an outside-unit minor into the major curriculum. HCAI eligibility comes from its separate UMSI handbook; this older bulletin’s examples do not independently list HCAI.')], 'stamps': [('eligibility', 'Stamps students: outside-unit minors', 'Stamps permits minors offered by any U-M Ann Arbor school or college. Follow each minor’s own prerequisites, required courses and electives, and discuss degree progress with both advisors. The page’s typical minor-credit range is not an HCAI requirement.'), ('release', 'Stamps students: declaration and release', 'The minor advisor must notify Stamps of the declaration. One semester before graduation, have the minor advisor submit a release to Stamps; failure to submit may prevent the minor from appearing at graduation.')], 'public-health': [('eligibility', 'Public Health students: outside-unit minor eligibility', 'The undergraduate FAQ explicitly includes Information among the units through which Public Health students may pursue a minor. It does not establish a course-sharing limit or general minor residence rule.')]}

def normalize(text):
    return clean(re.sub(r"\bL\d+:\s*", "", text))


def ross_text(html):
    root = content(html, 'BBA Minors')
    text = normalize(root.get_text(' ', strip=True))
    start = text.find('BBA students may pursue academic minors')
    end = text.find('Other Questions?', start)
    if start < 0 or end < 0:
        raise ValueError('Ross minor policy boundaries missing')
    return normalize(text[start:end])


REVIEWED_HASHES = {'ross-bulletin': 'c668adb3cbf9866e0d70527f74be1f5c1d5cee4c7b4bec3066376a271b174409', 'ford': '01a4ae13da408aed34232631f32d74ae468c69e5ccf63cfb1bd576c2caf9fbb8', 'kinesiology': '3f51900546eb8431263a558767ffe1e5dbbe7fe4ec152f925aed81d6ee0af93e', 'stamps': 'e56fd09ff2410bf9240a47180e2a47d6114dcd2390afc02579cf7ea5415de7ab', 'public-health': '816ce0ac958920d8c4c297747edb4994e6e3b8bdac0efff948a3b76fd2e87c50', 'ross': 'eaf3776cc191258da1d9f4dd21bbe9187e090921c3c16bbb9b2cc2ead18eb247'}

def _observe(key, text):
    if hashlib.sha256(normalize(text).encode()).hexdigest() != REVIEWED_HASHES[key]:
        raise ValueError(f'{key} policy text changed or unavailable; source review required')
    sid = SOURCE_INFO[key]['id']
    return dict(id=PROGRAM_ID, requirements=[
        rule('umich-hcai-home-'+key+'-'+suffix, title, sid,
             parent='umich-hcai-root', kind='note', summary=summary)
        for suffix, title, summary in POLICIES[key]
    ])


def parse(html):
    return _observe('ross', ross_text(html))


def parse_ross_bulletin_reviewed(text):
    return _observe('ross-bulletin', text)


def parse_ford_reviewed(text):
    return _observe('ford', text)


def parse_kinesiology_reviewed(text):
    return _observe('kinesiology', text)


def parse_stamps_reviewed(text):
    return _observe('stamps', text)


def parse_public_health_reviewed(text):
    return _observe('public-health', text)
