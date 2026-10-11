"""Remaining linked language inventories and current Chicanx/Latinx schedules."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course,requirement,text
from atlas.adapters.ucsd_degree_policies import PID,guarded
from atlas.adapters.ucsd_warren_disciplines import heading
CHIN_URL='https://catalog.ucsd.edu/courses/CHIN.html'
JAPN_URL='https://japan.ucsd.edu/courses/course-descriptions/language-courses.html'
CLX_URL='https://cls.ucsd.edu/courses/course-offerings.html'


def node(key,title,source,summary):
    return requirement(PID,'warren-language-'+key,title,PID+'-warren-language-'+source,unit='quarter_hours',category='human_context',kind='note',summary=summary)


def parse_chinese(html):
    s=BeautifulSoup(html,'html.parser');heading(s,'Chinese Language Acquisition Courses');guarded(text(s),['placement interview','N track','M and D tracks converge'])
    rows=[];courses=[]
    for p in s.find_all('p',class_='course-name'):
        raw=text(p);m=re.fullmatch(r'CHIN (\d+[A-Z/0-9]*)\. (.+) \(([^)]+)\)',raw)
        if not m:raise ValueError('Chinese catalog course heading changed')
        if int(re.match(r'\d+',m[1])[0])>=200:continue
        d=p.find_next_sibling('p');description=text(d);prereq=description.split('Prerequisites:',1)[1].strip()if'Prerequisites:'in description else None
        credit=float(m[3])if re.fullmatch(r'\d+(?:\.\d+)?',m[3])else None
        c=course('CHIN '+m[1],m[2],PID+'-warren-language-chinese',CHIN_URL,institution='ucsd',unit='quarter_hours',credits=credit,category='human_context');c['prerequisites']=prereq
        if '/' not in m[1]:courses.append(c)
        n=node('chinese-'+m[1].lower().replace('/','-'),c['code']+' language option','chinese','Current CHIN catalog heading: '+raw+'. '+('Prerequisite/enrollment: '+prereq if prereq else'No prerequisite statement extracted.')+' Warren language use remains at most two in a Humanities/FineArts Area Study, subject to its four-unit-course rule and approval; catalog membership does not waive placement or course-specific restrictions.');n['course_ids']=[c['id']]if '/'not in m[1]else[];rows.append(n)
    if not courses:raise ValueError('No Chinese course entries')
    rows.append(node('chinese-policy','Chinese language placement and source conflict','chinese','Graduate-numbered CHIN260/296/299/500 entries are excluded; no undergraduate enrollment exception was verified. A placement interview authorizes appropriate enrollment. N is no-background, M spoken Mandarin without writing, D another Chinese language; M/D converge in the second year. First-year catalog entries are five units, whereas AAPI’s compressed language list prints four. Keep those sources separate; do not infer Warren’s treatment of a non-four-unit option or assignment to a language track.'))
    return dict(id=PID,curriculum_status='partial',courses=courses,requirements=rows)


def parse_japanese(html):
    s=BeautifulSoup(html,'html.parser');heading(s,'Japanese Language');guarded(text(s),['placement exam and an oral interview','Students who have lived in Japan'])
    rows=[]
    for h in s.find_all('h2'):
        label=text(h)
        if not label.startswith('JAPN '):continue
        m=re.match(r'JAPN (\d+) A-B-C (.+)',label)
        if not m:raise ValueError('Japanese sequence heading changed')
        rows.append(node('japanese-'+m[1],label,'japanese','Listed language sequence: '+label+'. The A–B–C sequence is preserved as a named progression, not three universally mandatory courses. This page does not supply unit values for each course. Warren language use is limited to two courses in Humanities/FineArts, with course-level eligibility and placement still applicable.'))
    if not rows:raise ValueError('No Japanese language sequences')
    rows.append(node('japanese-placement','Japanese language placement','japanese','Prior Japanese preparation uses a placement exam and oral interview. Students who lived in Japan or use Japanese at home must take the exam before fall; department placement, not the full displayed sequence, determines the appropriate course.'))
    return dict(id=PID,curriculum_status='partial',requirements=rows)


def parse_chicanx(html):
    s=BeautifulSoup(html,'html.parser');heading(s,'Course Offerings');guarded(text(s),['schedule is tentative and subject to change','Courses with * need a petition form'])
    rows=[];courses={}
    for term in ['Fall 2026','Winter 2027','Spring 2027']:
        b=heading(s,term+' Elective Courses').find_next_sibling('div')
        if not b:raise ValueError('Chicanx current term block missing')
        n=0
        for p in b.find_all('p'):
            raw=text(p)
            if not re.match(r'\*?[A-Z]+-\d',raw):continue
            m=re.fullmatch(r'(\*?)([A-Z]+)-(\d+)([A-Z]*)\.\s*(.+)',raw);ids=[]
            if m:
                code=m[2]+' '+str(int(m[3]))+m[4];c=course(code,m[5],PID+'-warren-language-chicanx',CLX_URL,institution='ucsd',unit='quarter_hours',category='human_context');courses[c['id']]=c;ids=[c['id']]
            r=node('chicanx-'+term.lower().replace(' ','-')+'-'+str(n),raw.split('.',1)[0]+' — '+term,'chicanx','Tentatively listed '+term+' option: '+raw+'. Starred entries require a program petition and are not automatically approved. Language conversation/analysis co-enrollment and topic restrictions remain attached. Apply Warren’s discipline, level, four-unit and overlap rules independently; this seasonal inventory is not a permanent full approved list.');r['course_ids']=ids;rows.append(r);n+=1
        if not n:raise ValueError('Empty current Chicanx term')
    rows.append(node('chicanx-policy','Chicanx/Latinx current schedule scope','chicanx','Only Fall2026/Winter2027/Spring2027 elective blocks are extracted; historical offerings are excluded. Courses marked * require petitions before, during or after enrollment because they are not in the formal curriculum. The CLX core descriptions and their practicum/capstone substitutions belong to the optional other degree, not mandatory AI or Warren requirements. Complete permanent-pool coverage is not inferred from a schedule.'))
    return dict(id=PID,curriculum_status='partial',courses=list(courses.values()),requirements=rows)
