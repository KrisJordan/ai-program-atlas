"""Marshall current first-year/transfer pools and reviewed writing-list text."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, slug, text
from atlas.adapters.ucsd_college_context import requirement
from atlas.adapters.ucsd_degree_policies import PID, guarded
from atlas.adapters.ucsd_revelle_pools import normal
FIRST_URL='https://marshall.ucsd.edu/academics/first-year-ge.html'
TRANSFER_URL='https://marshall.ucsd.edu/academics/transfer-ge.html'
WRITING_URL='https://marshall.ucsd.edu/_files/academics/sigwriting.pdf'
SELECTOR_URL='https://stark.ucsd.edu/public/tmc_breadth/'


def node(key,title,source='first',**kw):
    return requirement(PID,'marshall-'+key,title,PID+'-marshall-'+source,unit='quarter_hours',category='human_context',**kw)


def scope(html,heading):
    s=BeautifulSoup(html,'html.parser')
    if not any(text(h)==heading for h in s.find_all(['h1','h2'])):raise ValueError('Marshall heading changed')
    return s.find('section',class_='main-section')or s.find('main')or s


def parse_first(html):
    s=scope(html,'General Education Requirements for First-Year Students');v=text(s)
    guarded(v,['Option A:','Option B:','Option C:','two different academic disciplines','four 4-unit','no exceptions','before enrolling in DOC 2 and DOC 3'])
    rows=[node('first-policy','Marshall first-year sequence and distributions',kind='note',summary='DOC 1/2/3 must be letter graded and completed at UCSD, normally within two years. ELWR precedes DOC 2/3. Science: one each biology, chemistry and physics. Mathematics/statistics/logic: either two advanced-math/statistics, one advanced plus one introductory-statistics/programming-logic, or one introductory statistics plus one programming-logic. Humanities/cultural studies: two; fine arts: one. Approved science/math courses may overlap the major.'),node('breadth-policy','Marshall disciplinary breadth distribution',kind='note',summary='Four four-unit courses outside the major discipline, including two upper division and at least one approved significant-writing course. No major overlap. Noncontiguous double majors need one upper-division writing breadth course, from any discipline but not counted in either major. Public-service coursework is an approved route subject to its program rules.')];courses={}
    for h in s.find_all('h3'):
        label=text(h);m=re.fullmatch(r'(DOC-\d+): (.*?) \((\d+) units\).*',label)
        if m:
            c=course(normal(m[1]),m[2],PID+'-marshall-first',FIRST_URL,institution='ucsd',unit='quarter_hours',credits=int(m[3]),category='human_context');courses[c['id']]=c
            rows.append(node('core-'+slug(c['code']),c['code'],kind='all',course_ids=[c['id']],summary='Required DOC sequence component for the first-year route.'));continue
        panel=h.find_parent('div',class_='panel');listing=panel.find('ul')if panel else None
        if listing is None:continue
        conditional=label in ['Mathematics, Advanced Statistics','Introductory Statistics','Computer Programming & Logic']
        count=None if conditional else (2 if label=='Humanities and Cultural Studies'else 1)
        root=node('pool-'+slug(label),label+' approved pool',kind='note'if conditional else'choose_courses',count=count,summary='Conditional pool under the Marshall distribution/alternative rule; mathematics pools are not all additional requirements.');rows.append(root)
        for li in listing.find_all('li',recursive=False):
            value=text(li);match=re.match(r'([A-Z]+)-(.*)',value)
            if not match:raise ValueError('Department-coded Marshall option changed')
            dept,tail=match.groups()
            for i,item in enumerate(tail.split(',')):
                item=re.sub(r'^or\s+','',item.strip());code=normal(dept+'-'+item);ids=[]
                if code:
                    c=course(code,None,PID+'-marshall-first',FIRST_URL,institution='ucsd',unit='quarter_hours',category='human_context');courses[c['id']]=c;ids=[c['id']]
                rows.append(node('option-'+slug(label)+'-'+slug(dept)+'-'+str(i),dept+' '+item,kind='note',parent=root['id'],course_ids=ids,summary='Published approved choice: '+dept+' '+item+'.'+(' Compound, range or qualified notation remains literal.'if not ids else'')))
    rows.append(node('arts-units','Marshall MUS 80 eligibility',kind='note',summary='MUS 80 must be taken for four units to count as fine arts; the requirement does not establish every listed course’s credit value.'))
    return dict(id=PID,curriculum_status='partial',courses=list(courses.values()),requirements=rows)


def parse_transfer(html):
    s=scope(html,'General Education Requirements for Transfer Students');v=text(s)
    guarded(v,['Cal-GETC','Fall 2026 term and forward','DOC-170','Winter 2027','one or two missing IGETC','D grade or better','Letter of GE Completion','course-by-course basis'])
    c=course('DOC 170',None,PID+'-marshall-transfer',TRANSFER_URL,institution='ucsd',unit='quarter_hours',category='human_context')
    return dict(id=PID,curriculum_status='partial',courses=[c],requirements=[node('transfer-cert','Marshall certified-transfer and partial-certification routes','transfer',kind='note',summary='IGETC/CalGETC and UC Reciprocity waive lower-division GE; partial IGETC leaves one or two missing requirements at D or P, with advising for missing language. Two upper-division 100–199 courses of at least four units outside the major remain, including writing breadth. Transfer agreements do not apply to first-year admits.'),node('transfer-doc170','Marshall Fall-2026 transfer writing rule','transfer',kind='all',course_ids=[c['id']],summary='For transfers admitted Fall 2026 onward, DOC 170 is the writing-breadth course, first available Winter 2027; it is part of the two-course upper-division breadth requirement, not an extra third course. The general writing list remains relevant to other eligible cohorts.'),node('transfer-other','Marshall transfers without an agreement','transfer',kind='note',summary='Prior completed lower-division GE at a non-UC four-year or out-of-state two-year institution can waive lower GE after a Letter of GE Completion and advising. Otherwise advising reviews each transfer course and determines remaining DOC, math, science, humanities, arts and up-to-four breadth requirements; petitions may be needed. This is an individual approval route, not an unprovided universal course list.')])


def parse_writing_text(value):
    """Reviewed PDF text only; does not certify a new PDF download or audit."""
    guarded(value,['July 28, 2026','2026-2027','DOC 170','Winter 2027','ALL UPPER-DIVISION COURSE OFFERINGS'])
    headings=['Classical Studies','History','Literature','Music','Philosophy','Study of Religion','Theatre & Dance','Visual Arts','Anthropology','Cognitive Science','Communication','Education Studies','Political Science','Psychology','Sociology','Urban Studies & Planning','Critical Gender Studies','Ethnic Studies','Global Health','Japanese Studies','Latin American Studies']
    lines=value.splitlines();starts=[]
    for label in headings:
        indices=[i for i,line in enumerate(lines)if line.strip()==label]
        if len(indices)!=1:raise ValueError('Writing department boundary changed: '+label)
        starts.append((indices[0],label))
    starts.sort();rows=[node('writing-scope','Marshall 2026–27 significant-writing eligibility','writing',kind='note',summary='List updated July 28, 2026. Qualifying English writing is completed outside class, discipline-appropriate and evaluated for writing as well as content: at least ten pages or two five-page papers. Exams do not count. The course must be outside the major discipline. Transfers from Fall 2026 must instead use DOC 170, available from Winter 2027. Summer 2026 requires the prior-year list from advising.')]
    for j,(start,label)in enumerate(starts):
        end=starts[j+1][0]if j+1<len(starts)else len(lines)
        raw=' '.join(x.strip()for x in lines[start+1:end]if x.strip())
        raw=re.split(r' Note: This requirement',raw)[0]
        raw=re.sub(r' (?:Social Science|Interdepartmental/Interdisciplinary)$','',raw)
        rows.append(node('writing-'+slug(label),label+' writing options','writing',kind='note',summary='Published department option expression: '+raw+'. Course-number ranges and open department predicates are retained as eligibility expressions, without inventing course names or treating paired EDS service-learning entries as independent options.'))
    return dict(id=PID,curriculum_status='partial',requirements=rows)


def parse_breadth_observation(major, classification, groups):
    """Explicit rendered selector observation, never a raw-shell refresh."""
    if major!='CS29 - Artificial Intelligence' or classification!='Engineering or Science':raise ValueError('Wrong major/discipline selected')
    if set(groups)!={'Humanities/Fine Arts','Social Sciences','Interdepartmental / Interdisciplinary','Foreign Languages'}:raise ValueError('Rendered AI subject groups changed')
    rows=[node('ai-classification','Marshall AI disciplinary classification','selector',kind='note',summary='The public selector explicitly classifies CS29 Artificial Intelligence as Engineering or Science. Only its resulting eligible outside-discipline groups below are represented. Selected breadth courses cannot overlap AI major requirements; no signed-in student record was used.')]
    for label,values in groups.items():
        if not values:raise ValueError('Empty rendered breadth pool')
        rows.append(node('ai-breadth-'+slug(label),label+' breadth departments','selector',kind='note',summary='Approved outside-discipline subjects for AI: '+'; '.join(values)+'. These are open department predicates, not an enumerated finite course list.'+(' Foreign-language eligibility must match the linked TritonLink Language Courses list.'if label=='Foreign Languages'else'')))
    return dict(id=PID,curriculum_status='partial',requirements=rows)
