"""Published SMU policy tabs scoped to the current named page, not draft payloads."""
import json
from bs4 import BeautifulSoup
from atlas.adapters.national_depth_curricula import CONFIG, clean, root, rule

PROGRESS='https://catalog.smu.edu/policies/undergraduate/academicprogress'
GRADES='https://catalog.smu.edu/policies/undergraduate/gradepolicies'
TRANSFER='https://catalog.smu.edu/policies/undergraduate/ugcreditpolicies'
LYLE='https://catalog.smu.edu/schools/lyle'


def tab(html,page_name,tab_name):
 root(html,page_name)
 soup=BeautifulSoup(html,'html.parser');script=soup.find('script',id='__NUXT_DATA__')
 if script is None:raise ValueError('Published policy tab payload missing')
 values=json.loads(script.string)
 pages=[x for x in values if isinstance(x,dict) and {'published','name','widgets','temporaryContent'}<=x.keys() and values[x['name']]==page_name]
 if len(pages)!=1 or values[pages[0]['published']] is not True:raise ValueError('Published policy page identity changed')
 bodies=[]
 for ref in values[pages[0]['widgets']]:
  widget=values[ref]
  if values[widget['type']]!='tabs':continue
  for ref in values[widget['data']]:
   item=values[ref]
   if values[item['name']]==tab_name:bodies.append(values[item['content']])
 if len(bodies)!=1:raise ValueError('Named published policy tab missing')
 body=BeautifulSoup(bodies[0],'html.parser');heading=body.find(['h1','h2'])
 if not heading or clean(heading.get_text())!=tab_name:raise ValueError('Published policy tab heading mismatch')
 return body


def require(body,*phrases):
 text=clean(body.get_text(' ',strip=True))
 if any(x not in text for x in phrases):raise ValueError('Material policy clause missing or changed')
 return text


def output(key,suffix,items):
 return {'id':CONFIG[key][0],'requirements':[rule(key,code,title,summary,sid=CONFIG[key][0]+'-'+suffix) for code,title,summary in items]}


def parse_progress(html,key):
 body=root(html,'Academic Advising and Satisfactory Academic Progress')
 require(body,'Students must meet with their assigned academic adviser prior to enrolling','The concentration or track does not appear on the diploma or the transcript','appears on the transcript. A specialization is not reflected on the diploma','received, approved and processed','may not double count courses across concentrations/tracks','may not double count courses across specializations','no later than upon completion of 75 credit hours','not standalone credentials')
 is_bs=key=='smu-bs'
 items=[('credential-relationship','Relationship to host degree','The '+('specialization appears on the transcript but not diploma' if is_bs else 'track appears on neither transcript nor diploma')+'. It cannot be awarded outside its associated major; multiple '+('specializations' if is_bs else 'tracks/concentrations')+' within one major may not share courses.'),('declaration-advising','Declaration and advising','Meet the assigned advisor before enrollment. Qualify for and declare the host major by 75 total credits, including examination and transfer credits. Program changes must be approved and processed through the current school records office.')]
 residence=tab(html,'Academic Advising and Satisfactory Academic Progress','SMU Resident Credit Requirement')
 require(residence,'minimum of 60 credit hours','minimum of 48 credit hours','last enrolled full-time','For further degree requirements','greater number of transferred hours','SMU online offerings','departmental examination, audition and portfolio reviews')
 items.append(('university-residency-context','University and school residency relationship','University baseline residency is 60 SMU credits after a two-year institution or 48 after a four-year institution; when there was no prior full-time enrollment, the greater transferred-credit source determines the category. SMU-campus, online, Taos, approved Abroad and departmental-examination/audition/portfolio credit qualify. Lyle publishes its own more restrictive school requirements, mapped separately. These are host-degree conditions, not an invented nine-credit track residency rule.'))
 return output(key,'progress-policy',items)


