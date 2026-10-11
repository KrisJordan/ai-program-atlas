"""Local Tepper concentration policies and course facts; no host-degree replay."""
from functools import partial
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import content, clean, require_phrases, rule, course
PID='cmu-ai-business-concentration'
TEPPER='https://coursecatalog.web.cmu.edu/schools-colleges/tepper/'
REGULATIONS='https://coursecatalog.web.cmu.edu/aboutcmu/undergraduateacademicregulations/'
SITE='https://www.cmu.edu/tepper/programs/undergraduate-programs/business-administration'
ADVISING='https://www.cmu.edu/tepper/programs/undergraduate-programs/advising'
BUSINESS='https://coursecatalog.web.cmu.edu/schools-colleges/tepper/undergraduatebusinessadministrationprogram/courses/'
ECON='https://coursecatalog.web.cmu.edu/schools-colleges/tepper/undergraduateeconomicsprogram/courses/'
CODES={'business':{'70-445','70-317','70-441','70-389','70-334','70-374','70-467','70-498'},'economics':{'73-367'}}


def note(key,title,sid,text):
    return rule(PID+'-'+key,title,PID+'-'+sid,kind='note',summary=text)


def parse_tepper(html):
    root=content(html,'Tepper School of Business')
    require_phrases(root,[
        'For business administration majors, courses in the concentration and business elective requirements are not allowed to double count',
        'including minor or additional major pursuits',
        'Students must earn letter grades (A through D) for required degree courses',
        'Spring 2020 and Spring 2026 CMUQ Special Pass/No Pass election',
        'Repeating courses does not replace the previously earned grade',
        'Students must earn a final grade of C- or higher to receive transfer credit unless otherwise noted by an individual approval',
        'Only 1 course can transfer between the concentration and business elective course requirements',
        'CMU Washington Semester and CMU-Qatar courses are exempt from this transfer course policy',
        'Students pursuing a Tepper School dual degree are subject to the transfer policy for primary majors',
        'including the concentration requirement for business administration majors',
        'the concentration requirement for the business administration dual degree',
        'Independent study cannot be used as a substitute for an existing course',
        'cannot be a substitute for a curriculum requirement',
        'Earn a cumulative QPA of 2.0 or higher',
    ])
    return dict(id=PID,requirements=[
        note('college-overlap','Concentration overlap limit','tepper-policy','For Business Administration majors, concentration and business-elective courses cannot double count toward other degree requirements, including a minor or additional major. This concentration does not certify completion of the host BS.'),
        note('college-grades','Required-course letter grades and repeat treatment','tepper-policy','Required degree courses need A–D letter grades. P is permitted for Core @ CMU and the expressly named Spring 2020 / Spring 2026 CMUQ special elections; those historical exceptions do not create a current concentration pass/fail option. Repeated courses retain both grades in QPA. The host degree requires cumulative QPA of at least 2.0; no separate concentration QPA threshold is stated here.'),
        note('college-transfer','Shared concentration/business-elective transfer cap','tepper-policy','At most one external course may apply across the concentration and business-elective requirements together, after Tepper equivalency review. Normally C− or higher is required unless an individual approval specifies otherwise. CMU Washington Semester and CMU-Qatar courses are exempt from this transfer policy; online/community-college courses depend on department policy. Tepper dual-degree students follow the primary-major transfer policy. The host degree also has broader transfer limits; these local observations do not approve any individual transfer.'),
        note('dual-degree-context','Dual degree differs from an additional major','tepper-policy','A Business Administration dual degree still requires a concentration. The primary/dual degree can replace the other program’s minor when completed no later than that degree. This is distinct from the additional-major concentration waiver stated on the BS page; neither route automatically awards this named AI concentration.'),
        note('independent-study','No independent-study replacement of a required course','tepper-policy','Independent study cannot replace an existing catalog course or a curriculum requirement. Its general availability is not an unlisted AI concentration elective permission.'),
    ])


