"""Public UMSI handbook and published course-table observations.

Handbook input is a reviewed Markdown export from its publicly linked Google Doc.
An HTML sign-in/shell is never treated as document text. Raw exports stay outside git.
"""
import hashlib
import json
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course, rule

PROGRAM_ID = 'university-of-michigan-ann-arbor-human-centered-artificial-intelligence-minor-minor'
HANDBOOK = 'https://docs.google.com/document/d/1HjJWDqwtp4_CJJisHxaQQI2a7MTjji-JbBdI3NLuHyg/edit?usp=sharing'
TABLE = 'https://docs.google.com/spreadsheets/u/0/d/e/2PACX-1vRc2MbMVeseCzlazMefnLy0ZNo8CHRbvlpuNP9TYBLTfBJ1w2ns75NNxmhP-DErYU--QR0GEoTYXmQv/pubhtml/sheet?headers=false&gid=2034280409'
SID = "umich-hcai-handbook"
TABLE_SID = "umich-hcai-course-table"
HANDBOOK_HASH = 'ef36f003119443540153bb72a1eb4f179c23bfce41fab6223c4c247e401a7e1d'
POLICIES = [('eligibility', 'Declaration eligibility', 'A declared major, good academic standing and an approving home college are required. The handbook lists Engineering; LSA; Ford Public Policy; Ross Business; Education; Kinesiology; Music, Theatre & Dance; Nursing; Public Health; Stamps Art & Design; and Taubman Architecture. BSI students may take HCAI, but not the other two UMSI minors.'), ('grades', 'Letter grades and minor GPA', 'Each minor course requires a letter grade of C- or higher; the minor GPA must be at least 2.0.'), ('residency', 'Residential coursework', 'All minor coursework must be completed residentially at the University of Michigan; study-abroad and other-institution courses are not eligible.'), ('overlap', 'Major and minor overlap', 'UMSI generally permits major/minor overlap, subject to the major and home department rules. Those local rules have not all been inventoried.'), ('bsi', 'BSI-specific overlap', 'SI 310 automatically counts toward both BSI and HCAI. Other HCAI courses cannot also fulfill BSI pathway prerequisites or advanced selectives; SI credits still count toward the BSI overall SI-credit requirement.'), ('two-minors', 'Two UMSI minors', 'HCAI may be combined with either UX or SMAD, with no course double-counting between the two minors. UX and SMAD cannot be paired.'), ('release', 'Declaration and release', 'Separate declaration and release requests are required. A release request requires completed or current enrollment in all necessary coursework.'), ('registration', 'Enrollment and priority', 'Courses can be taken before declaration when prerequisites and seats permit; declared minors have enrollment priority. The course-specific registration guide linked from this handbook was unavailable at review.'), ('renumbering', 'Renumbered courses', 'UMSI accepts both the previous and current names/numbers toward minor progress. The handbook identifies SI 310 as formerly SI 302 and SI 346 as formerly the SI 311 AI and the Law topic.'), ('ranges', 'Variable-credit choices', 'PHIL 340 is listed at 2–4 credits and COMM 349 at 3–4. Neither is assigned a guessed fixed amount; actual elected credits must meet the elective minimum.'), ('coreq', 'SI 376 prerequisite relationship', 'The handbook identifies SI 326 as a corequisite for SI 376. The current course table permits SI 326 before or alongside SI 376, with C- or better.'), ('dated-electives', 'Current credits versus historical course count', 'The May 2025 launch announcement described three electives. The current handbook instead requires at least nine elective credits and includes 1.5-credit choices; the historical count is not applied to the current inventory.')]
SUMMARIES = {'212': 'Uses AI assistants to create programs without prior programming study, including simulations, text processing and games.', '310': 'Applies ethical frameworks to information technology, including privacy, intellectual property, surveillance and generative AI.', '326': 'Introduces how AI functions and examines bias, inequality, surveillance and societal consequences without requiring coding.', '332': 'Examines privacy and surveillance across law, computing, media, health and other disciplines.', '346': 'Examines whether existing legal and regulatory approaches address the ethical and policy consequences of AI and machine learning.', '376': 'Uses no-code AI tools to assess practical applications and ethical tradeoffs in fields such as health, education and design.', '405': 'Builds and evaluates applied generative-AI systems in Python using language-model APIs and local models.', '410': 'Examines ethical information practices through social technologies, collective knowledge and game design.', '434': 'Examines algorithmic effects on people and communities, including bias, discrimination, fairness, privacy and justice.', '465': 'Implements machine-learning methods in Python, emphasizing supervised learning with introductions to unsupervised, deep and reinforcement learning.'}
PREREQUISITES = {'376': 'SI 326 before or concurrently, with C- or better.', '405': 'Prior SI 345 (previously SI 330) and SI 385 (previously SI 370).', '410': 'Junior or senior standing.', '465': 'Term-dependent enforced rule: Winter 2026 had no enforced prerequisites. From Fall 2026, prior SI 345 and prior or concurrent SI 385, OR a declared Engineering/LSA undergraduate major in Data Science, Computer Science, Mathematics or Economics. Advisory preparation is separately listed as prior SI 325 and SI 385 (previously SI 370).'}
ROW_HASHES = {'212': '141ebba0cf0dd1e15fab6d15a87c9b4b387e9b41a064a3aa9f4c17767bb6f85a', '310': 'c3ca62ee76d27f91cac36756b2e2ffc428080f505c26eb70148165e628e8e927', '326': 'a007ed219de751e7696d84b3d477b58f997062dfcbe9a1d076c67f377b0eba33', '332': '2b92a0c908decd6965ce723b79d0b2b52df6118cbf33eceaed78ce21b7cfdc44', '346': '8fc16c51322be9bcab051ed32009a517dca20353f335ff2891b220d96b805377', '376': '5702d000ee8e9ffc42a4aeb596645155688435aa1c340c02b286dbdfcf141de8', '405': '5eb63e88413823d305ba5b115f66d5c803fd85da31218225e71657d2c7461bc7', '410': '7d755e45cdb8390cd7b2b35fe90fb2ab28b8eedb2ba2db64249310af9e7ca212', '434': 'd69828f7424bea981e88a1bbacf3ea4b021170e47a2be3e77478d8ef1e390ad7', '465': 'e0e8a2744e99682441a8925400ba448a7f7a3e6a087a25b4086ffe02fb06cab7'}


