"""Reviewed MIT registrar policy observations; no completion/freshness claims."""
from bs4 import BeautifulSoup
from functools import partial
from atlas.adapters.national_curriculum_common import clean, require_phrases, rule

PID = 'mit-ai-decision-making-bs'
BASE = 'https://registrar.mit.edu/'
# Each source has an exact page heading and independently guarded rule summaries.
SPECS = {
 'hass': ('registration-academics/academic-requirements/hass-requirement', 'HASS Requirement', [
  ('units', 'HASS units and grading', ['eight subjects of at least nine units each', 'letter grade, or under first-year P/NR grading or flexible P/NR grading', 'AP credit can never'], 'Complete eight HASS subjects normally carrying at least nine units each, using letter grades or authorized first-year/flexible P/NR. AP credit cannot fulfill any HASS component. Approved six-unit combinations are separate exceptions.'),
  ('external', 'External HASS credit restrictions', ['cannot be used towards the Distribution component', 'Subjects graded Pass/Fail', 'Harvard Law School are not eligible'], 'External transfer/cross-registered work is generally HASS Elective credit only; the HASS policy excludes external Distribution credit, Pass/Fail subjects and Harvard Law subjects. The separate transfer-processing page mentions a Distribution award case; that wording conflict requires office clarification, not an inferred automatic exception.'),
 ]),
 'hass-substitutions': ('registration-academics/academic-requirements/hass-requirement/substitutions-within-hass-requirement', 'Substitutions within the HASS Requirement', [
  ('petition', 'HASS substitution eligibility and approval', ['must petition the CUP Subcommittee', 'first-year grading, or through your flexible P/NR option', 'UROPs', 'Internships', 'Independent studies', 'instructor of the class will also need to sign'], 'A nondesignated subject needs HASS-subcommittee approval and an authorized grading basis. Letter-graded Harvard/Wellesley subjects, SHASS graduate subjects and approved six-unit combinations may qualify; UROPs, internships, independent studies, Pass/Fail or P/D/F work and Harvard Law subjects do not. Obtain advisor approval and, for a graduate subject, the instructor signature.'),
  ('language-pairs', 'Six-unit classical-language combinations', ['21L.611 and 21L.612 or 21L.613 and 21L.614', '21L.607 and 21L.608 or 21L.609 and 21L.610', 'by petition'], 'By petition, one HASS Humanities or Elective subject can be formed from a complete Latin pair 21L.611+21L.612 or 21L.613+21L.614, or Greek pair 21L.607+21L.608 or 21L.609+21L.610. These are conditional combination rules, not additional degree course slots.'),
  ('performance', 'Six-unit performance and literature combinations', ['maximum of four 6-unit performance', 'two 12-unit HASS subjects', 'except 21L.340', 'email hassreq@mit.edu for an audit adjustment'], 'Up to four six-unit Music/Theater performance or sampling subjects can form two 12-unit HASS subjects. Up to four six-unit literature samplings can form two HASS subjects, excluding 21L.340. Arts/Humanities Distribution combinations audit automatically as applicable; using a combination for HASS Elective credit needs an office audit adjustment.'),
 ]),
 'hass-fields': ('registration-academics/academic-requirements/hass-requirement/hass-concentrations', 'HASS Concentrations', [
  ('approval', 'HASS concentration plan and revision', ['three or four subjects', 'You may concentrate and minor in the same field', 'approval from the appropriate transfer credit examiner and your Concentration advisor', 'Select your field of study and choose subjects in consultation', 'cancel your Concentration Form and start a new one'], 'Choose a listed HASS field and an advisor-approved three- or four-subject plan. A concentration and minor may share a field. Outside subjects require both transfer examiner and concentration-advisor approval; one Distribution overlap requires the advisor. Revise subjects with the advisor and form; a field change requires notifying the former advisor and submitting a new form. Specific field rules remain conditional on the selected field.'),
 ]),
 'ci': ('registration-academics/academic-requirements/communication-requirement', 'Communication Requirement', [
  ('passing', 'CI passing and ordering conditions', ['must pass your CI', 'will not receive CI credit for a CI subject taken before a CI-HW', 'credit limit for the following term'], 'CI credit requires passing the designated subject. A CI-HW-required student gets no CI credit for an earlier CI subject taken before the required writing subject. Failure to maintain communication pace can lead to a CAP warning and next-term credit limit.'),
 ]),
 'ci-pace': ('registration-academics/academic-requirements/communication-requirement/pace-planning', 'Pace & planning', [
  ('transfer', 'Communication transfer route', ['During your first year at MIT, you must pass a CI subject or receive transfer credit for one', 'petition the Subcommittee on the Communication Requirement', 'total of two CI-H and two CI-M'], 'Transfer entrants take the FEE and pass or obtain approved transfer credit for a CI subject in their first MIT year. Transfer CI credit needs department-examiner approval followed by a communication-subcommittee petition. Two CI-H and two CI-M credits are still required by graduation.'),
  ('petitions', 'Communication exceptions and double-major reuse', ['CI‑M outside your major', 'coherent program approved by your academic advisor', 'rarely approved except in cases of a change of major', 'substantial and compelling new information'], 'Petition the communication subcommittee for a CI-M outside the major or a CI-M serving two majors. An outside CI-M needs a coherent advisor-approved plan. Pace deferral is rarely approved except after a major change; an appeal requires substantial new information. No exception is automatic.'),
 ]),
 'fee': ('registration-academics/academic-requirements/communication-requirement/pace-planning/first-year', 'First-year Essay Evaluation (FEE)', [
  ('placement', 'FEE-specific first writing route', ['automatically be placed', '21W.222 as your first CI subject', 'We strongly recommend that you register for 21W.220', 'does not carry CI credit', 'score', '7 on the English A or B'], 'Without an FEE result or valid exemption, placement defaults to CI-HW required. If placed into 21W.222, it must precede any other CI credit. A 21W.220 recommendation is preparation, earns HASS-H but no CI credit, and does not replace required 21W.222. AP English 5 or English A/B higher-level IB 7 provides the stated FEE exemption.'),
 ]),
 'first-year': ('classes-grades-evaluations/grades/grading-policies/first-year-grading', 'First year grading', [
  ('basis', 'First-year grading and credit', ['P/NR) grading during fall and IAP', 'A, B, C, or No Record', 'C- or better', 'earn no credit', 'Fall 2020 and beyond'], 'First-year fall and IAP use P/NR; spring uses A/B/C/No Record before standard grading from sophomore year. P requires C- or better; D/F become No Record and earn no credit. Fall 2020+ entrants may use the separate 48-unit flexible P/NR allowance after their first term.'),
 ]),
 'pnr': ('classes-grades-evaluations/grades/grading-policies/flexible-pnr-grading-option', 'Flexible P/NR Grading Option', [
  ('eligibility', 'Flexible P/NR credit and designation', ['up to 48 units', 'after their first term', 'Any subject is eligible', 'Advanced Standing Examinations are not eligible', 'before Add Date of your next enrolled regular term', 'day before the CAP degree meetings'], 'After the first term, up to 48 units may use flexible P/NR, including GIR and departmental requirements; advanced-standing-exam grades cannot. P requires C- or better; D/F earn no credit. Choose after final grades and before the next enrolled regular-term Add Date; final-term seniors have until the day before CAP degree meetings. Late changes or reversal are normally not permitted.'),
 ]),
 'repeat': ('classes-grades-evaluations/grades/grading-policies/repeating-subject', 'Repeating a subject', [
  ('credit', 'Repeat credit and GPA', ['both grades will appear', 'unit credit for a subject only once', 'can be repeated for credit'], 'Repeated subjects normally earn unit credit once, unless explicitly designated repeatable for credit. Both grades remain on internal/external records and enter term/cumulative GPA calculations using the normal units for each attempt.'),
 ]),
 'transfer': ('registration-academics/transfer-credit', 'Transfer credit', [
  ('general', 'External transfer eligibility and accounting', ['grade of S', 'not used in calculating your term or cumulative GPA', 'cannot receive transfer credit for subjects used to fulfill a degree at another institution', 'minimum grade is required', 'official transcript'], 'Department examiners decide equivalence, elective credit and any minimum grade; consult before external enrollment and provide an official transcript. Transfer credit uses S, counts toward approved requirements and does not enter GPA. Work used for another institution’s awarded degree cannot transfer. HASS and CI require additional approval.'),
  ('hass-conflict', 'Unresolved external HASS Distribution wording', ['HASS Distribution credit', 'email hassreq@mit.edu for a final signature', 'must be approved by SOCR'], 'The transfer-processing page describes final HASS signature handling when an examiner awards Distribution credit, whereas the HASS requirement/substitution pages disallow external Distribution credit. Preserve this administrative source conflict and seek HASS-office clarification before treating it as an exception. All CI transfer credit requires communication-subcommittee approval.'),
 ]),
}