def parse_regulations(html):
    root=content(html,'Undergraduate Academic Regulations')
    require_phrases(root,['Residency Requirement','minimum of four semesters of full-time study','at least 180 units of coursework','Deviation from these policies requires action by the dean', 'Only official and final college or university transcripts', 'All units required for an undergraduate degree','within eight years of the date on which the degree is granted','extended by the Dean'])
    return dict(id=PID,requirements=[
        note('host-residency','Host-degree residency context','university-policy','The bachelor’s degree requires at least four full-time semesters (or part-time equivalent) and 180 CMU units; more restrictive college rules may apply and deviations require the home-college dean. This is a host-degree condition, not an extra 180-unit concentration or a claim that the full BS inventory is mapped.'),
        note('transfer-record','Official transfer records','university-policy','Transfer credit requires an official final college/university transcript and applicable college/department approval. External transfer grades do not enter the CMU QPA, whereas university cross-registration grades do. This does not waive the Tepper shared one-course concentration/business-elective transfer cap.'),
        note('time-limit','Host-degree credit age','university-policy','Units used toward the undergraduate degree must normally have been earned within eight years of graduation. The college dean may extend the period under the published course-relevance, preparation and legitimate-delay conditions; exceptions are not automatic.'),
    ])


def parse_site(html):
    root=content(html,'Business Administration')
    require_phrases(root,['AI and Business','For students in the Business major, a concentration','Students are encouraged to declare their concentration by the end of their sophomore year','Courses taken to meet concentration requirements are not allowed to double count'])
    return dict(id=PID,requirements=[note('declaration','Declaration timing recommendation','business-site','The Business major offers this concentration and encourages declaration by the end of sophomore year. This is a recommendation, not a published eligibility deadline. Concentration selection is discussed with the academic advisor; no independent admission test or automatic transcript notation is inferred.')])


def parse_advising(html):
    root=content(html,'Academic Advising');require_phrases(root,['Students are expected to meet with their advisors at least once each semester'])
    return dict(id=PID,requirements=[note('semester-advising','Regular academic advising','advising','Tepper students are expected to meet their academic advisor at least once each semester to select courses and review progress. The concentration catalog also directs consultation when selecting a concentration.')])


def parse_courses(key,html):
    title='Undergraduate Business Administration Courses' if key=='business' else 'Undergraduate Economics Courses'
    root=content(html,title);url=BUSINESS if key=='business' else ECON;sid=PID+'-'+key+'-courses';out=[]
    for b in root.find_all('dl',class_='courseblock'):
        h=b.find('dt');body=b.find('dd')
        if not h or not body:raise ValueError('CMU course block changed')
        match=re.fullmatch(r'(\d{2}-\d{3})\s+(.+)',clean(h.get_text(' ',strip=True)))
        if not match or match[1] not in CODES[key]:continue
        copy=BeautifulSoup(str(body),'html.parser')
        for br in copy.find_all('br'):br.replace_with('\n')
        lines=[clean(x) for x in copy.get_text(' ',strip=False).splitlines() if clean(x)]
        amount=re.fullmatch(r'[^:]+:\s*(\d+(?:\.\d+)?) units',lines[0])
        if not amount:raise ValueError('Course units require review')
        c=course(PID,match[1],match[2],sid,url,credits=float(amount[1]),unit='units',category='applications')
        prereq=[re.sub(r'^Prerequisites?:\s*','',x) for x in lines if re.match(r'^Prerequisites?:',x)]
        if len(prereq)>1:raise ValueError('Repeated prerequisite field')
        c['prerequisites']=prereq[0] if prereq else None;out.append(c)
    if {c['code'] for c in out}!=CODES[key] or len(out)!=len(CODES[key]):raise ValueError('Concentration course metadata missing or duplicated')
    return dict(id=PID,courses=out,requirements=[])


SOURCE_PARSERS={TEPPER:parse_tepper,REGULATIONS:parse_regulations,SITE:parse_site,ADVISING:parse_advising,BUSINESS:partial(parse_courses,'business'),ECON:partial(parse_courses,'economics')}


def parse_host_context(html):
    root=content(html,'Business Administration, B.S.')
    panel=root.find(id='degreerequirementstextcontainer') or root
    require_phrases(panel,['For students electing to complete an additional major, the concentration requirement is waived','students must complete 27 units of business elective courses as part of the waived concentration requirement'])
    return dict(id=PID,requirements=[note('host-waiver','Additional-major waiver is not completion of this concentration','catalog','The Business Administration BS ordinarily requires a concentration. Students completing an additional major may waive the concentration and minor requirements and complete 27 business-elective units in place of the concentration. That host-degree waiver does not award the named AI and Business concentration; completing this concentration requires its published four-course, minimum-36-unit plan.')])
