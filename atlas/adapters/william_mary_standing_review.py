"""Observed public standing/version policies; manual audits live only in seeds."""
from functools import partial
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import content, require_phrases, rule

PID = 'william-mary-applied-ai-ba'
BASE = 'https://www.wm.edu/'
SPECS = {
 'continuance': (BASE+'offices/advising/forstudents/academicpolicies/contfulltime/index.php', 'Continuance Requirements for Full-time Students', [
  ('degree', 'Graduation GPA and academic credit minimum', ['120 credits in academic subjects', '2.0 overall and in their major'], 'The central undergraduate continuance policy explicitly requires 120 academic credits and a GPA of at least 2.0 overall and in the major for graduation. The minimum credits in this policy are not a replacement for the major, proficiency or distribution requirements.'),
  ('thresholds', 'Full-time continuance thresholds', ['Only W&M credit', 'Transfer, Advanced Placement (AP), and International Baccalaureate (IB)', 'begin at William & Mary under the Continuance Standards for semester 1'], 'Full-time continuance uses cumulative W&M credits and GPA, including W&M summer work. Semesters 1–10 require credits 9, 21, 33, 48, 60, 72, 84, 96, 108 and 120 respectively, with GPA 1.7, 1.7, 1.85 and then 2.0 for semesters 4–10. Incoming transfer and first-year students both start at semester 1. Transfer/AP/IB credit is excluded from continuance, even when eligible toward the degree. This table does not itself establish a ten-semester graduation deadline.'),
  ('probation', 'Continuance probation and warning conditions', ['Academic Warning', 'ASPIRE or THRIVE', 'may not enroll in more than 16', 'may not receive any incompletes', 'or all credits in an approved underload', 'two regular semesters'], 'GPA below 2.0 triggers academic warning and CONNECT. Falling below the continuance GPA or earned-credit threshold triggers probation. This page specifies at most 16 credits, no incompletes, at least a 2.0 semester GPA and 12 passed credits or all credits of an approved underload; ASPIRE or THRIVE and advisor consultation are required. It allows two regular semesters to restore continuance while those conditions hold. The separate probation page gives narrower wording; no priority or automatic exception is inferred.'),
 ]),
 'gpa': (BASE+'offices/studentsuccess/academic-wellbeing/resources/gradecalculation/index.php', 'Grade Calculation', [
  ('calculation', 'GPA calculation and grade values', ['A = 4.0', 'A- = 3.7', 'B+ = 3.3', 'C- = 1.7', 'D- = .7', 'F = 0', 'total number of quality points earned', 'total number of attempted credit hours', 'Fs have no quality points', 'P (passing grade)'], 'GPA divides quality points by attempted graded credit hours. Grade values are A 4.0, A− 3.7, B+ 3.3, B 3.0, B− 2.7, C+ 2.3, C 2.0, C− 1.7, D+ 1.3, D 1.0, D− 0.7 and F 0. F counts in attempted credits; P is excluded. Cumulative GPA uses W&M semesters, subject to the separately published repeat policy. Illustrative courses in this explanatory page are not degree requirements.'),
 ]),
 'probation': (BASE+'offices/advising/forstudents/academicpolicies/probation/index.php', 'Academic Probation', [
  ('qualification', 'Separate probation-page wording', ['ASPIRE Program', 'one semester', 'an additional probationary semester may be granted', 'at least 12 credits', 'only to work completed in a W&M summer program'], 'The separate probation page requires ASPIRE, a semester GPA of at least 2.0 and at least 12 passed credits, caps enrollment at 16 and disallows final incompletes. It describes one semester to restore continuance and a possible additional semester if the GPA/credit minimums are met. W&M summer work can restore standing under its stated conditions. Its omission of the approved-underload and THRIVE alternatives, and discretionary second-semester wording, differ from the continuance page; applicability remains unresolved.'),
 ]),
 'suspension': (BASE+'offices/advising/forstudents/academicpolicies/suspension/index.php', 'Academic Suspension', [
  ('return', 'Suspension, appeal and outside-credit restrictions', ['complete severance', 'Committee on Academic Exceptions', 'Credits earned while a student is academically suspended', 'will not transfer', 'unlikely that a student who is suspended twice'], 'Academic suspension severs enrollment and appears on the transcript. A written appeal addressing compelling circumstances goes to the Committee on Academic Exceptions by the individual notice deadline. Reinstatement requires evidence that barriers to success have been corrected. Suggested outside courses or work are preparatory recommendations, not new degree requirements; courses taken while suspended do not transfer or count toward the W&M degree. Return after a second suspension is described as unlikely, not categorically impossible.'),
 ]),
 'progress': (BASE+'offices/advising/forstudents/academicpolicies/progress/index.php', 'Normal Progress Toward a Degree', [
  ('pace', 'Four-year progress guidance and semester calendar', ['four academic years without attending summer school', '30 academic credits and 60 quality points', '2.0 cumulative', '2.0 major', 'two semesters, one in the fall and one in the spring'], 'For a four-academic-year plan without summer school, the university advises an annual average of 30 academic credits and 60 quality points while maintaining 2.0 overall and major GPAs. The typical year has fall and spring semesters, sometimes with summer; January entrants use the stated shifted year. This pacing guidance is not an unconditional annual degree-credit requirement or proof of a ten-semester maximum.'),
 ]),
 'flex': (BASE+'offices/advising/forstudents/academicpolicies/flextrackfaqs/index.php', 'Policies for FlexTrack Students', [
  ('route', 'Conditional FlexTrack load, duration and standing', ['between 3 and 18', 'minimum of 12 credit hours each calendar year', 'within ten years', '1.7 cumulative GPA by the end of a nine-credit term', '1.85 cumulative GPA by the end of a 33-credit term', '2.0 cumulative GPA by the end of a 48-credit term', 'must petition the Committee on Academic Exceptions'], 'Only admitted or approved FlexTrack students use this alternative: 3–18 credits per semester, at least 12 credits each calendar year and all degree/major requirements within ten years. Switching to or from full-time status requires a petition. Cumulative GPA thresholds are 1.7 at the nine- and 21-credit terms, 1.85 at 33 and 2.0 at 48 and later terms. These conditional rules do not replace the full-time route or imply Applied AI-specific admission approval.'),
 ]),
 'active-duty': (BASE+'offices/advising/forstudents/academicpolicies/active-duty/index.php', 'Withdrawal from the University for Students Called to Active Duty', [
  ('exception', 'Conditional military-service withdrawal and return', ['Option 1', 'Option 2', 'agreed upon in writing', 'within one semester of reenrollment', 'faculty and dean approval', 'have not enrolled for degree-seeking study at another institution', 'without a time limit imposed', 'accreditation or other external policies'], 'Eligible students called to active duty may arrange withdrawal or written instructor agreements for incompletes through the Advising Center. Incomplete work is normally finished within one semester of return; extensions require faculty and dean approval. Students who left in good standing and did not enter another degree program may return without a time limit, subject to enrollment encumbrances and accreditation/external limits. The stated conditions and military orders are required; this is not an automatic general time-limit waiver.'),
 ]),
 'glossary': (BASE+'as/undergraduate/academic-resources/glossary/index.php', 'Glossary of Terms', [
  ('version', 'Published distinction between general-education and major catalog versions', ["general education requirements described in the catalog that's in effect when you matriculate", "major requirements described in the catalog that's in effect when you declare your major"], 'The university undergraduate glossary distinguishes the matriculation catalog for general education from the declaration catalog for the major. This general guidance identifies the need for student/version context; it does not resolve the Applied AI FAQ/diagram conflict or establish which catalog governed an unspecified student.'),
  ('classes', 'Credit class, social class and audit-course distinctions', ['freshman, 0-23 credits; sophomore, 24-53 credits; junior, 54-84 credits; senior, 85+', 'year of your projected graduation', 'without earning credit', 'do not count toward the 12', 'do count toward the 18'], 'Credit class uses earned credits including transfer: freshman 0–23, sophomore 24–53, junior 54–84 and senior 85+. Social class is projected graduation year, so credit standing alone does not establish pass/fail eligibility. Audited courses carry no earned credit, do not meet the 12-credit minimum, and count toward the 18-credit enrollment maximum.'),
 ]),
 'majordeclare': (BASE+'as/undergraduate/major/how-to-declare/index.php', 'How to Declare Your Major', [
  ('declaration', 'Major declaration threshold and advisor approval', ['39 academic credits (including transfer credits)', 'must declare a major once you have 54 credits', 'major advisor confirming their approval', 'additional forms to declare interdisciplinary majors'], 'A major can be declared after 39 academic credits including transfer and must be declared by 54. A faculty major advisor approves the Registrar form; interdisciplinary programs may require additional forms. The specific Applied AI declaration procedure remains applicable. The general page does not replace its curriculum or authorize a substitution.'),
 ])
}

CONTINUANCE = [['1','1.7','9'],['2','1.7','21'],['3','1.85','33'],['4','2.0','48'],['5','2.0','60'],['6','2.0','72'],['7','2.0','84'],['8','2.0','96'],['9','2.0','108'],['10','2.0','120']]


def parse(html, key):
    _, heading, rows = SPECS[key]
    root = content(html, heading)
    if key == 'continuance':
        tables = BeautifulSoup(html, 'html.parser').select('main table')
        actual = [[c.get_text(' ', strip=True) for c in tr.select('td')] for table in tables for tr in table.select('tr') if tr.select('td')]
        if actual != CONTINUANCE:
            raise ValueError('W&M continuance table changed or missing')
    result = []
    for suffix, title, phrases, summary in rows:
        require_phrases(root, phrases)
        result.append(rule(PID+'-standing-'+key+'-'+suffix, title, PID+'-standing-'+key, kind='note', summary=summary))
    return {'id': PID, 'requirements': result, 'courses': []}


def register(parsers):
    for key, (url, _, _) in SPECS.items():
        if url in parsers:
            raise ValueError('Duplicate W&M standing source')
        parsers[url] = partial(parse, key=key)
