"""Public UCSB Engineering policy observations; approved dynamic pools stay unknown."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, requirement, text

PID = 'ucsb-ai-bs'
REQUIREMENTS_URL = 'https://engineering.ucsb.edu/undergraduate/academic-advising/undergraduate-requirements'
GRADING_URL = 'https://engineering.ucsb.edu/undergraduate/academic-advising/grading'
ELWR_URL = 'https://catalog.ucsb.edu/pages/0xkYLCPyqj23vECidesR'
GEAR_URL = 'https://www.engineering.ucsb.edu/sites/default/files/docs/26-27_GEAR.pdf'
FAQ_URL = 'https://ai.cs.ucsb.edu/faq'


def body(html, heading):
    soup = BeautifulSoup(html, 'html.parser')
    if not any(text(h) == heading for h in soup.find_all(['h1', 'h2'])):
        raise ValueError('UCSB policy heading missing: ' + heading)
    return text(soup.find('main') or soup)


def guarded(value, clauses):
    if any(c not in value for c in clauses):
        raise ValueError('UCSB policy changed; review required')


def node(key, title, source, **kw):
    return requirement(PID, 'policy-' + key, title, PID + '-' + source,
                       unit='quarter_hours', category='other', **kw)


def parse_requirements(html):
    value = body(html, 'Undergraduate Requirements')
    guarded(value, ['2018 forward', '35 of the final 45', '35 of the final 90',
        'minimum of 12 units on campus', 'at least three terms', '6 or more units',
        'at least two units but fewer than six', 'at least a 2.0',
        'third quarter of matriculation', 'nine quarters or more',
        'one four-unit course', 'one of these areas', 'P/NP basis'])
    courses, nodes = {}, []
    def add(key, title, **kw):
        r = node(key, title, 'college-requirements', **kw); nodes.append(r); return r['id']
    add('residence', 'University and senior residence', kind='note', summary='Register for at least three terms. A regular quarter (including the full summer period) with six resident units counts as one term; a UC summer with two to fewer than six counts as half. Complete 35 of the final 45 units in the degree-awarding college. Other institutions and UC Extension do not supply residence credit.')
    add('residence-eap', 'Senior EAP/UCDC residence exception', kind='note', summary='Prior approval permits senior EAP/UCDC students to meet 35 of the final 90 units instead. Graduation abroad is allowed if all requirements are finished; otherwise return for at least 12 campus units while completing the remaining requirements.')
    add('gpa', 'Three graduation GPA tests', kind='note', summary='At least 2.0 separately in graded UC work, all UC major courses, and upper-division UC major courses. UC Extension is excluded except UCSB concurrent enrollment from Fall 2000. Graded incompletes enter the final calculation as F; remedial workload credit does not enter GPA.')
    add('elwr-deadline', 'Entry writing timing and credit restrictions', kind='note', summary='Finish entry-level writing by the end of the third enrolled quarter or further enrollment is blocked. Writing 1, 1E or LING 12 requires C or better; unsuccessful attempts repeat in successive quarters. After matriculation, another institution cannot satisfy this requirement. Area A credit is permitted only after entry writing is satisfied. Current catalog placement/AWPE qualifications are recorded separately.')
    add('ahi', 'American History and Institutions', kind='note', summary='Satisfy through an approved four-unit course, AP American History or American Government and Politics score of at least 3, a departmental noncredit exam, or the page’s listed SAT II American History score of at least 650. Equivalent accredited, UC Extension or summer coursework may qualify; prior satisfaction at another UC transfers. Nonimmigrant visa holders may petition for waiver. Approved courses may overlap GE and major requirements. Historical exam routes do not assert current test availability.')
    ge = add('ge', 'Engineering general education, catalog 2018 onward')
    area = re.search(r'Students must complete Writing (.*?)\. NOTE:', value)
    if not area or ' and one course from' not in area[1]:
        raise ValueError('Area A course choices missing')
    left, right = area[1].split(' and one course from', 1)
    for key, label, chunk in [('a1', 'Area A first composition course', left), ('a2', 'Area A advanced composition course', right)]:
        ids = []
        for number in re.findall(r'\b\d+[A-Z]*\b', chunk):
            c = course('WRIT ' + number, None, PID + '-college-requirements', REQUIREMENTS_URL,
                       institution='ucsb', unit='quarter_hours', category='human_context')
            courses[c['id']] = c; ids.append(c['id'])
        if not ids: raise ValueError('Empty Area A pool')
        add(key, label, parent=ge, kind='choose_courses', count=1, course_ids=ids)
    for area in 'DEFG':
        match = re.search(r'Area ' + area + r': A minimum of (\d+) courses?', value)
        if not match: raise ValueError('GE distribution changed')
        add('area-' + area.lower(), 'General education Area ' + area, parent=ge,
            kind='choose_courses', count=int(match[1]), summary='Choose approved Area ' + area + ' courses. The public filtered catalog returned a loading shell; its finite pool is not yet verified.')
    guarded(value, ['four designated courses', '1800 words', 'ENGR 101', 'Ethnicity Requirement (one course)', 'World Cultures Requirement (one course)'])
    add('writing', 'Four designated writing courses', parent=ge, kind='choose_courses', count=4,
        summary='Use four Academic Senate-approved UCSB writing courses, involving at least 1,800 words beyond examinations. ENGR 101 may count even when required for the major. Transfer students consult college advising; no blanket exemption inferred.')
    add('ethnicity', 'Ethnicity designation', parent=ge, kind='choose_courses', count=1)
    add('culture', 'European Traditions or World Cultures designation', parent=ge, kind='choose_courses', count=1,
        summary='One approved course with either designation; not one in each.')
    add('overlap', 'GE overlap and grading', parent=ge, kind='note', summary='A course counts in only one general subject area, but may also satisfy each applicable special subject designation and American History and Institutions. GE may use P/NP when that option is offered; a major requirement still follows major letter-grade rules.')
    add('catalog-year', 'Applicable curriculum year', kind='note', summary='Normally use the curriculum from entering UCSB as an engineer. Changing majors uses the curriculum then in force. For students admitted from Fall 1997, breaks totaling at least nine non-summer quarters require a newer year. A year change may also be petitioned.')
    return {'id': PID, 'curriculum_status': 'partial', 'courses': list(courses.values()), 'requirements': nodes}


def parse_grading(html):
    value = body(html, 'Grading & GPA')
    guarded(value, ['120 units, or two-thirds', 'must be taken for a letter grade',
                    'all ECE courses require a C- or better', 'C or better in order to move on'])
    rows = [node('letter-grading', 'Letter-grade requirements', 'grading', kind='note',
        summary='Major courses inside and outside Engineering require letter grades. At graduation the page specifies at least 120 units, or two-thirds of UCSB resident units, letter graded; preserve this wording rather than infer a new maximum/minimum formula.'),
        node('prerequisite-grades', 'ECE and mathematics prerequisite grades', 'grading', kind='note',
        summary='ECE prerequisites require C− or better. Progression through MATH 3A–B, 4A–B and 6A–B requires C or better. Course-specific requirements may also apply.')]
    return {'id': PID, 'curriculum_status': 'partial', 'requirements': rows}


def parse_elwr(html):
    value = body(html, 'UC Entry Level Writing Requirement')
    guarded(value, ['3 or higher on either of the English AP Exams', '30 or higher', '680 or higher',
        '5 or higher', '6 or higher', 'only accept AWPE results from students transferring from another UC campus',
        'LING 12 with a C or better', 'C- or lower must repeat Writing 1', 'neither earns UC-transferable units'])
    rows = [node('elwr-entry', 'Current catalog entry-writing alternatives', 'elwr', kind='note',
        summary='Before entry: AP English, Seminar or Research at least 3 (Seminar/Research award no transfer units); ACT ELA at least 30; SAT at least 680; IB higher English A at least 5 or standard English A1 at least 6; C or better in composition meeting Area A1; or CWP placement into Writing 2. AWPE is accepted only from students transferring from another UC campus, a qualification missing from the college overview.'),
        node('elwr-placement', 'Domestic and multilingual writing placement', 'elwr', kind='note',
        summary='Students not placed into Writing 2 take Writing 1 and earn C or better, repeating after lower grades. Nonimmigrant international students use the multilingual diagnostic; placement may be LING 3A, 3B, 3C or 12, or Writing Program referral. LING 12 at C or better satisfies entry writing. These placements are not a requirement to take all listed courses.')]
    return {'id': PID, 'curriculum_status': 'partial', 'requirements': rows}
