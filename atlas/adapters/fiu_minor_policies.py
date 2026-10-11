"""FIU public minor policy and separately identified CAI course observations."""
from atlas.adapters.national_curriculum_common import content, clean, course, rule, require_phrases
PID='florida-international-university-artificial-intelligence-minor-minor'
POLICY_URL='https://catalog.fiu.edu/policiesandprocesses/program-graduation/degree-program/undergraduate/minor-certificate'
COURSE_URL='https://catalog.fiu.edu/courses/0364401/overview-aoYks'
RULES=[
 ('declaration','Minor declaration and approval',['initiated by an academic advisor','electronic Change of Program Plan process','approved by the appropriate academic unit'], 'An academic advisor must initiate declaration through the electronic Change of Program Plan process; the appropriate academic unit must approve it. Plan with the advisor to avoid extending graduation.'),
 ('late-change','Changes after 90 credit hours',['earned 90 credit hours','extend the time required to complete degrees or result in excess credit hours','approval from the College Dean'], 'After 90 earned credit hours, adding/changing a minor requires College Dean approval when it extends degree completion or results in excess credit hours.'),
 ('award','Minor awarded with bachelor’s degree',['A minor is awarded upon completion of the bachelor’s degree','notation as a part of the degree comment on their transcript'], 'The minor is awarded upon completion of the bachelor’s degree and recorded in the transcript degree comment; this does not establish permission to complete it as a standalone post-degree credential.'),
]
def parse_policy(html):
 root=content(html,'Minor and Certificate Programs');sid='fiu-ai-minor-university-policy';result=[]
 for suffix,title,phrases,summary in RULES:
  require_phrases(root,phrases);result.append(rule(PID+'-policy-'+suffix,title,sid,kind='note',summary=summary))
 return dict(id=PID,curriculum_status='partial',requirements=result,courses=[])

def parse_course(html):
 root=content(html,'CAI4105');text=clean(root.get_text(' ',strip=True))
 require_phrases(root,['Introduction to Machine Learning','classification, clustering, structured models and recommendation system','STA 3033 or STA 2122 or STA 3145 or STA 3193 or STA 3163 or STA 3111 or STA 2023 or STA 4322','Minimum Credits 3 Maximum Credits 3','Repeat for Credit No'])
 c=course(PID,'CAI 4105','Introduction to Machine Learning','fiu-ai-minor-cai4105',COURSE_URL,credits=3,category='ai_ml')
 c.update(description='Introduces machine-learning concepts and approaches for classification, clustering, structured models and recommendation systems.',prerequisites='STA 3033 or STA 2122 or STA 3145 or STA 3193 or STA 3163 or STA 3111 or STA 2023 or STA 4322.')
 return dict(id=PID,curriculum_status='partial',requirements=[],courses=[c])
SOURCE_PARSERS={POLICY_URL:parse_policy,COURSE_URL:parse_course}
