"""Source-specific public USF policy observations; review completeness stays manual."""
import re
from atlas.adapters.national_curriculum_common import content, clean, require_phrases, rule, course

PID = 'university-of-south-florida-artificial-intelligence-bs-degree'
GE = 'https://www.usf.edu/undergrad/general-education-council/usf-general-education/index.aspx'
APPROVED = 'https://www.usf.edu/undergrad/general-education-council/usf-general-education/approved-usf-general-education-courses.aspx'
CIVIC = 'https://www.usf.edu/undergrad/students/civics-literacy.aspx'
TRANSFER = 'https://www.usf.edu/undergrad/curriculum/general-course-information.aspx'

def parse_ge(html):
    root = content(html, "USF's General Education")
    require_phrases(root, ['36 hours divided into 15 hours', '21 hours of USF-chosen courses', 'There are no requirements around how many of these enhancements students need to take', 'in some cases a student can take a State Core course as a gen ed elective', 'please check with an academic advisor'])
    table = next((t for t in root.find_all('table') if 'State Core Credits' in t.get_text()), None)
    if not table: raise ValueError('GE distribution table missing')
    rows = [[clean(c.get_text()) for c in tr.find_all(['td','th'])] for tr in table.find_all('tr')]
    fields = ['Communication','Humanities','Mathematics','Natural Science','Social Science']
    observed = [row for row in rows if row and row[0] in fields]
    if len(observed)!=5 or {r[0] for r in observed}!=set(fields): raise ValueError('GE discipline inventory changed')
    sid='usf-ai-general-education';rootid='usf-ai-ge'
    groups=[rule(rootid,'General education: 36 published credit hours',sid,kind='note',credits=36,summary='Complete 15 state-core and 21 USF-designated credit hours across five disciplines, including the additional two-course choice below. Current approved course attributes determine eligibility; no finite pool is inferred.')]
    for name,state,usf,total in observed:
        if [state,usf,total]!=['3','3','6']: raise ValueError('GE discipline credit distribution changed')
        groups.append(rule(rootid+'-'+name.lower().replace(' ','-'),name,sid,parent=rootid,kind='note',credits=6,summary='Three state-core credits plus three USF-designated credits in this discipline; choose currently approved courses. Credit unit normalization remains unverified.'))
    choice = next((r for r in rows if r and 'Choose 2 courses' in r[0]),None)
    if not choice or choice[1:]!=['0','6','6']: raise ValueError('Additional GE course choice changed')
    groups += [rule(rootid+'-additional','Two further general-education courses',sid,parent=rootid,kind='note',credits=6,summary='Choose two courses totaling six published credits from any of the five general-education disciplines.'),rule(rootid+'-enhancements','Enhancement and state-core reuse rules',sid,kind='note',summary='Enhancement labels impose no separate student quota. A state-core course may sometimes serve as a general-education elective; an advisor must confirm the major-specific use. This does not authorize double-counting one course in two slots.')]
    return dict(id=PID,requirements=groups)

def parse_approved(html):
    root=content(html,"Approved USF's General Education Courses")
    require_phrases(root,['courses currently approved', 'Course Inventory', 'Course Attributes', 'USF General Education Communication', 'click "Search."'])
    return dict(id=PID,requirements=[rule('usf-ai-ge-approval','Current course-attribute approval', 'usf-ai-ge-approved',kind='note',summary='Use the public Course Inventory and filter Course Attributes by the required general-education discipline. Approval is a current designation; the full changing pool is not invented from brochure examples.')])

