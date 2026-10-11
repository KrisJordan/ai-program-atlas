"""Independent public NC State concentration/advising policies, not an audit."""
from functools import partial
from atlas.adapters.national_curriculum_common import content, rule, require_phrases
PID='ncsu-cs-ai-concentration'
PAGES={
 'department':('https://csc.ncsu.edu/academic-program/bachelor-of-science-in-computer-science-artificial-intelligence/','ADMISSION REQUIREMENTS'),
 'restrictions':('https://csc.ncsu.edu/academics/undergrad/curriculum-restrictions-and-restricted-electives/','Curriculum Restrictions and Restricted Electives'),
 'faq':('https://my.csc.ncsu.edu/undergrad-advising/advising-faq/','Advising Frequently Asked Questions'),
}
RULES={
 'department':[
 ('admission','Concentration admission',['after completing CSC 230 and CSC 316','major GPA of 3.0 or higher','GPAs between 2.75 and 2.99','depending on space','reviewed at least once per semester'], 'Apply through CSC Advising after CSC 230 and CSC 316. Major GPA should be at least 3.0; applicants at 2.75–2.99 may be considered as space permits. Review occurs at least once each semester, normally after CODA decisions.'),
 ('special-topics','Department-approved special topics',['Approved CSC 495 (special topics) in the area of AI','CSC AI Restricted Electives (6 hours)'], 'The department permits approved AI offerings of CSC 495 in the six-hour CSC AI elective block. The catalog’s finite list omits this option; approval and applicability to the student’s catalog remain to be confirmed. This is not blanket approval of every CSC 495 offering.'),
 ],
 'restrictions':[
 ('substitution','Prior substitution approval',['course syllabus, or other material','approval should be determined before taking the course'], 'Submit a syllabus or comparable content evidence for departmental evaluation before taking a proposed substitute. Approved substitutions are recorded in the student file.'),
 ('outside','Independent study and study abroad approval',['Independent Study and Study Abroad must have the department’s prior approval'], 'Prior departmental approval is required to use independent study or study abroad in CSC or Other Restricted electives. Approval does not automatically settle the narrower AI concentration allocation.'),
 ],
 'faq':[
 ('reuse','Distinct credit-bearing audit slots',['requires a unique class','one of the groups but not both','do not need credit hours to be fulfilled'], 'Each credit-bearing degree-audit slot needs a distinct course. A course eligible for several lists may fill only one of those groups; an advisor can shift it. Designated non-credit-bearing co-requirements may overlap.'),
 ('group-a','Group A excluded from concentrations',['Group A classes cannot be used for any of the CSC Concentrations'], 'Other Restricted Electives Group A courses cannot satisfy a CSC concentration merely through their Group A eligibility.'),
 ('non-gpa','Non-NC-State-GPA credit caps',['maximum of 6 hours of CSC RE and 6 hours of ORE','credit-only, credit-by-exam, transfer, study abroad'], 'At most six CSC Restricted Elective hours and six Other Restricted Elective hours may be non-NC-State-GPA credit, including transfer, study abroad, credit by exam and credit-only. These are host-category caps, not an assurance that all such credits satisfy the AI-specific lists.'),
 ('letter','Letter grades and concentration thresholds',['CSC RE and ORE must be taken for a letter grade','Concentration are required to have a C or higher in certain concentration electives'], 'Restricted electives generally require letter grades; concentration-specific C thresholds in the degree audit override generic minimums. Special credit-only research exceptions require approval. The catalog’s C versus C-minus CSC-AI-pool discrepancy remains unresolved.'),
 ('application','Advising application timing',['passed CSC 116, CSC 216, CSC 217, CSC 226','enrolled in CSC 230 and CSC 316','all classes have been passed with grades of C or higher'], 'The advising FAQ allows applications while enrolled in CSC 230/316 after passing CSC 116/216/217/226; review follows CODA and completion of these classes with C or higher. The department overview describes application after completion; verify timing with advising.'),
 ('robotics','Robotics-track exclusion',['AI Concentration + Robotics Track'], 'The AI concentration cannot be combined with the Robotics track.'),
 ('topics','Special-topic scope',['each topic can be taken only once','Individual offerings in a given semester may have additional prerequisites and restrictions'], 'Special-topic sections differ; absent a stated exception, a topic may count only once. Section prerequisites and restrictions can exceed the shell catalog minimum.'),
 ('transfer','External-course evaluation',['For all “CSC” prefix courses students should submit','External Transfer Class','official transcript to NC State’s Undergraduate Admissions'], 'Before relying on external CSC credit, submit the department’s transfer-class review form. Unlisted equivalencies require syllabus evaluation; accepted work needs an official transcript sent to Undergraduate Admissions.'),
 ],
}
def parse_policy(html,key):
 root=content(html,PAGES[key][1]);sid=PID+'-'+key+'-policy';req=[]
 for suffix,title,phrases,summary in RULES[key]:
  require_phrases(root,phrases);req.append(rule(PID+'-policy-'+suffix,title,sid,kind='note',summary=summary))
 return dict(id=PID,curriculum_status='partial',courses=[],requirements=req)
SOURCE_PARSERS={u:partial(parse_policy,key=k) for k,(u,_) in PAGES.items()}

# The official course-directory link uses /dsc/ but identifies its courses as DSA.
DSA_URL='https://catalog.ncsu.edu/course-descriptions/dsc/'
def parse_dsa(html):
 import re
 from atlas.adapters.national_curriculum_common import clean,course
 root=content(html,'Data Science (DSA)');courses=[]
 for b in root.select('.courseblock'):
  code=b.select_one('.detail-coursecode')
  if code is None:continue
  code=clean(code.get_text(' ',strip=True))
  if code not in {'DSA 405','DSA 406','DSA 412','DSA 435'}:continue
  name=clean(b.select_one('.detail-title').get_text(' ',strip=True));hours=clean(b.select_one('.detail-hours_html').get_text(' ',strip=True))
  if hours!='(1 credit hours)':raise ValueError('Reviewed DSA credit amount changed')
  text=clean(b.select_one('.courseblockextra').get_text(' ',strip=True))
  parts=re.split(r'(?:Prerequisite skills and knowledge|Skill-based prerequisites):',text,flags=re.I)
  if len(parts)!=2:raise ValueError('DSA prerequisite structure changed')
  c=course('ncsu-ai',code,name,PID+'-dsa-courses',DSA_URL,credits=1,category='ai_ml' if code in {'DSA 412','DSA 435'} else 'foundations')
  c['description']=parts[0].strip();c['prerequisites']=parts[1].strip();courses.append(c)
 if len(courses)!=4:raise ValueError('Four concentration DSA entries required')
 return dict(id=PID,curriculum_status='partial',courses=courses,requirements=[])
SOURCE_PARSERS[DSA_URL]=parse_dsa
