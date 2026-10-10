"""Conditional MIT entrant-credit and HASS evidence, separate from major slots."""
import re
from functools import partial
from atlas.adapters.national_curriculum_common import content, clean, course, rule, require_phrases

PID = 'mit-ai-decision-making-bs'
AP_GATE = 'https://firstyear.mit.edu/academics-exploration/ap-transfer-credit/'
HASS = 'https://shass.mit.edu/for-students/undergraduate-study/computing-and-society-concentration/'
MATH = 'https://math.mit.edu/academics/undergrad/major/'


def parse_ap_gateway(html):
    root = content(html, 'MIT Credit Policies at Entrance for Fall 2026')
    require_phrases(root, ['applies only to the Class of 2030 entering Fall 2026', 'grade of S', 'does not count toward term or cumulative averages', 'register for any version of that subject you will forfeit the credit', 'only if you drop the registered subject by Add Date'])
    sid = PID + '-ap-gateway'
    return dict(id=PID, requirements=[rule('mit-ai-ap-cohort', 'Fall 2026 entrant credit policy and repeat forfeiture', sid, kind='note', summary='This gateway expressly applies only to Fall 2026 entrants (Class of 2030), not automatically to every 6-4_2025 cohort. Entrance credit may be equivalent-subject or unrestricted elective credit at departmental discretion; S credits do not enter GPA. Registering for any version of a subject already credited from prior study forfeits that credit; reinstatement requires dropping by Add Date. Earlier entrants need their own cohort policy.')])


def parse_hass(html):
    root = content(html, 'Computing and Society Concentration')
    require_phrases(root, ['Four of any of the subjects listed below', 'selected in consultation with the Concentration Advisor', 'only one subject that also counts toward the HASS Distribution Requirement'])
    sid = PID + '-hass-computing'
    courses = []
    for p in root.find_all('p'):
        text = clean(p.get_text(' ', strip=True))
        m = re.fullmatch(r'([A-Z0-9]+\.[A-Z0-9]+(?:\[J\])?) (.+), HASS-[A-Z](?:, CI-H)?', text)
        if m:
            courses.append(course('mit-ai-hass-computing', m[1], m[2], sid, HASS, unit='units', category='human_context', topic=m[2] if '.S' in m[1] else None))
    if not courses:
        raise ValueError('Optional HASS concentration course list missing')
    parent = 'mit-ai-hass-computing-option'
    return dict(id=PID, courses=courses, requirements=[
        rule(parent, 'Optional HASS field: Computing and Society', sid, kind='note', summary='This is one optional HASS concentration, not an AI-major requirement or the only eligible HASS field. Apply its child rule only when this field is selected. Other HASS fields retain their own advisor-approved requirements.'),
        rule('mit-ai-hass-computing-four', 'Four advisor-selected subjects', sid, [c['id'] for c in courses], parent=parent, kind='choose_courses', count=4, summary='For this chosen HASS field, complete four listed subjects in consultation with its advisor. At most one may also meet the HASS Distribution requirement. Topic-specific special-subject titles are preserved rather than treating every offering of a special number as eligible.'),
    ])


def parse_math(html):
    root = content(html, 'Math Major')
    require_phrases(root, ['Fall 2026 start date and beyond', 'at most one of the subjects from each', 'Special subjects are not automatically counted', '18.06, 18.C06', '18.702 or 18.703', '18.04 or 18.075 or 18.112', '18.05 or 18.600 or 6.3700', '18.650 or 15.075', '18.400J or 18.404J', '18.062 or 18.200 or 18.200A', '18.413 or 18.417'])
    sid = PID + '-math-similarity'
    return dict(id=PID, requirements=[rule('mit-ai-math-similarity', 'Linked Course 18 similarity restrictions', sid, kind='note', summary='The linked mathematics page labels its new program Fall 2026+ and directs earlier entrants to older rules; special subjects are not automatically eligible. Its similarity exclusions allow at most one within each set: {18.06, 18.C06, 18.700}; {18.702, 18.703}; {18.04, 18.075, 18.112}; {18.05, 18.600, 6.3700, 15.069, 15.079}; {18.650, 15.075}; {18.400J, 18.404J}; {18.062, 18.200, 18.200A}; {18.413, 18.417}. The 6-4 source explicitly applies the no-similar-content criterion to its open MATH elective. Historical special cases remain restricted to their stated offerings; these groups are exclusions, not a finite elective pool.')])


