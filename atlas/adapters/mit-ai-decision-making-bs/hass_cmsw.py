"""CMS/W HASS observations; normal Chrome can read these TLS-valid public pages.

HTML observers remain registered for when the normal fetcher's trust chain works.
They never disable TLS or replay curated browser observations as fresh data.
"""
from bs4 import BeautifulSoup
from importlib import import_module
import re
from atlas.adapters.national_curriculum_common import content, clean, course, rule, require_phrases
optional = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_departments').optional
PID = 'mit-ai-decision-making-bs'
URLS = {
    'cms': 'https://cmsw.mit.edu/academics/comparative-media-studies/undergraduate/',
    'education': 'https://cmsw.mit.edu/education-and-teaching-licensure/',
    'els': 'https://cmsw.mit.edu/english-language-studies/',
    'writing': 'https://cmsw.mit.edu/academics/writing/undergraduate/',
    'pool': 'https://cmsw.mit.edu/academics/subject-lists/cms/',
}


def section(html, identity, heading):
    root = content(html, identity)
    h = root.find(lambda n: n.name in ['h2', 'h3'] and clean(n.get_text(' ', strip=True)) == heading)
    if h is None:
        raise ValueError('CMS/W concentration heading missing')
    pieces = [str(h)]
    for n in h.next_siblings:
        if getattr(n, 'name', None) in ['h2', 'h3']:
            break
        pieces.append(str(n))
    return root, BeautifulSoup(''.join(pieces), 'html.parser')


def ids(key):
    return PID + '-hass-cmsw-' + key, 'mit-ai-hass-cmsw-' + key


def parse_cms(html):
    _, pane = section(html, 'Undergraduate Studies: Comparative Media Studies', 'Concentration')
    require_phrases(pane, ['four classes from the complete list of', 'that carry a HASS designation', 'Education subjects without a media studies component', 'but not the CMS concentration', 'make an appointment'])
    if not pane.find('a', href=URLS['pool']):
        raise ValueError('CMS complete-list target changed')
    sid, p = ids('cms')
    return dict(id=PID, requirements=[optional(p, 'Comparative Media Studies', sid), rule(p+'-four', 'Four HASS-designated CMS subjects', sid, parent=p, kind='choose_courses', count=4, summary='Choose four from the linked complete CMS required/elective list, each carrying a HASS designation. Education subjects without a media-studies component are excluded even when listed as HASS. Consult the concentration advisor/academic administrator; the list alone does not establish that a particular education subject has the required media component.')])


def parse_writing(html):
    _, pane = section(html, 'Writing Majors, Minor, Concentration', 'Concentration in Writing')
    require_phrases(pane, ['four subjects chosen in consultation with the Concentration Advisor', 'one may be a CI-HW', 'not necessary to complete a separate Concentration', 'Concentration Proposal and Completion forms', 'Only five subjects in the Minor', 'must carry a HASS designation'])
    sid, p = ids('writing')
    return dict(id=PID, requirements=[optional(p, 'Writing', sid), rule(p+'-four', 'Four advisor-selected Writing HASS subjects', sid, parent=p, kind='choose_courses', count=4, summary='Four Writing subjects chosen with the concentration advisor; every subject must carry HASS and at most one may be CI-HW. This is an advisor-selected subject criterion, not the Writing minor’s Tier I/II plan.'), rule(p+'-minor-context', 'Writing minor substitution and HASS overlap context', sid, parent=p, kind='note', summary='Completing the Writing minor removes the need for a separate concentration, but proposal/completion forms are still required. The page limits that minor’s HASS-GIR contribution to five subjects. Its six-subject minor and thesis/CI-M major requirements are not imported into the four-subject concentration.')])


def parse_els(html):
    root, pane = section(html, 'English Language Studies', 'Concentration in ELS (undergraduates)')
    require_phrases(pane, ['any three subjects in English Language Studies or related fields', 'Concentration Advisor for ELS'])
    require_phrases(root, ['open only to matriculated MIT students', 'advanced writing classes are open to native-English-speaking students as well'])
    sid, p = ids('els')
    return dict(id=PID, requirements=[optional(p, 'English Language Studies', sid), rule(p+'-three', 'Three ELS or related-field subjects', sid, parent=p, kind='choose_courses', count=3, summary='Any three English Language Studies or related-field subjects with the ELS concentration advisor. The surrounding general three-or-four-subject HASS introduction does not change this field’s explicit three-subject rule.'), rule(p+'-eligibility', 'ELS enrollment context', sid, parent=p, kind='note', summary='ELS is open only to matriculated MIT students. Advanced writing classes also admit native-English-speaking students; individual placement rules remain applicable. The English Evaluation Test described elsewhere on the page is for incoming international graduate students, not an undergraduate concentration requirement. Combined undergraduate/graduate catalog rows are not automatically three-subject eligibility options.')])


def _course_row(text, prefix, sid, url):
    match = re.fullmatch(r'((?:CMS|STS|21A|9)\.[A-Z0-9]+(?:/(?:CMS|STS)\.[A-Z0-9]+)?)\s+(.+)', clean(text))
    if not match:
        raise ValueError('Education course row changed')
    code, name = match.groups()
    return course(prefix, code, name, sid, url, category='human_context', topic=name if code=='CMS.S61' else None)