def category(code):
    # Editorial grouping from reviewed course titles/descriptions, not source outcomes.
    if code in {"SI 326", "SI 405", "SI 465", "LING 321", "EECS 449", "EECS 492", "COGSCI 446"}: return "ai_ml"
    if code in {"SI 212", "SI 311", "SI 376", "ARCH 411", "TO 433", "TO 438"}: return "applications"
    return "human_context"

def parse_handbook(text):
    if hashlib.sha256(text.encode()).hexdigest() != HANDBOOK_HASH:
        raise ValueError('Handbook changed or export unavailable; review public document before updating')
    section = text.split('## **Human-Centered Artificial Intelligence**', 1)[1].split('## **Frequently Asked Questions**', 1)[0]
    courses = []
    for match in re.finditer(r'^\* ([A-Z/]+ \d+): (.+?) \((\d+(?:\.\d+)?(?:-\d+)?) credits\)', section, re.M):
        code, name, amount = match.groups()
        name = name.replace('\\', '')
        value = None if '-' in amount else float(amount)
        topic = name if code in ('SI 311', 'SI 411') else None
        c = course('umich-hcai', code, name, SID, HANDBOOK, value, 'semester_hours', category=category(code), topic=topic)
        if code == 'SI 376': c['prerequisites'] = 'Corequisite: SI 326 (handbook); see current course-table qualification.'
        courses.append(c)
    if len(courses) != 25 or [c['code'] for c in courses[:2]] != ['SI 326','SI 376']:
        raise ValueError('Expected two core courses and 23 named elective options')
    core, electives = courses[:2], courses[2:]
    si310 = next(c for c in electives if c['code'] == 'SI 310')['id']
    requirements = [
        rule('umich-hcai-root', 'Human-Centered AI minor requirements', SID),
        rule('umich-hcai-core', 'Two required core courses', SID, [c['id'] for c in core], parent='umich-hcai-root'),
        rule('umich-hcai-routes', 'Elective route determined by degree enrollment', SID, parent='umich-hcai-root', kind='alternative', summary='The standard and BSI routes are conditional on the student’s degree; they are not freely interchangeable.'),
        rule('umich-hcai-standard', 'Non-BSI students: at least nine elective credits', SID, [c['id'] for c in electives], parent='umich-hcai-routes', kind='choose_credits', credits=9, unit='semester_hours'),
        rule('umich-hcai-bsi-route', 'BSI students: SI 310 plus six additional elective credits', SID, [si310], parent='umich-hcai-routes'),
        rule('umich-hcai-bsi-electives', 'BSI: six additional approved elective credits', SID, [c['id'] for c in electives if c['id'] != si310], parent='umich-hcai-bsi-route', kind='choose_credits', credits=6, unit='semester_hours'),
    ]
    requirements += [rule('umich-hcai-'+key, title, SID, parent='umich-hcai-root', kind='note', summary=summary) for key,title,summary in POLICIES]
    outcomes = [dict(text=text, kind='source_stated', statement_type='learning_outcome', source_id=SID, locator='Human-Centered Artificial Intelligence: five learning outcomes') for text in [
        'Understand AI from technical and social perspectives.', 'Reason ethically about AI use and consequences.',
        'Assess whether AI is appropriate for a situation.', 'Investigate practical applications of AI.',
        'Communicate the effects of AI systems and applications.']]
    return dict(id=PROGRAM_ID, courses=courses, requirements=requirements, outcomes=outcomes)


def parse_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    rows = {}
    for tr in soup.find_all('tr'):
        cells = [clean(td.get_text(' ',strip=True)) for td in tr.find_all('td')]
        if len(cells) >= 9 and cells[0] == 'SI' and cells[1] in ROW_HASHES:
            if cells[1] in rows: raise ValueError('Duplicate reviewed course')
            rows[cells[1]] = cells
    if set(rows) != set(ROW_HASHES): raise ValueError('Incomplete public course table')
    courses=[]
    for code, cells in rows.items():
        digest=hashlib.sha256(json.dumps(cells[:9],ensure_ascii=False).encode()).hexdigest()
        if digest != ROW_HASHES[code]: raise ValueError('Course changed; review SI '+code)
        c=course('umich-hcai','SI '+code,cells[2].rsplit(' (',1)[0],TABLE_SID,TABLE,float(cells[8]),'semester_hours',category=category('SI '+code))
        c['description']=SUMMARIES[code]
        c['prerequisites']=PREREQUISITES.get(code)
        courses.append(c)
    return dict(id=PROGRAM_ID,courses=courses)
