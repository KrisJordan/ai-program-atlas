"""Declared BSECE specialization, explicitly not a separate Rice credential."""
from copy import deepcopy
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import content, clean, require_phrases
from atlas.adapters.degree_table_observations import Tables
PROGRAM_ID='rice-ece-ai-systems-specialization'
CATALOG='https://ga.rice.edu/programs-study/departments-programs/engineering/electrical-computer-engineering/electrical-computer-engineering-bsece/'
REGISTRAR='https://registrar.rice.edu/students/majors-minors-and-university-certificates'
SOURCES=(CATALOG,REGISTRAR)
def merged(tables):
 out=BeautifulSoup('<table><tbody></tbody></table>','html.parser');seen=set()
 for table in tables:
  for row in table.select('tr'):
   if not row.select_one('td.codecol'):continue
   signature=clean(row.get_text(' ',strip=True))
   if signature not in seen:out.tbody.append(deepcopy(row));seen.add(signature)
 return out.table
def parse(html):
 root=content(html,'Bachelor of Science in Electrical and Computer Engineering (BSECE)')
 if not any(clean(h.get_text(' ',strip=True))=='Area of Specialization: AI & Systems' for h in root.find_all(['h2','h3','h4'])):raise ValueError('AI & Systems section heading absent')
 require_phrases(root,['A total of 6 courses (minimum of 18 credit hours)','at least two areas of specialization','minimum of 3 courses','1 course from an area of specialization outside','2 courses from any area','500-level','with permission','A course can satisfy only one program requirement','does not count as a specialization course','as a General Elective, not as a specialization course','at least during their junior and senior years','formally applied and entered into Degree Works'])
 tables=root.select('table.sc_courselist')
 if len(tables)!=6:raise ValueError('BSECE table structure changed')
 for sup in root.find_all('sup'):sup.decompose()
 t=Tables(PROGRAM_ID,PROGRAM_ID+'-catalog',CATALOG,unit='semester_hours')
 t.table(tables[2],'AI & Systems: at least three courses',kind='choose_courses',count=3,interpret_choices=False)
 t.table(merged(tables[3:6]),'One course from a different specialization',kind='choose_courses',count=1,interpret_choices=False)
 t.table(merged(tables[2:6]),'Two courses from any specialization',kind='choose_courses',count=2,interpret_choices=False)
 t.group('Six courses and eighteen-hour minimum',kind='note',count=6,credits=18,summary='Six specialization courses, at least eighteen semester credit hours, spanning at least two areas: at least three in AI & Systems, one outside it, and two from any area. Each course satisfies only one program requirement; cross-listed codes identify alternative registrations, not extra courses.')
 t.group('Conditional advanced and substitution options',kind='note',summary='ELEC 500-level graduate coursework may satisfy specialization requirements with permission. Unlisted substitutions need the major advisor or applicable Director of Undergraduate Studies approval and formal Degree Works entry by the official certifier.')
 t.group('Design-laboratory exclusion',kind='note',summary='The required design laboratory cannot satisfy this specialization. An extra design laboratory is a general elective, not a specialization course.')
 t.group('Advising and placement',kind='note',summary='ECE major-advisor meetings are required in junior and senior years to review specialization and design selections. Placement without transcript credit requires an approved substitute in the same area; consult the advisor.')
 require_phrases(root,['COMP 222 is a recommended prerequisite','COMP 140','COMP 182','COMP 215'])
 t.group('Computer-engineering pool preparation',kind='note',summary='The source recommends COMP 140, 182 and 215 preparation for computer-engineering options. Its marked COMP 321, COMP 432, ELEC 421/COMP 421, ELEC 429/COMP 429 and ELEC 450/COMP 450/MECH 450 options recommend COMP 222; these footnotes do not establish every course’s current enrollment prerequisites.')
 t.group('Transfer evaluation',kind='note',summary='The department requires approval of Rice course equivalence by the appropriate subject transfer-credit advisor. The linked university transfer and grading policies also apply; their rules are recorded under separate policy sources.')
 return dict(id=PROGRAM_ID,title='AI & Systems',award_level='concentration',program_kind='concentration',courses=list(t.courses.values()),requirements=t.rules)
def parse_registrar(html):
 root=content(html,'Majors, Minors, and University Certificates')
 require_phrases(root,['area of specialization','not an official academic credential','will not appear on the transcript','during or before the spring semester of their second year','any academic year between their matriculation and graduation','may not declare a catalog year in the future','signature of the advisor and/or department chair','not required to drop or change'])
 t=Tables(PROGRAM_ID+'-registrar',PROGRAM_ID+'-registrar',REGISTRAR)
 t.group('Declared path, not a credential',kind='note',summary='Rice distinguishes a declared area of specialization from an official major concentration. An area of specialization is not an official academic credential and does not appear on the transcript. Atlas groups this formal BSECE path under its concentration category, not as a standalone award.')
 t.group('Declaration and applicable catalog',kind='note',summary='Undergraduates declare a major by spring of their second year; the declaration form also records a required specialization with advisor approval. Requirements may follow a catalog from matriculation through graduation, not a future year. Changing or dropping a specialization is requested through the registrar; a signature is not required, though advisor consultation is recommended.')
 return dict(id=PROGRAM_ID,requirements=t.rules)
SOURCE_PARSERS={CATALOG:parse,REGISTRAR:parse_registrar}

