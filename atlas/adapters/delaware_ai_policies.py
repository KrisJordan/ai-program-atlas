"""Public college/university rules independently of the inaccessible degree catalog."""
from functools import partial
from atlas.adapters.national_curriculum_common import content,rule,require_phrases
PID='delaware-ai-engineering-major'
PAGES={
'advising':('https://engr.udel.edu/undergraduate-education/undergraduate-advisement/','Undergraduate Advisement'),
'college-transfer':('https://engr.udel.edu/undergraduate-education/transfer-credit-information/','Transfer Credit Information'),
 'transfer-policy':('https://www.udel.edu/academics/registrar/students/transfer-credit/how-to/','How to Transfer UNDERGRADUATE Courses to UD'),
}
RULES={
'advising':[
 ('catalog','Entry-year catalog and degree audit',['degree requirements specified in the UG Catalog for the year you entered','All requirements on your Audit must be satisfied'], 'Complete the requirements of the undergraduate catalog for the year of entry and satisfy the degree audit. The public sample AI plan is not a substitute for that audit.'),
 ('exceptions','Approved substitutions and waivers',['all course exceptions (substitutions, waivers, etc.) have been submitted and approved in the Stellic system'], 'Have all substitutions and waivers formally submitted and approved in Stellic before graduation clearance.'),
 ('checkout','Senior checkout',['Complete a Senior Checkout meeting','first two weeks of your senior year'], 'Arrange departmental senior checkout with the academic advisor within the first two weeks of senior year; confirm all major and other credential requirements and the expected graduation term.'),
 ('incomplete','Resolve unfinished course grades',['Complete any coursework for courses with a Sustaining (S) or Incomplete (I) grade'], 'Complete coursework carrying Sustaining or Incomplete grades before graduation clearance.'),
],
'college-transfer':[
 ('prior-transfer','Prior transfer evaluation',['TCE Form BEFORE you take a course','Department Approval','course syllabus'], 'Submit the Transfer Credit Evaluation form before external enrollment. Unlisted courses require a syllabus-based departmental equivalency decision and college review; otherwise equivalency changes may prevent counting the work.'),
],
 'transfer-policy':[
 ('transfer-grade','Transfer course eligibility',['accredited institution that issues college-level degrees','standard letter grade','C- or better','eligible to count directly toward a college-level degree'], 'Transfer courses must align with UD curricula, be eligible for a degree at the originating accredited institution, and earn a standard letter grade equivalent to C-minus or higher. International institutions require the stated national authorization.'),
 ('transfer-exclusions','Excluded transfer evidence',['does not transfer remedial classes','basic/introductory computing','religious study','Not be listed as “transfer credit,” “credit by exam,” nor “test credit”'], 'The transfer-course route excludes remedial and English-language instruction, basic computing, religious study and government-mandated political content. A sending transcript’s transfer/test-credit notation does not itself establish transferable coursework.'),
 ('conversion','UD semester credits and transfer GPA',['1 quarter cr. = .67 UD semester cr.','not included in the UD GPA'], 'UD uses semester credits for transfer conversion: one quarter credit becomes 0.67 UD semester credit. External grades do not enter UD GPA or appear as grades on the official UD transcript.'),
 ('equivalence','Course equivalence evaluation',['content covers at least 70%','Official Syllabus'], 'When a course lacks a reviewed equivalency, submit its description and official syllabus for departmental evaluation. A specific UD equivalent requires at least 70% content alignment; elective credit may be awarded instead.'),
 ('approval','Current-student transfer approval',['MUST submit a TCE form to their Asst. Dean for review and approval','conflict with UD’s Residency Requirement','at least 6 weeks prior'], 'Current undergraduates require Assistant Dean TCE approval. Discuss degree applicability and residency before external enrollment; students graduating that term should initiate the process at least six weeks beforehand. The numeric residency requirement is not supplied by this page.'),
 ('breadth','Transfer breadth eligibility',['Whether a student may count a specific UD or transfer course toward University breadth is tied to their major'], 'An elective equivalency approved for university breadth is not automatically usable by every major; confirm applicability with the academic advisor or Assistant Dean.'),
],
}
def parse_policy(html,key):
 root=content(html,PAGES[key][1]);sid=PID+'-'+key+'-policy';req=[]
 for suffix,title,phrases,summary in RULES[key]:
  require_phrases(root,phrases);req.append(rule(PID+'-policy-'+suffix,title,sid,kind='note',summary=summary))
 return dict(id=PID,curriculum_status='partial',courses=[],requirements=req)
SOURCE_PARSERS={u:partial(parse_policy,key=k) for k,(u,_) in PAGES.items()}