SOURCE_PARSERS = {AP_GATE: parse_ap_gateway, HASS: parse_hass, MATH: parse_math}


ENTRANCE = {
 'ap': ('https://firstyear.mit.edu/academics-exploration/ap-transfer-credit/advanced-placement/', 'Advanced Placement', [
  ('math-science', ['Class of 2030 (entering Fall of 2026)', 'No credit is given for the AP Biology exam', 'No credit is given for the AP Chemistry exam', 'No credit is given for the AP Computer Science exams', 'Calculus BC', 'Calculus AB', 'both Physics C exams', 'Environmental Science or Statistics'], 'For Fall 2026 entrants only, AP Calculus BC 5 earns 18.01; AB 5 permits accelerated 18.01A/18.02A placement rather than credit. Both Physics C exams at 5 earn 8.01. No AP Biology, Chemistry, Computer Science, Environmental Science, Statistics or separate Physics 1/2 credit is granted. Lower scores receive no partial credit; a repeated exam uses the higher score.'),
  ('electives', ['9 units each of unrestricted elective credit', 'both of the Capstone exams', 'total of 9 units', 'cannot be used to satisfy any part of the HASS Requirement', 'still required to take a Communication-Intensive subject'], 'For the stated entrant cohort, eligible Arts, English, History/Social Sciences and World Languages/Cultures AP exams at 5 yield nine unrestricted elective units each. Both Capstone exams at 5 together yield nine units. AP never substitutes for HASS; English AP placement does not waive the first-year CI subject. Official College Board scores, rather than self-reports, establish credit.'),
 ]),
 'international': ('https://firstyear.mit.edu/academics-exploration/ap-transfer-credit/international-examinations/', 'International Examinations', [
  ('math-physics', ['A-LEVELS', 'A* or A', 'Higher Level Exams Only', 'score of 7', 'D3, D2, or D1', 'No credit is given for Pre-U Mathematics', 'scores 16 through 20', 'scores 13 through 15'], 'Within the Fall-2026-entry policy gateway, A-level Mathematics/Physics A* or A earn 18.01/8.01; higher-level IB Mathematics/Physics 7 earn those respective subjects. Pre-U Physics D1/D2/D3 earns 8.01, while Pre-U Mathematics/Further Mathematics earns none. French Baccalaureate Mathematics/Physics 16–20 and Abitur Mathematics/Physics 13–15 earn 18.01/8.01 respectively. Unlisted examinations require departmental review.'),
  ('other', ['Geography', '3 units of unrestricted elective credit', '9 units of unrestricted elective credit', 'No credit is given for the IB Biology exam', 'No credit is given for the IB Chemistry exam', 'Information Technology in a Global Society', 'final credit cannot be applied'], 'The listed qualifying humanities/arts/social-science international exams earn nine unrestricted elective units: A-level A*/A, higher-level IB 7, Pre-U D1–D3, French Baccalaureate 16–20 or Abitur 13–15. Geography A*/A is listed for three unrestricted units in A-level and Pre-U sections. The source denies Biology/Chemistry credit across its listed systems and specified A-level CS/IB ITGS credit. Final degree credit needs official final certification (or electronically released IB results), not preliminary results alone. The gateway limits these policies to its entrant cohort.'),
 ]),
}


def parse_entrance(key, html):
    url, heading, specs = ENTRANCE[key]
    root = content(html, heading)
    sid = PID + '-entrance-' + key
    rules = []
    for suffix, markers, summary in specs:
        require_phrases(root, markers)
        rules.append(rule('mit-ai-entrance-' + key + '-' + suffix, heading + ': ' + suffix.replace('-', ' '), sid, kind='note', summary=summary))
    return dict(id=PID, requirements=rules)


SOURCE_PARSERS.update({spec[0]: partial(parse_entrance, key) for key, spec in ENTRANCE.items()})
