"""Penn AI-specific FAQ and linked technical-elective evidence.

The CIS page explicitly extends approved list entries to ARIN, but its later
CSCI-specific quota rules are not imported into the AI degree.
"""
import json
import re
from atlas.adapters.national_curriculum_common import content,require_phrases
from .common import penn_course,req
PID='penn-bse-ai'
HANDBOOK='https://advising.cis.upenn.edu/tech-electives/'
INVENTORY='https://advising.cis.upenn.edu/assets/json/37cu_csci_tech_elective_list.json'


def parse_technical_policy(html):
    root=content(html,'Technical Electives')
    require_phrases(root,['ARIN degree','everything approved (i.e., yes/unrestricted/restricted)','does count as a Technical Elective for these degrees as well','the rest of this article focuses solely on the 37CU CSCI Technical Electives'])
    return dict(id=PID,requirements=[req(PID,'technical-list-scope','Scope of the linked technical-elective list',PID+'-technical-policy',kind='note',summary='The CIS handbook explicitly allows its approved technical-elective entries in ARIN. Its subsequent restricted-course quotas concern the 37-CU CSCI degree and are not applied here. The AI program separately permits Engineering, Mathematics and Natural Science courses.')])


def parse_technical_inventory(raw):
    data=json.loads(raw)
    if not isinstance(data,list) or not data:raise ValueError('Expected technical-elective JSON array')
    courses=[];approved=[];conditional=[];seen=set()
    for row in data:
        code=row.get('course4d');name=row.get('title');status=row.get('status')
        if not isinstance(code,str) or not re.fullmatch(r'[A-Z]{2,5} \d{4}',code) or not isinstance(name,str) or status not in {'yes','unrestricted','restricted','ask','no'}:raise ValueError('Technical-elective row schema or status changed')
        if code in seen:raise ValueError('Duplicate technical-elective code')
        seen.add(code)
        if status=='no':continue
        c=penn_course(code,name,PID+'-technical-inventory',INVENTORY,category='electives');courses.append(c)
        (conditional if status=='ask' else approved).append(c['id'])
    if not approved:raise ValueError('No approved technical electives observed')
    groups=[req(PID,'technical-electives','Technical Electives (3 CU)',PID+'-technical-inventory',kind='choose_credits',credits=3,category='electives',course_ids=approved,summary='Complete three course units from Engineering, Mathematics, Natural Science or the linked approved list. These listed courses are approved under the current status column; the open disciplinary categories are not an exhaustive course inventory.'),req(PID,'technical-conditional','Technical electives requiring individual approval',PID+'-technical-inventory',kind='note',course_ids=conditional,summary='These entries are marked ask and are not included as automatically approved options. Seek the CIS undergraduate chair’s decision with supporting documentation before counting one.')]
    return dict(id=PID,courses=courses,requirements=groups)


def faq_requirements(root):
    require_phrases(root,['Current Penn Engineering students, including current first- and second-year M&T students','Submit a 4-year academic plan','Declare/Update Field of Study form','with the exception of CSCI, NETS and SSE','within 8 semesters in total (or 10 semesters for M&T students)','first day of their first-year Fall Semester'])
    sid=PID+'-curriculum'
    return [req(PID,'transfer-declaration','AI transfer and declaration procedure',sid,kind='note',summary='Current Engineering students, including first- and second-year M&T students, may apply by submitting a four-year academic plan and the Declare/Update Field of Study form. Other students must follow the Engineering transfer policy, which remains inaccessible in this review.'),req(PID,'declaration-time-limit','Graduation limit for changing into AI',sid,kind='note',summary='The major change is not approved unless graduation remains possible within eight total semesters, or ten for M&T students.'),req(PID,'dual-major-restrictions','Dual majors and other degrees',sid,kind='note',summary='Engineering dual majors are permitted except CSCI, NETS and SSE. Eligibility for dual degrees or College of Arts and Sciences second majors, including VIPER, requires program advising review.'),req(PID,'incoming-mt','Incoming M&T declaration timing',sid,kind='note',summary='Incoming first-year M&T students may begin declaring AI on the first day of their first fall semester using the field-of-study form.')]