SPECS.update({
 'ase': ('classes-grades-evaluations/examinations/advanced-standing-examinations', 'Advanced Standing Examinations', [
  ('eligibility', 'Advanced-standing examination eligibility', ['may not retake the exam', 'must submit a petition', 'Cross-registered students and special students are not eligible', 'never attended the class', 'within the first week'], 'An ASE needs advisor/registration-officer and instructor/department approval. Cross-registered and special students are ineligible. Prior attendance or registration in the subject or a variation normally disqualifies the attempt; the exception requires never attending and dropping within the first week. A failed ASE cannot be repeated, though the subject may subsequently be taken.'),
 ]),
 'ase-grades': ('classes-grades-evaluations/grades/grading-policies/advanced-standing-exam-grades', 'Advanced Standing Exam grades', [
  ('credit', 'ASE credit, GPA and first-year timing', ['passing grade on an ASE entitles you to full credit', 'not included in the calculation of your term or cumulative GPA', 'December or May count toward your credit limit', 'August/September or January/February do not', 'C or better', '54 units plus 6 units', '60 units plus 6 units'], 'Passing an ASE earns full subject credit but its grade does not enter GPA; a subsequent enrolled attempt enters GPA and both records remain visible. ASE grades cannot use flexible P/NR. For first-year students, fall ASE C-or-better is P, spring passing grades are A/B/C; nonpassing-record visibility depends on timing. December/May ASE units count toward first-year or academic-warning term limits, unlike August/September or January/February. Published first-year regular-term limits are 54 plus six FYD units in fall and 60 plus six FYD in spring; IAP ASE units do not count toward its 12-unit limit.'),
 ]),
})


def parse(key, html):
    path, heading, specs = SPECS[key]
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('input', attrs={'type': 'password'}):
        raise ValueError('Access page is not policy evidence')
    h1, main = soup.find('h1'), soup.find('main')
    if h1 is None or clean(h1.get_text(' ', strip=True)) != heading or main is None:
        raise ValueError('Registrar source identity or main content missing')
    for n in main.find_all(['nav', 'aside', 'footer', 'script', 'style']): n.decompose()
    sid = PID + '-registrar-' + key
    rules = []
    for suffix, title, markers, summary in specs:
        require_phrases(main, markers)
        rules.append(rule('mit-ai-registrar-' + key + '-' + suffix, title, sid, kind='note', summary=summary))
    return dict(id=PID, requirements=rules)


SOURCE_PARSERS = {BASE + spec[0]: partial(parse, key) for key, spec in SPECS.items()}
