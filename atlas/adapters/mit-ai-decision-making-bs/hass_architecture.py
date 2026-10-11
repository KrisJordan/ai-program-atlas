"""Source-separated architecture HASS pages and public PDF requirement sheets."""
import re
from atlas.adapters.national_curriculum_common import content,clean,course,rule,require_phrases
from importlib import import_module
optional=import_module('atlas.adapters.mit-ai-decision-making-bs.hass_departments').optional
PID='mit-ai-decision-making-bs'
ACT='https://architecture.mit.edu/art-culture-technology'
HTC='https://architecture.mit.edu/history-theory-criticism'
UNDERGRAD='https://architecture.mit.edu/undergraduate-programs'
PDFS={
 'design':('Design','https://architecture.mit.edu/sites/default/files/2025-11/Design%20HASS%20Concentration%20AY26.pdf'),
 'htc':('History of Architecture, Art, and Design','https://architecture.mit.edu/sites/default/files/2026-09/HTC%20HASS%20Concentation_AY27.pdf'),
 'act':('Art, Culture, and Technology','https://architecture.mit.edu/sites/default/files/2026-03/ACT%20HASS%20Concentration_program%20info.pdf'),
}


def parse_pdf_text(key,text):
    title,url=PDFS[key];flat=clean(text)
    markers=([title+' HASS Concentration','Three subjects are required from two groups of study; two from Group 1 and one from Group 2','~or~','~And~'] if key=='design' else [title,'Concentration','Four subjects are required from two groups of study, three from Group 1 and one from Group 2'])
    for marker in markers:
        if marker not in flat:raise ValueError('Architecture PDF requirement marker changed: '+marker)
    stage=None;rows=[];stages=[]
    for line in text.splitlines():
        line=clean(line.strip(' •'))
        if not line:continue
        group=re.match(r'^Group ([12])(?::|$)',line)
        if group:stage=int(group[1]);stages.append(stage);continue
        if line.startswith('Total for Concentration'):stage=None;continue
        if stage is None:continue
        if line in ['Art, Culture & Technology','History of Architecture, Art, and Design','History of Art','Introductory Subjects','Intermediate / Advanced Subjects','~And~']:continue
        match=re.match(r'^(4\.[0-9A-Z]+),?\s+(.+)',line)
        if match:rows.append([stage,match[1],match[2]])
        elif rows and rows[-1][0]==stage:
            rows[-1][2]+=' '+line
        else:raise ValueError('Unexpected PDF group content')
    if stages!=[1,2]:raise ValueError('Architecture PDF group order changed')
    sid=PID+'-hass-architecture-'+key+'-pdf';prefix='mit-ai-hass-architecture-'+key+'-pdf';cs={};groups={1:[],2:[]}
    for group,code,tail in rows:
        annotation=re.search(r'\s+\(?(?:FA|SP|IAP)\b',tail)
        unit=re.search(r'\b(\d+)\s+units?\b',tail)
        if not annotation or not unit:raise ValueError('Architecture course annotation/unit missing')
        name=tail[:annotation.start()]
        # Visually confirmed PDFKit ligature mapping in the ACT file, not a course-number repair.
        if key=='act':name=name.replace('Introduc/on','Introduction')
        c=course(prefix,code,name,sid,url,credits=int(unit[1]),unit='units')
        if c['id'] in cs:raise ValueError('Duplicate architecture PDF course row')
        cs[c['id']]=c;groups[group].append(c['id'])
    if not all(groups.values()):raise ValueError('Architecture PDF option pool missing')
    rules=[optional(prefix,title+' — published PDF plan',sid)]
    rules[0]['summary']+=' This is a self-contained source version, not cumulative with a separate webpage reference. File path labels are not assumed printed publication dates or launch dates; seasonal annotations are not current-offering guarantees.'
    if key=='design':
        by={c['code']:c['id'] for c in cs.values()}
        if set(groups[1])!={by.get(c) for c in ['4.021','4.02A','4.053']}:raise ValueError('Design studio alternative structure changed')
        rules += [rule(prefix+'-studio','First design studio: regular or IAP intensive',sid,[by['4.021'],by['4.02A']],parent=prefix,kind='choose_courses',count=1),rule(prefix+'-visual','Required visual communication subject',sid,[by['4.053']],parent=prefix,kind='all'),rule(prefix+'-group2','One Group 2 subject',sid,groups[2],parent=prefix,kind='choose_courses',count=1)]
    else:
        rules += [rule(prefix+'-group1','Three Group 1 subjects',sid,groups[1],parent=prefix,kind='choose_courses',count=3),rule(prefix+'-group2','One Group 2 subject',sid,groups[2],parent=prefix,kind='choose_courses',count=1)]
    return dict(id=PID,courses=list(cs.values()),requirements=rules)


def _concentration_pane(root,title):
    h=root.find(lambda n:n.name=='h4' and clean(n.get_text(' ',strip=True))==title)
    pane=h.find_parent('div',class_='expcol-wrap') if h else None
    if pane is None:raise ValueError('Architecture concentration pane missing')
    return pane