def parse_civic(html):
    root=content(html,'Civic Literacy Requirement')
    require_phrases(root,['Cohort 1 - Started Before The 2018 Summer B session', 'Cohort 2 - Started During 2018 Summer B through 2021 Summer A', 'Cohort 3 - Started Summer B 2021 or later', 'assessment AND approved course', 'Out-of-state students and students pursuing an additional bachelor’s degree are NOT exempt', 'students entering in Fall 2024 or later can no longer', 'not offered at USF', '60% or better', 'official high school transcript', 'Both the exam and course requirement must be documented', 'course syllabus', 'Office of Undergraduate Studies', '"C-" or higher', 'did not meet the requirements as part of their initial degree', 'unlimited attempts', '60% or higher', 'Naturalization/Citizenship Test', 'will not have met the Civic Literacy requirement', 'must be completed before graduation'])
    sid='usf-ai-civic-literacy'
    specs=[
      ('cohorts','Civic-literacy entry cohorts','Complete applicable civic literacy before graduation. The entry date at a Florida public institution controls: before Summer B 2018 generally exempt; Summer B 2018–Summer A 2021 requires course or assessment; Summer B 2021 onward requires both. Out-of-state and additional-degree students are not categorically exempt; the FAQ requires returning earlier graduates to fulfill previously unmet civic literacy.'),
      ('routes','Approved course and assessment routes','Course options are POS 2041, AMH 2020, AMH 2010 completed Fall 2024 onward, or transfer-only AMS X010 from Fall 2024 onward. Assessment uses FCLE or approved acceleration. The internal USF Canvas test is available only to pre-Fall-2024 entrants and requires 60%, with unlimited attempts.'),
      ('transfer','Civic transfer and prior assessment evidence','Florida public-college/university credit needs official transcript evidence for each completed component; an incomplete component remains due. A high-school FCLE pass of at least 60% needs the official transcript and satisfies assessment only. Out-of-state course substitutions require an advisor-submitted syllabus review.'),
      ('overlap','General-education overlap and passing grade','POS X041, AMH X010 and AMH X020 may also meet state-core social science with C− or better. A lower passing grade may satisfy civic literacy alone. AMH X010 must be completed Fall 2024 onward. Naturalization testing does not satisfy the assessment.')]
    groups=[rule('usf-ai-civic-'+key,title,sid,kind='note',summary=text) for key,title,text in specs]
    text=clean(root.get_text(' ',strip=True))
    mechanisms=[('Advanced Placement (AP) Government and Politics: United States','3 or higher','Course & Assessment'),('Advanced Placement (AP) United States History','4 or higher','Course & Assessment'),('Cambridge AICE History: U.S. History, c. 1840-1992 (A-level)','A-E','Course only'),('CLEP American Government','50 or higher','Course & Assessment'),('CLEP History of the United States I','50 or higher','Course & Assessment'),('CLEP History of the United States II: 1865 to present','50 or higher','Course only'),('Dual Enrollment POSX041, AMH X020, AMH X010 (taken Fall 2024 or later), or AMS X010 (taken Fall 2024 or later)','Passing Grade','Course only'),('International Baccalaureate (IB) History of the Americas','5-7','Course only')]
    for title,score,result in mechanisms:
        if f'{title} Score required: {score} Requirement Met: {result}' not in text: raise ValueError('Civic acceleration changed: '+title)
    groups.append(rule('usf-ai-civic-acceleration','Approved acceleration mechanisms',sid,kind='note',summary='Both components: AP US Government ≥3, AP US History ≥4, CLEP American Government ≥50, or CLEP US History I ≥50. Course only: AICE US History A-level A–E, CLEP US History II ≥50, IB History of the Americas 5–7, or passing approved dual enrollment (Fall 2024 timing applies to AMH X010/AMS X010).'))
    courses=[]
    for code in ['POS 2041','AMH 2010','AMH 2020']:
        m=re.search(re.escape(code)+r' ([A-Za-z][A-Za-z0-9 ]+?)(?:,|\s*\(|\.)',text)
        if not m:raise ValueError('Civic course name missing: '+code)
        courses.append(course('usf',code,m[1].strip(),sid,CIVIC,category='human_context'))
    return dict(id=PID,requirements=groups,courses=courses)

def parse_transfer(html):
    root=content(html,"Florida's Statewide Course Numbering System")
    require_phrases(root,['same prefixes and same last three digits', 'comparable faculty credentials', 'if the minimum grade has been earned', 'quarter-term system may not transfer the equivalent number', 'Courses not offered by the receiving institution', 'non-accredited institutions', 'prior to the established transfer date', '900-999 series', 'Applied academics for adult education', 'Graduate courses', 'Internships, apprenticeships, practica, clinical experiences', 'Applied courses in the performing arts', 'skills courses in Criminal Justice'])
    sid='usf-ai-course-equivalency'
    return dict(id=PID,requirements=[rule('usf-ai-scns','Statewide course-equivalency framework',sid,kind='note',summary='SCNS equivalence ordinarily requires the same prefix/last three digits, comparable faculty credentials and the applicable minimum grade; equivalent transferred work serves requirements on the same basis as native credit. Quarter and semester amounts may differ. Other credit acceptance remains institution-specific.'),rule('usf-ai-scns-exceptions','Exceptions to automatic course equivalency',sid,kind='note',summary='Individual review applies to unoffered or unaccredited/pre-transfer-date courses; 900–999 special work; adult applied academics; graduate courses; internships, apprenticeships, practica, clinical or abroad experiences; and performing-art/Criminal Justice skill courses. These exceptions do not establish approval for an AI requirement.')])

PARSERS={GE:parse_ge,APPROVED:parse_approved,CIVIC:parse_civic,TRANSFER:parse_transfer}