def parse_lyle(html,key):
 admission=tab(html,'Lyle School of Engineering','Undergraduate Admission')
 regs=tab(html,'Lyle School of Engineering','Undergraduate Academic Regulations')
 require(admission,'completed 24 credit hours','2.000 or higher cumulative GPA','2.500 and C- or better in all subset courses','identifiable counterparts','regional or comparable accreditation')
 rows=[r for r in admission.find_all('tr') if r.find(['td','th']) and clean(r.find(['td','th']).get_text())=='Computer Science']
 if len(rows)!=1:raise ValueError('CS admission subset row missing')
 cells=rows[0].find_all(['td','th']);subset=clean(cells[1].get_text(' ',strip=True))
 if len(cells)!=3 or clean(cells[2].get_text(' ',strip=True))!='2.500 and C- or better in all subset courses':raise ValueError('CS-specific admission grades changed')
 require(admission,'all attempts of subset courses','Grade Replacement Repeat policy','remaining graded subset courses','will not be included in the subset GPA','provided they carry grades of C - or better')
 require(regs,'A passing grade must be received in every course','2.000 or better','60 credit hours must be earned as SMU credit','including 30 credit hours','45 must be completed','may not be taken pass/fail','Majors must be officially declared','all college and university courses','all coursework attempted for the degree through enrollment at SMU','all coursework attempted for the degree in the major field of study','major department or interdisciplinary program','Of the last 60 credit hours','only under unusual circumstances','academic year of matriculation, or those of a subsequent academic year')
 return output(key,'lyle-policy',[
 ('host-admission','Admission to the host Computer Science major','Interschool admission needs 24 completed credits, cumulative GPA at least 2.000, the CS subset GPA at least 2.500 and C- or better in each subset course. Published subset: '+subset+'. Approval is by the department chair and undergraduate advising/records director. Transfer entrants must meet equivalent requirements.'),
 ('subset-gpa','Subset GPA and repeated work','CS subset GPA includes all attempts except authorized grade-replacement repeats. AP/IB holders use the remaining graded subset courses; properly forgiven old academic work is excluded. The university repeat policy is mapped separately.'),
 ('lyle-grades','School completion grades','Each prescribed course requires a passing grade. Overall all-college, SMU-attempted degree-work and major-field GPAs must each be at least 2.000. Coursework counted toward the major cannot be pass/fail. Course-specific prerequisites can require C- or better even where the school completion threshold is a passing grade.'),
 ('lyle-residency','Lyle host-degree residency','Earn 60 credits as SMU credit, including 30 in the major department or interdisciplinary program. Of the final 60 degree credits, 45 must be in courses offered by Lyle faculty; only unusual cases may receive a faculty exception. These host-degree totals are not additional track credits.'),
 ('lyle-declaration','Catalog choice and declaration','Major requirements follow the matriculation academic year or a subsequent year. Official declaration or changes go through Lyle Undergraduate Advising and Student Records.'),
 ('lyle-transfer','School transfer approval','Lyle accepts transfer work with identifiable curricular counterparts and C- or better from regionally or comparably accredited institutions. Acceptance and equivalency are reviewed, not automatic; school residency limits still apply.')])


def parse_grades(html,key):
 title='Undergraduate Grade Policies';pf=tab(html,title,'Pass/Fail Option');repeat=tab(html,title,'Grades for Repeated Courses')
 require(pf,'Courses in the academic majors and minors also are excluded','schools may have different pass/fail policies')
 require(repeat,'repeat up to six courses','D+','The course must be taken at SMU','Lyle School of Engineering.','C-','Such courses can be repeated only once','Effective for courses taken Fall 2017 or later','even if lower','only once under this policy','exact same course','prerequisite for a course already satisfactorily completed','Academic Writing (AW)','Critical Reasoning (CR)','will not count as a grade replacement repeat','Both grades will be included','Any repeats taken under the First-Year Repeat policy will count')
 return output(key,'grade-policy',[
 ('grade-option','Pass/fail and program requirements','Voluntary pass/fail generally excludes major/minor requirements; school policy controls any exception. Lyle explicitly prohibits pass/fail for coursework counted toward the major, including the associated track/specialization.'),
 ('repeat-replacement','Grade-replacement repeats','For courses from Fall 2017 onward, up to six SMU courses with D+ or lower may be repeated once at SMU under grade replacement; the later grade counts even if lower. The same course is required except permitted writing/critical-reasoning foundation substitutions. A prerequisite cannot be repeated after its dependent course has been satisfactorily completed. Withdrawn repeats do not consume the limit; former first-year repeats do. Only repeated-course hours count toward graduation; both grades remain on the record and original standing actions remain.'),
 ('repeat-average','Other Lyle repeats','Outside grade replacement, Lyle permits one repeat when the original grade is C- or lower. Both grades enter GPA and standing calculations; only the repeated-course hours count for graduation. The prerequisite-after-dependent-course prohibition still applies.')])


def parse_transfer(html,key):
 body=tab(html,'Undergraduate Credit Policies','Transfer Courses from Other Institutions')
 require(body,'no more than 30 credit hours','accredited four-year','no assurance that credit will be awarded','Education Abroad Council','prior to enrollment','October 1st','academic year preceding','principally Associates and Bachelor of Applied Science','including courses a student takes before graduating from high school','with the exception of direct enrollment through SMU','remotely or face to face','the EU is considered the home country','F-1 or J-1','full and current syllabus','must submit an official transcript','not binding to SMU')
 return output(key,'transfer-policy',[
 ('pre-transfer','Pre-matriculation transfer review','Pre-matriculation college work, including work during high school, may receive credit under university transfer-admission criteria; credit can be denied for educational reasons. Lyle equivalency and grade criteria apply.'),
 ('post-transfer','Post-matriculation transfer limits','After SMU matriculation, at most 30 credits may transfer from accredited four-year institutions; work at institutions principally awarding associate/BAS degrees is ineligible. Students designate applicable courses with academic services. Seek domestic preapproval to establish transferability; permission may still be denied for educational reasons. Without prior approval, a later petition has no guarantee of credit.'),
 ('international-transfer','International and study-away approval','US citizens need Education Abroad Council approval for non-SMU study outside the US, including remote instruction. Non-affiliated abroad programs require a petition by October 1 of the preceding academic year plus normal study-abroad application approval. Approved SMU Abroad courses are SMU coursework. F-1/J-1 students taking courses in their home country (EU treated as one home area) need each course approved before enrollment, current English syllabus documentation and a final official transcript; the 30-credit limit remains.'),
 ('foreign-evaluation','Foreign transcript evaluation','International transcripts require an official English record/translation, course information and evaluation by an SMU-accepted agency. An external evaluation recommends equivalence; SMU makes the credit decision.')])

SOURCE_PARSERS={PROGRESS:parse_progress,LYLE:parse_lyle,GRADES:parse_grades,TRANSFER:parse_transfer}