def parse_education(html):
    _, pane = section(html, 'Education and Teacher Licensure', 'Concentration')
    require_phrases(pane, ['The Concentration Consists of 3 Subjects', 'and/or', 'one or two of these subjects', '25 hours per semester'])
    sid, p = ids('education')
    intro = [_course_row(n.get_text(' ', strip=True), p, sid, URLS['education']) for n in pane.find_all('p') if re.match(r'^CMS\.58[67]J\s', clean(n.get_text(' ', strip=True)))]
    if {c['code'] for c in intro} != {'CMS.586J', 'CMS.587J'}:
        raise ValueError('Education introductory alternatives changed')
    tables = pane.find_all('table')
    if len(tables) != 1:
        raise ValueError('Education elective table changed')
    electives = [_course_row(td.get_text(' ', strip=True), p, sid, URLS['education']) for td in tables[0].find_all('td')]
    if not electives or len({c['id'] for c in electives}) != len(electives):
        raise ValueError('Education elective rows missing or duplicated')
    rules = [optional(p, 'Education', sid), rule(p+'-routes', 'One introductory subject plus two electives, or both plus one elective', sid, parent=p, kind='alternative', count=1)]
    for n in [1, 2]:
        branch = p+'-route-'+str(n)
        rules += [rule(branch, str(n)+' introductory subject(s)', sid, parent=p+'-routes'), rule(branch+'-intro', 'Introductory choice', sid, [c['id'] for c in intro], parent=branch, kind='choose_courses', count=n), rule(branch+'-elective', 'Remaining elective choice', sid, [c['id'] for c in electives], parent=branch, kind='choose_courses', count=3-n)]
    rules += [rule(p+'-scope', 'Education fieldwork and topic scope', sid, parent=p, kind='note', summary='The introductory Education sequence includes 25 hours per semester observing/working in local schools. Listed special-subject topics retain their source terms; they are not assurances of current availability or permission to count repeated content twice. Teacher-licensure requirements and the separate six-subject minor’s 300-hour practicum are not concentration requirements.')]
    return dict(id=PID, courses=intro+electives, requirements=rules)


def parse_pool(html):
    root = content(html, 'CMS Subjects: Full List and Pre-approved Electives')
    require_phrases(root, ['Full Subject List', 'Course CMS: Comparative Media Studies', 'Pre-approved Electives in Other Departments', 'sampling of classes that CMS majors', 'this list is not exhaustive', 'With permission from their CMS Major advisor'])
    tables = root.find_all('table')
    if not tables:
        raise ValueError('CMS subject tables missing')
    sid, p = ids('pool'); courses = []; main=[]; no_hass=[]; external=[]
    for i, table in enumerate(tables):
        rows = table.find_all('tr')
        header = [clean(c.get_text(' ', strip=True)) for c in rows[0].find_all(['th','td'])]
        if len(header) not in [4,5] or header[:3] != ['Subject Number (Undergraduate)', 'Subject Number (Graduate)', 'Subject Name'] or header[-1] != 'HASS, CI-H/M':
            raise ValueError('CMS undergraduate/graduate table columns changed')
        for tr in rows[1:]:
            cells=[clean(c.get_text(' ',strip=True)) for c in tr.find_all(['th','td'])]
            if not any(cells):continue
            if len(cells)!=len(header) or not cells[0] or not cells[2]:
                raise ValueError('CMS subject row structure changed')
            c=course(p+('-cms' if i==0 else '-external'), cells[0], cells[2], sid, URLS['pool'], category='human_context')
            courses.append(c)
            (external if i else main if 'HASS-' in cells[-1] else no_hass).append(c['id'])
    if len({c['id'] for c in courses})!=len(courses):raise ValueError('Duplicate CMS subject identity')
    return dict(id=PID,courses=courses,requirements=[rule(p+'-hass', 'CMS list rows with an explicit HASS designation', sid, main, kind='note', summary='Reference observations from the undergraduate column. CMS concentration selection still requires a media-studies component for education subjects; HASS designation alone is insufficient. Graduate registrations in the adjacent column are not imported. Cross-list labels are preserved as printed, including unusual punctuation.'),rule(p+'-no-hass', 'CMS list rows without a published HASS designation',sid,no_hass,kind='note',summary='These observed rows do not establish HASS eligibility and are not automatically usable for the four-subject concentration.'),rule(p+'-external','External-elective reference list explicitly framed for majors',sid,external,kind='note',summary='The linked page labels these other-department rows a nonexhaustive sampling used by CMS majors and states a major-advisor approval route. Although the concentration page links the whole required/elective list, it does not explicitly extend that major-only substitution route to concentrators. Keep this reference distinct; confirm concentration applicability and HASS/media-content criteria with the concentration advisor before treating it as an approved concentration pool.')])


SOURCE_PARSERS={URLS['cms']:parse_cms,URLS['education']:parse_education,URLS['els']:parse_els,URLS['writing']:parse_writing,URLS['pool']:parse_pool}