GRADUATION='https://ga.rice.edu/undergraduate-students/academic-policies-procedures/graduation-requirements/'
TRANSFER='https://ga.rice.edu/undergraduate-students/academic-policies-procedures/transfer-credit/'
GRADES='https://ga.rice.edu/undergraduate-students/academic-policies-procedures/grades/'
REGISTRATION='https://ga.rice.edu/undergraduate-students/academic-policies-procedures/registration/'
POLICIES={
 'graduation':(GRADUATION,'Graduation Requirements',[
  ('Major-grade scope',['Complete all Rice coursework that satisfy major, minor, and/or certificate requirements','2.00 or higher','standard letter grade earned','not on a Pass/Fail basis'],'Specialization courses are part of the BSECE major: major coursework needs a combined GPA of at least 2.00 and the earned letter grade, not elected pass/fail. This is a major-wide GPA, not a separately invented AI-specialization GPA.'),
  ('Major residence scope',['more than half of the upper-level coursework required by the declared major(s)','at Rice University','some may specify a higher proportion'],'More than half the upper-level coursework required by each declared major must be completed at Rice, subject to a higher departmental proportion. The source does not impose a separate half-of-specialization calculation.'),
  ('Uncovering elected pass grades',['P grade be replaced with the letter grade earned','will not be restored'],'A P in coursework applied to a major is replaced by the underlying letter grade, either by student request or final degree audit; the P is not subsequently restored.'),
  ('Host-degree residence discrepancy',['up to one summer semester','at least four semesters'],'The host-degree graduation page permits one summer among four full-time resident semesters, while the transfer page says four fall/spring semesters. This remains an unresolved host-degree source discrepancy; it is not converted into an invented local specialization minimum.')]),
 'transfer':(TRANSFER,'Transfer Credit',[
  ('Equivalent credit and grade',['grade of at least a C-','may not transfer courses taken pass/fail','designated transfer credit advisor','Rice equivalent'],'External coursework needs Rice-equivalent approval by the subject transfer advisor and an official transcript. The minimum external grade is C− or equivalent; externally elected pass/fail credit is ineligible. General TRAN elective credit does not establish a specialization-equivalent course.'),
  ('Transfer limits and duplicate credit',['limited to 15 semester hours of summer school transfer credit','restriction is waived','courses previously completed at Rice with a passing grade','exception to the repeat transfer credit rule'],'After matriculation, summer transfer is limited to fifteen semester hours except official summer study abroad. A previously passed Rice course ordinarily cannot earn transfer credit again, except repeatable courses or an extraordinary approved exception. Departments may impose further restrictions; the BSECE page supplies its advisor-approval rule.'),
  ('Semester-hour definition and evaluation',['converted to semester hours','Office of the Registrar will determine appropriate transferable credit hours','no instance will a course transfer in with credit greater'],'Rice normalizes external credits into semester hours; the registrar determines equivalence and level, never exceeding the original semester-hour equivalent. No conversion is inferred from the academic calendar.'),
  ('International and off-campus approval',['professional course-by-course evaluation','Office of Study Abroad','Office of the Registrar'],'International transfer generally needs a professional course-by-course evaluation; official study-abroad programs follow the study-abroad approval process and documented exceptions. External-equivalent approval remains necessary for this specialization.')]),
 'grades':(GRADES,'Grades',[
  ('Elected P/F and S/U distinction',['May not take as Pass/Fail any course used to meet the requirements for their major','14 semester hours','Satisfactory/Unsatisfactory','no credit will be awarded if a grade of U'],'Major requirements cannot remain elected pass/fail. General electives have separate P/F limits (one per semester, four courses and fourteen semester hours overall). Instructor-designated S/U is a different grading basis; an S earns university credit, but this alone does not waive the major letter-grade rule or establish specialization approval.'),
  ('Unfinished and audit coursework',['There are no credit hours associated with audited courses','may not receive a grade of INC','final semester'],'Audited courses carry no credit. Degree candidates cannot receive an incomplete in their final semester; outstanding coursework must be resolved under the published deadlines before conferral.')]),
 'registration':(REGISTRATION,'Registration',[
  ('Semester credits and advanced-course registration',['15 to 18 semester credit hours','500-and-above','electronic course registration override','instructor permission required'],'Rice undergraduate course loads are expressed in semester credit hours. Registration in graduate-level courses (500 and above) needs an electronic instructor-permission override, in addition to the specialization’s permission to apply that course.'),
  ('Repeats and cross-list credit',['credit is awarded only for the course with the highest grade','all attempts','cross-listed'],'Repeating a passed course awards credit only for the attempt with the highest grade, while all attempts remain in the GPA; designated repeatable courses follow their published limits. Cross-listed registrations do not manufacture separate course completions.')])}
def parse_policy(html,key):
 url,heading,specs=POLICIES[key];root=content(html,heading)
 t=Tables(PROGRAM_ID+'-'+key,PROGRAM_ID+'-'+key,url,unit='semester_hours')
 for title,markers,summary in specs:
  require_phrases(root,markers);t.group(title,kind='note',summary=summary)
 return dict(id=PROGRAM_ID,requirements=t.rules)
SOURCES += tuple(x[0] for x in POLICIES.values())
SOURCE_PARSERS.update({value[0]:(lambda html,key=key:parse_policy(html,key)) for key,value in POLICIES.items()})
