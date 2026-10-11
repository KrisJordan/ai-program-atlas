"""Finite discipline lists linked by Warren; no optional degree reconstructed."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, text, slug
from atlas.adapters.ucsd_college_context import requirement
from atlas.adapters.ucsd_degree_policies import PID,guarded
URLS={'aapi':'https://catalog.ucsd.edu/curric/AAPI.html','chinese':'https://catalog.ucsd.edu/curric/CHIN.html','latin-american':'https://catalog.ucsd.edu/curric/LATI-ug.html','japanese':'https://japan.ucsd.edu/courses/course-descriptions/non-language-courses.html','jewish':'https://jewishstudies.ucsd.edu/courses/course_listing.html'}


def node(key,title,source,summary,parent=None):
    return requirement(PID,'warren-discipline-'+key,title,PID+'-warren-discipline-'+source,unit='quarter_hours',category='human_context',kind='note',parent=parent,summary=summary)


def heading(s,label):
    h=next((h for h in s.find_all(['h1','h2','h3','h4'])if text(h)==label),None)
    if not h:raise ValueError('Discipline pool heading missing: '+label)
    return h


def between(s,start,stop=None):
    h=heading(s,start);parts=[]
    for item in h.find_all_next():
        if stop and item.name in ['h2','h3']and text(item)==stop:break
        if item.name=='p' or (item.name=='li' and not item.find('p')):
            copy=BeautifulSoup(str(item),'html.parser')
            for br in copy.find_all('br'):br.replace_with('\n')
            for line in copy.get_text().splitlines():
                line=re.sub(r'\s+',' ',line).strip()
                if re.match(r'[A-Z]+\s+\d',line):parts.append(line)
    return parts


def parse(html,key):
    s=BeautifulSoup(html,'html.parser');rows=[]
    if key=='aapi':
        heading(s,'Asian American and Pacific Islander Studies Minor');rows=between(s,'CORE COURSES')
    elif key=='chinese':
        rows=between(s,'Courses Applicable for the Chinese Studies Major and/or Minor Offered by Various Departments and Programs')
    elif key=='latin-american':
        rows=between(s,'Courses that Satisfy Undergraduate Degree Elective Requirements in Latin American Studies','Methods Courses')
    elif key=='jewish':
        rows=between(s,'Jewish Studies Major Courses','Past Course Offerings 2025-2026')
    elif key=='japanese':
        heading(s,'Non Language Courses');guarded(text(s),['more than 33% of the course content concerns Japan'])
        for t in s.find_all('table'):
            family=text(t.find_previous('h2'))
            if family=='Graduate School of International Relations and Pacific Studies':continue
            for tr in t.find_all('tr'):
                cells=[text(c)for c in tr.find_all(['th','td'])]
                if len(cells)<2 or cells[0]in ['Course','Course Name']:continue
                if not re.match(r'\*?\s*[A-Z]+\s+\d',cells[0]):raise ValueError('Japanese option code changed')
                rows.append(re.sub(r'^([A-Z]+\s+\d+[A-Z]*)\s+',r'\1. ',cells[0]))
    else:raise ValueError('Unknown discipline')
    if not rows:raise ValueError('Empty discipline pool')
    root=node(key,key.title()+' linked approved discipline pool',key,'Conditional Warren interdisciplinary Area Study options from the linked discipline source. Apply Warren’s three four-unit courses, two upper-division, one course atUCSD, noncontiguous discipline and overlap rules. Language is limited to two and Humanities/FineArts only. This list does not impose the other program’s major/minor curriculum. Topic, petition, language, cross-list and graduate-level restrictions remain literal; program approval is not a guarantee of course availability.');nodes=[root];courses={}
    for i,raw in enumerate(rows):
        m=re.match(r'([A-Z]+)\s+(\d+[A-Z]*)\.\s+(.+)',raw);ids=[]
        if m and int(re.match(r'\d+',m[2])[0])<200:
            credit=re.search(r'\((\d+(?:\.\d+)?)\)\s*$',m[3]);name=re.sub(r'\s*\(\d+(?:\.\d+)?\)\s*$','',m[3]);c=course(m[1]+' '+m[2],name,PID+'-warren-discipline-'+key,URLS[key],institution='ucsd',unit='quarter_hours',credits=float(credit[1])if credit else None,category='human_context');courses[c['id']]=c;ids=[c['id']]
        n=node(key+'-row-'+str(i),raw.split('.',1)[0],key,'Published approved-list expression: '+raw+'. Cross-list/sequence/range/conditional notation remains one qualified row; no independent alternative, credit split, or undergraduate permission for a graduate-numbered alternative is inferred.',root['id']);n['course_ids']=ids;nodes.append(n)
    if key=='aapi':nodes.append(node(key+'-scope','AAPI list qualifications',key,'The source distinguishes core, Asian-American-content electives, optional Asia-focused courses and optional language. Do not treat Asia-focused or language eligibility as unrestricted. Quarterly AAPI schedules are not the complete approved pool.'))
    if key=='latin-american':nodes.append(node(key+'-scope','Latin American course-topic qualification',key,'Electives marked “when Latin American content” need that topic; these are conditional options. Published source repeats USP135; the requirement observations preserve the duplicate but course metadata deduplicates. Methods-only course lists and the entire optional Latin American Studies degree are not imposed on the AI major.'))
    if key=='japanese':nodes.append(node(key+'-scope','Japanese graduate block and language route',key,'Starred Literature/Music options require more than33% Japan content and program confirmation. The page’s separate Graduate School of International Relations and Pacific Studies table is excluded from this undergraduate option inventory; no undergraduate permission was verified. Warren’s language/discipline limit still applies; this parser inventories the non-language page only.'))
    if key=='jewish':nodes.append(node(key+'-scope','Jewish list version and conditional options',key,'Use the full discipline list separately from term projections/history. The projected2026–27 section labels winter/spring2026; those schedule dates are not silently corrected or used to certify current enrollment. Compressed undergraduate/graduate cross-lists, directed study and language options require their own eligibility and Warren area approval.'))
    return dict(id=PID,curriculum_status='partial',courses=list(courses.values()),requirements=nodes)
