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
 t=Tables(PROGRAM_ID,PROGRAM_ID+'-catalog',CATALOG,unit='unknown')
 t.table(tables[2],'AI & Systems: at least three courses',kind='choose_courses',count=3,interpret_choices=False)
 t.table(merged(tables[3:6]),'One course from a different specialization',kind='choose_courses',count=1,interpret_choices=False)
 t.table(merged(tables[2:6]),'Two courses from any specialization',kind='choose_courses',count=2,interpret_choices=False)
 t.group('Six courses and eighteen-hour minimum',kind='note',count=6,credits=18,summary='Six specialization courses, at least eighteen published credit hours, spanning at least two areas: at least three in AI & Systems, one outside it, and two from any area. Each course satisfies only one program requirement; cross-listed codes identify alternative registrations, not extra courses.')
 t.group('Conditional advanced and substitution options',kind='note',summary='ELEC 500-level graduate coursework may satisfy specialization requirements with permission. Unlisted substitutions need the major advisor or applicable Director of Undergraduate Studies approval and formal Degree Works entry by the official certifier.')
 t.group('Design-laboratory exclusion',kind='note',summary='The required design laboratory cannot satisfy this specialization. An extra design laboratory is a general elective, not a specialization course.')
 t.group('Advising and placement',kind='note',summary='ECE major-advisor meetings are required in junior and senior years to review specialization and design selections. Placement without transcript credit requires an approved substitute in the same area; consult the advisor.')
 require_phrases(root,['COMP 222 is a recommended prerequisite','COMP 140','COMP 182','COMP 215'])
 t.group('Computer-engineering pool preparation',kind='note',summary='The source recommends COMP 140, 182 and 215 preparation for computer-engineering options. Its marked COMP 321, COMP 432, ELEC 421/COMP 421, ELEC 429/COMP 429 and ELEC 450/COMP 450/MECH 450 options recommend COMP 222; these footnotes do not establish every course’s current enrollment prerequisites.')
 t.group('Transfer evaluation',kind='note',summary='The department requires approval of Rice course equivalence by the appropriate subject transfer-credit advisor. The linked university transfer and grading policies remain to be reviewed for this path.')
 return dict(id=PROGRAM_ID,title='AI & Systems',award_level='concentration',program_kind='concentration',courses=list(t.courses.values()),requirements=t.rules)
def parse_registrar(html):
 root=content(html,'Majors, Minors, and University Certificates')
 require_phrases(root,['area of specialization','not an official academic credential','will not appear on the transcript','during or before the spring semester of their second year','any academic year between their matriculation and graduation','may not declare a catalog year in the future','signature of the advisor and/or department chair','not required to drop or change'])
 t=Tables(PROGRAM_ID+'-registrar',PROGRAM_ID+'-registrar',REGISTRAR)
 t.group('Declared path, not a credential',kind='note',summary='Rice distinguishes a declared area of specialization from an official major concentration. An area of specialization is not an official academic credential and does not appear on the transcript. Atlas groups this formal BSECE path under its concentration category, not as a standalone award.')
 t.group('Declaration and applicable catalog',kind='note',summary='Undergraduates declare a major by spring of their second year; the declaration form also records a required specialization with advisor approval. Requirements may follow a catalog from matriculation through graduation, not a future year. Changing or dropping a specialization is requested through the registrar; a signature is not required, though advisor consultation is recommended.')
 return dict(id=PROGRAM_ID,requirements=t.rules)
SOURCE_PARSERS={CATALOG:parse,REGISTRAR:parse_registrar}
