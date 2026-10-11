"""Independent public UB Curriculum evidence; AI+X major catalogs remain separate."""
from functools import partial
import hashlib
import re
from atlas.adapters.national_curriculum_common import content,clean,course,rule,require_phrases

URLS={key:'https://www.buffalo.edu/ubcurriculum/'+key+'.html' for key in ('overview','seminar','foundations','pathways','capstone')}
URLS['undergraduate-conferral']='https://www.buffalo.edu/registrar/degree-conferral/undergraduate-degree-application-conferral.html'
# Factual rules in original wording, guarded against material source changes.
POLICIES={
'overview':('Overview of the UB Curriculum',['40 credits of study for all students','Communication Literacy 1','Scientific Literacy and Inquiry Sequence','Thematic Pathway','Global Pathway'],[
('overview','University general education scope','The overview describes40 credits across seminar, foundations, two Pathways and capstone, regardless of major. Transfer students have a different seminar amount; this headline is not summed into an exact AI+X degree total.'),
('foundation-amounts','Published foundations credit amounts','Communication Literacy1 is4 credits, CL2 is3, quantitative reasoning is4, and scientific literacy is7. Degree-specific approved choices and transfer substitutions remain unverified.'),
]),
'seminar':('The entryway to your UB education',['first semester of enrollment','199','198','lose matriculation status','9 credits per semester'],[
('seminar','Entry-semester seminar','First-year students take a three-credit199 seminar; transfer students take a one-credit198 seminar. All matriculating students must complete the seminar in their first semester, including part-time students.'),
('seminar-standing','Seminar and matriculation','The page states that students unable to take a seminar lose matriculated status and are limited to9 credits per semester as non-degree students. The linked full catalog policy remains unavailable.'),
]),
'foundations':('Communication Literacy Sequence',['ENG 105 is approved','specific CL2 course','minimum of 2 courses totaling at least 7 credits','same subject area','satisfied within the Pathways'],[
('cl1','Communication Literacy1','ENG105 is the approved CL1 course. This is a university requirement; approved transfer or other exceptions remain a separate review gap.'),
('cl2','Communication Literacy2','A second writing course develops disciplinary communication; some majors prescribe a particular CL2 course. The AI+X-specific mappings remain unverified.'),
('science','Scientific literacy and inquiry','Complete at least two courses totaling at least7 credits, including a laboratory in the same subject as one completed lecture. The full approved course/sequence pool is not mapped.'),
('diversity','Diversity within Pathways','The Diversity in the United States requirement is fulfilled within Pathways; it is not counted as an additional standalone course here.'),
]),
'pathways':('About the Pathways',['minimum of nine credit hours','Global Reflections','Language and Culture','International Experience','three different disciplinary perspectives','submit your Pathway selections'],[
('pathways','Two Pathways','Complete Global and Thematic Pathways, each at least9 credits. Global choices are Global Reflections, Language and Culture, or International Experience; the latter may use study abroad alone or with UB courses.'),
('thematic','Thematic choice and perspectives','Choose Environment, Health, Innovation, Justice or Humanity and examine the topic through three disciplinary perspectives. Exact list-combination and area rules require the linked catalog or Path Finder.'),
('pathfinder','Pathway approval record','Selections must be submitted through Path Finder to appear on the Academic Advising Report. Public offering tables assist planning; dated offerings are not a complete, timeless approved pool.'),
]),
'capstone':('UB Curriculum Capstone (UBC 399)',['one-credit course','successfully complete UBC 399','UB Seminar is a prerequisite','completed or are concurrently enrolled','repeat it in any subsequent term'],[
('capstone','University capstone','Complete the one-credit UBC399 reflective ePortfolio. This is general education and is not assumed equivalent to an AI+X major capstone.'),
('capstone-entry','Capstone registration conditions','UB Seminar must be completed before UBC399; all remaining UB Curriculum requirements must be completed or concurrently enrolled. Unsuccessful students repeat UBC399 in a later term.'),
('capstone-transfer','Transfer artifacts in capstone','Accepted transfer coursework may supply ePortfolio artifacts according to the transfer-credit and academic-advising reports.'),
]),
'undergraduate-conferral':('Requirements for a Bachelor',['minimum of 120 credit hours','30 of which','complete 90 credits','approved major','All grades must be finalized','official transcripts arrive'],[
('degree-minimum','University minimum and campus residence','Bachelor’s degrees require at least120 credit hours, including30 at UB. These are institution minima; a specific AI+X major may require more.'),
('degree-application','Graduation application','Students need90 completed credits and an approved major to apply for a degree. A graduation application in HUB is required; applying does not certify completion.'),
('final-grades','Final grades and transfer records','All grades, including study abroad and independent study, must be finalized before conferral. Incomplete grades prevent conferral. Transfer coursework must be accepted without duplicate credit and official transcripts must arrive before conferral, or the Registrar must be notified.'),
]),
}


def parse_policy(html,*,program_id,key):
    identity,guards,notes=POLICIES[key]
    root=content(html,identity);require_phrases(root,guards)
    sid='buffalo-ubc-'+key
    requirements=[rule('buffalo-ubc-'+slug,title,sid,kind='note',summary=summary) for slug,title,summary in notes]
    courses=[]
    if key=='foundations':
        courses=[course('buffalo-ubc','ENG 105',None,sid,URLS[key],4,category='human_context')]
        requirements[0]['course_ids']=[courses[0]['id']]
    if key=='capstone':
        c=course('buffalo-ubc','UBC 399','UB Curriculum Capstone',sid,URLS[key],1,category='human_context')
        c['description']='Builds a reflective portfolio linking general-education coursework with other learning experiences.'
        c['prerequisites']='Completed UB Seminar; all remaining UB Curriculum requirements completed or concurrently enrolled.'
        courses=[c];requirements[0]['course_ids']=[c['id']]
    if key=='pathways':
        table=root.find('table',id='ub-areas')
        if table is None:raise ValueError('Published Pathways offering table missing')
        observed={};groups={}
        for row in table.find_all('tr'):
            cells=[clean(c.get_text(' ',strip=True)) for c in row.find_all('td')]
            if not cells:continue
            if len(cells)!=4:raise ValueError('Pathways offering columns changed')
            match=re.fullmatch(r'([A-Z]+) (\d{3})(?:[A-Z]+)?: (.+)',cells[0])
            if not match:raise ValueError('Unrecognized course offering: '+cells[0])
            code=match[1]+' '+match[2];name=match[3]
            c=course('buffalo-ubc',code,name,sid,URLS[key],category='electives',topic=name)
            observed[c['id']]=c
            if not re.fullmatch(r'(Fall|Winter|Spring|Summer) \d{4}',cells[1]):raise ValueError('Unrecognized offering term')
            context=(cells[1],cells[2]);groups.setdefault(context,set()).add(c['id'])
        if not observed:raise ValueError('Empty offering table')
        courses=list(observed.values())
        for (term,pathway),ids in sorted(groups.items()):
            keyhash=hashlib.sha256((term+'|'+pathway).encode()).hexdigest()[:12]
            requirements.append(rule('buffalo-ubc-offerings-'+keyhash,term+' · '+pathway,sid,sorted(ids),kind='note',summary='Observed offered candidates for '+term+' in '+pathway+'. This dated subset is not a complete approved course list and does not mean every listed course is required.',category='electives'))
    return dict(id=program_id,courses=courses,requirements=requirements)


def register(program_id,sources,parsers):
    for key,url in URLS.items():
        if url not in sources:sources.append(url)
        parsers[url]=partial(parse_policy,program_id=program_id,key=key)
