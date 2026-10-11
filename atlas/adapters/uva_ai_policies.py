"""Public UVA advising policies, scoped separately to BACS and BSCS."""
from functools import partial
from atlas.adapters.national_curriculum_common import content,rule,require_phrases
PAGES={
 'policies':('https://uvacsadvising.org/policies.html','Policies and Procedures'),
 'transfer':('https://uvacsadvising.org/transfer.html','Transferring Courses to UVA'),
 'college-minor':('https://college.as.virginia.edu/minor-declaration-and-policy','Minor Declaration and Policy'),
}
RULES={
 'policies':[
 ('prerequisites','Enforced course prerequisites',['enforces all course prerequisites listed in course descriptions','check all prerequisites at the start of each semester'], 'CS checks published prerequisites and required prerequisite grades at the start of each semester; successful registration alone does not establish eligibility. Individual course prerequisites still need separate verification.'),
 ('overlap-content','CS elective content overlap',['Two electives with significant overlap of material cannot both count toward the CS degree'], 'Two substantially overlapping electives cannot both count toward the CS degree. General 3000-level CS elective eligibility does not expand the concentration’s specifically approved lists.'),
 ('internships','Internships do not earn CS degree credit',['internships','cannot grant course credit','UNST 3910 or UNST 3920','cannot be used toward degree requirements'], 'An internship does not itself earn CS course credit. The special UNST internship courses may support enrollment/visa purposes but do not fulfill degree requirements or the AI concentration.'),
 ('term-transfer','External study during regular terms',['explicit written permission from your dean’s office','will not be able to transfer any credits','does not normally apply to summer or J-term'], 'External coursework during a regular UVA fall/spring semester requires explicit written dean permission to transfer back. The regular-term restriction normally does not apply in summer or J-term; separate school and course approval rules still apply.'),
 ],
 'transfer':[
 ('transfer-review','Review external courses before enrollment',['approval is required before you take the course','Link to course syllabus or a PDF','school’s procedures for the paperwork approval'], 'For a course absent from the student’s school pre-approved list, request the relevant CS program director’s review before enrollment, including the syllabus and proposed equivalence; then complete school approval paperwork.'),
 ('transfer-posting','Transcript and prerequisite posting',['official transcripts','appropriate dean’s office','completed and the grade is shown in SIS'], 'Send the external institution’s official transcript to the appropriate dean’s office. External work cannot meet a UVA prerequisite until completed and posted with its grade in SIS.'),
 ],
 'college-minor':[
 ('minor-conflict','Unresolved BACS major/minor reuse',['Classes used to satisfy a minor requirement cannot also be used to satisfy requirements for a major or different minor'], 'College policy prohibits using a minor course for a major or another minor. The AI concentration page says concentration courses may also satisfy any major/minor, and all BACS concentration courses also meet major requirements. Whether the AI statement is an authorized exception is unverified; do not treat it as blanket reuse permission.'),
 ],
}
def parse_policy(html,pid,key):
 root=content(html,PAGES[key][1]);sid=pid+'-'+key+'-policy';requirements=[]
 if key=='college-minor' and pid!='uva-bacs-ai-concentration':raise ValueError('College minor policy is not a BSCS rule')
 for suffix,title,phrases,summary in RULES[key]:
  require_phrases(root,phrases);requirements.append(rule(pid+'-policy-'+suffix,title,sid,kind='note',summary=summary))
 if key=='transfer':
  require_phrases(root,['College students must submit a form before they take it','SEAS does not require anything in advance if the course is pre-approved'])
  text='BACS students must submit the College transfer form before taking even a pre-approved course.' if pid=='uva-bacs-ai-concentration' else 'For pre-approved courses, SEAS does not require advance course-approval paperwork; follow its post-completion process. The separate written-permission rule for concurrent fall/spring enrollment still applies.'
  requirements.append(rule(pid+'-policy-preapproved','School-specific pre-approved transfer procedure',sid,kind='note',summary=text))
 if key=='policies' and pid=='uva-bscs-ai-concentration':
  require_phrases(root,['SEAS has no restriction on allowing a course to count for two majors','SEAS has no restriction on allowing a course to count for both a SEAS major and a minor'])
  requirements.append(rule(pid+'-policy-seas-reuse','SEAS major and minor overlap',sid,kind='note',summary='The advising policy reports no SEAS restriction on sharing a course between two majors or a SEAS major and a minor. This does not waive another school’s or credential’s requirements.'))
 return dict(id=pid,curriculum_status='partial',courses=[],requirements=requirements)
def parsers(pid):
 return {u:partial(parse_policy,pid=pid,key=k) for k,(u,_) in PAGES.items() if k!='college-minor' or pid=='uva-bacs-ai-concentration'}