def parse_act(html):
    root=content(html,'Art Culture + Technology');pane=_concentration_pane(root,'HASS Concentration in Art, Culture and Technology')
    require_phrases(pane,['Four subjects are required','three from Group A and one from Group B','Choose from Group A the History of Art section','Total for Concentration in ACT = 4 Subjects'])
    sid=PID+'-hass-architecture-act-page';prefix='mit-ai-hass-architecture-act-page';cs=[]
    for p in pane.find_all('p'):
        for br in p.find_all('br'):br.replace_with('__BR__')
        for text in p.get_text(' ',strip=True).split('__BR__'):
            match=re.fullmatch(r'(4\.[A-Z0-9]+) — (.+)',clean(text))
            if match:cs.append(course(prefix,match[1],match[2],sid,ACT,unit='units'))
    if not cs:raise ValueError('ACT webpage Group A pool missing')
    return dict(id=PID,courses=cs,requirements=[optional(prefix,'Art, Culture and Technology — webpage reference',sid),rule(prefix+'-a','Three Group A subjects in this webpage version',sid,[c['id'] for c in cs],parent=prefix,kind='choose_courses',count=3),rule(prefix+'-b','One History of Art subject: unresolved linked reference',sid,parent=prefix,kind='choose_courses',count=1,summary='This page points to Group A’s History of Art section at a legacy URL that returned 404. The separately linked ACT PDF supplies a specific six-subject Group 2 pool. The observed wording is not silently replaced with that PDF or the different History of Art subgroup in the current HTC PDF. Advisor/source-precedence clarification is needed. These source versions are not cumulative.')])


def parse_htc(html):
    root=content(html,'History Theory + Criticism');pane=_concentration_pane(root,'HASS Concentration in History of Architecture, Art and Design')
    require_phrases(pane,['composed of four subjects','Choose three subjects from Group A, and one from Group B','Undergraduate section'])
    sid=PID+'-hass-architecture-htc-page'
    return dict(id=PID,requirements=[rule('mit-ai-hass-architecture-htc-page','HTC webpage scope and linked requirements',sid,kind='note',summary='The undergraduate HTC concentration comprises three architecture/art/design-history subjects and one ACT subject. This page directs subject details to the undergraduate section; the currently linked HTC PDF supplies its two full pools. Do not import graduate Islamic Architecture/Urbanism or PhD requirements from other sections of this page.')])


def parse_undergraduate(html):
    root=content(html,'Undergraduate Programs')
    require_phrases(root,['Department of Architecture offers three HASS concentrations','Design (NEW!)','History of Architecture, Art, and Design (HTC)','Art, Culture + Technology (ACT)','Students majoring in Course 4 may concentrate in either the HTC or ACT concentrations','students majoring in Course 4B may concentrate in Design, HTC, or ACT','carefully considering overlapped courses'])
    # Observe the actually published targets; a changed filename queues review.
    for _,url in PDFS.values():
        path=url.removeprefix('https://architecture.mit.edu')
        if not root.find('a',href=lambda h:h in [url,path]):raise ValueError('Architecture requirement-sheet link changed')
    sid=PID+'-hass-architecture-undergraduate'
    return dict(id=PID,requirements=[rule('mit-ai-hass-architecture-undergraduate','Architecture HASS fields and major-overlap context',sid,kind='note',summary='The current undergraduate page links Design, HTC and ACT requirement sheets. It allows Course 4 majors to concentrate in HTC or ACT, and Course 4B majors in Design/HTC/ACT with attention to overlapped courses; students are directed to the undergraduate administrator for overlap allowances. These conditional major-affiliation rules are preserved without applying an architecture major’s degree requirements to the AI BS.')])


SOURCE_PARSERS={ACT:parse_act,HTC:parse_htc,UNDERGRAD:parse_undergraduate}

LIT_PDF='https://lit.mit.edu/wp-content/uploads/2026/06/Literature-MajorMinor.pdf'


def parse_literature_pdf_text(text):
    flat=clean(text)
    for marker in ['The concentration in Literature requires three subjects','one subject from the intermediate tier','one subject from the seminar (700-) tier','Two six-unit samplings courses','combined by petition','permission of the instructor','meet with a concentration advisor']:
        if marker not in flat:raise ValueError('Literature concentration sheet changed: '+marker)
    sid=PID+'-hass-literature-pdf'
    return dict(id=PID,requirements=[rule('mit-ai-hass-literature-pdf','Literature linked sheet: corroborating concentration scope',sid,kind='note',summary='The currently linked one-page Literature information sheet agrees with the HTML concentration rule: three subjects including intermediate and seminar tiers, the two-six-unit sampling petition, instructor-approved outside subjects, and an advisor meeting. The major/minor columns are separate programs and add no concentration requirements. The file path is not a printed publication date.')])
