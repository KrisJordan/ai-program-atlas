"""Warren AI applicability, conditional area studies, and public approval tables."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, slug, text
from atlas.adapters.ucsd_college_context import requirement
from atlas.adapters.ucsd_degree_policies import PID, guarded
from atlas.adapters.ucsd_revelle_pools import section, normal
AREA_URL='https://warren.ucsd.edu/academics/general-education/area-studies.html'
GE_URL='https://warren.ucsd.edu/academics/general-education/index.html'
TRANSFER_URL='https://warren.ucsd.edu/academics/general-education/ud-non-contiguous.html'
SHEET_BASE='https://docs.google.com/spreadsheets/u/0/d/e/'
FORMAL_ID='2PACX-1vTfBllYaNkwMFbcEs9cYwCTJsDcM0-a_-tWW6-DR-zZXlLyNpFfP3FBMCKR64Qj4dkG-zLDILNFgfqh'
AREA_ID='2PACX-1vR-aC9cVI_o4xRZ8I_Go7Mkx-hSy6dcbPt8znZAuOFwDBI7lwfdAqtb1IgwV7D-poKWvNVJvlG3OA5V'
TABLES={'formal':(FORMAL_ID,'0','Formal skills'), 'anti-racism-humanities':(AREA_ID,'0','Anti-racism humanities'), 'anti-racism-social':(AREA_ID,'2132537523','Anti-racism social science'), 'environment':(AREA_ID,'1107304246','Environmental studies'), 'law':(AREA_ID,'523589065','Law and society')}
TABLE_URLS={k:SHEET_BASE+v[0]+'/pubhtml/sheet?headers=false&gid='+v[1]for k,v in TABLES.items()}


def node(key,title,source='area',**kw):
    return requirement(PID,'warren-'+key,title,PID+'-warren-'+source,unit='quarter_hours',category='human_context',**kw)


def parse_area(html):
    s=section(html,'Area Studies - B.S. Engineering Majors Only');v=text(s)
    guarded(v,['Artificial Intelligence','three four-unit courses','At least one course from each Area Study','Rady School of Management (MGT) courses may not be used','only one discipline','prior to Winter 2022'])
    rows=[node('ai-scope','Warren engineering pathway explicitly includes AI',kind='note',summary='The published B.S. Engineering list explicitly includes CSE Artificial Intelligence. For Warren first-year/noncertified transfer routes, choose one humanities/fine-arts and one social-science Area Study, both unrelated to AI and each other. Each has three four-unit courses, including two upper-division and at least one UCSD course. This resolves applicability; the six-course PofC route for nonengineering majors is not imposed on AI.'),
          node('area-policy','Area-study grades, overlap and discipline limits',kind='note',summary='P/NP is permitted. Upper-division major/minor courses cannot overlap Area Study or other GE, apart from separately permitted major/minor overlap. No MGT courses; no language courses in social-science studies and at most two in humanities studies. A # subject may occupy only one discipline. Humanities and Perspectives of Social Science cannot be the two chosen studies. Special Studies 195 is excluded by the general GE page.'),
          node('minor-substitute','Optional noncontiguous minor substitution',kind='note',summary='A qualifying minor may replace its discipline’s Area Study; interdisciplinary substitution requires at least four minor courses in that discipline and advising review. A business minor needs three approved upper-division social-science courses outside MGT. At most two applicable upper-division courses/eight units may overlap major and minor. These are optional approval predicates, not a requirement to complete every minor.')]
    for label in ['Humanities and Fine Arts:','Social Sciences:']:
        h=next((h for h in s.find_all('h4')if text(h)==label),None)
        if not h:raise ValueError('Area-study discipline list missing')
        options=[text(li)for li in h.find_next('ul').find_all('li',recursive=False)]
        root=node('subjects-'+slug(label),label.rstrip(':')+' area-study choices',kind='choose_courses',count=1,summary='Select one subject area, not one course. * denotes a specialized pool; # denotes one-discipline-only eligibility; + marks the incompatible broad-area pair.');rows.append(root)
        for value in options:rows.append(node('subject-'+slug(label)+'-'+slug(value),value,kind='note',parent=root['id'],summary='Approved subject area: '+value+'. Its required course distribution and any specialized/interdisciplinary approvals still apply.'))
    for label in ['Humanities','Human Developmental Sciences','Perspectives of Social Science']:
        h=next((h for h in s.find_all('h2')if text(h)==label),None)
        if not h:raise ValueError('Specialized department predicate missing')
        block=h.find_next_sibling('div');items=[text(li)for li in block.find_all('ul')[0].find_all('li',recursive=False)]
        summary='Published eligible department predicates: '+'; '.join(items)+'. '
        if label=='Human Developmental Sciences':summary+='Take HDS 1 and two upper-division courses in Human Developmental Sciences from those departments; not every course in each department is automatically eligible.'
        else:summary+='Any three four-unit courses, at least two upper division. Humanities excludes linguistics/language; it cannot pair with Perspectives of Social Science. Off-list applicable humanities courses may be petitioned before enrollment.'if label=='Humanities'else'Any three four-unit courses, at least two upper division; cannot pair with Humanities. This area study does not itself satisfy minor requirements.'
        rows.append(node('special-'+slug(label),label+' specialized selection rule',kind='note',summary=summary))
    rows.append(node('law-topics','Law-and-society topical and date restrictions',kind='note',summary='ANSC 100, HIUS 181 and SOCI 120T need a law-related topic and prior Warren approval. The page’s asterisk excludes designated courses taken before Winter 2022; ** denotes cross-listing. The embedded table prints ETHN 153*** without a matching triple-asterisk explanation, retained as unresolved.'))
    return dict(id=PID,curriculum_status='partial',requirements=rows)


def parse_table(html,key):
    if key not in TABLES:raise ValueError('Unknown Warren approval table')
    s=BeautifulSoup(html,'html.parser');v=text(s)
    guarded(v,['Course Code','Course Title'])
    title=TABLES[key][2];root=node('pool-'+key,title+' approved choices','table-'+key,kind='choose_courses',count=2 if key=='formal'else 3,summary='Conditional Warren approval pool. Formal skills selects two; a selected specialized Area Study needs three four-unit courses including two upper division. Law has its separate one-plus-two split. Units are requirement minima, not inferred course metadata.');rows=[root];courses={};parent=root['id'];found=0
    for tr in s.find_all('tr'):
        cells=[text(c)for c in tr.find_all('td')]
        if not cells or not any(cells)or cells[0]=='Course Code':continue
        if cells[0].startswith('Choose '):
            m=re.fullmatch(r'Choose (one|two) of the following:',cells[0])
            if not m or key!='law':raise ValueError('Unexpected selection boundary')
            n=node('law-'+m[1],'Law and society: choose '+m[1],'table-law',parent=root['id'],kind='choose_courses',count=1 if m[1]=='one'else 2,summary='Preserve the table’s introductory versus further-course split.');rows.append(n);parent=n['id'];continue
        if len(cells)<2:raise ValueError('Incomplete public course row')
        if re.fullmatch(r'[A-Z/]+',cells[0])and len(cells)>=3:raw=cells[0]+'-'+cells[1];name=cells[2]
        else:raw=cells[0];name=cells[1]
        code=normal(raw);ids=[]
        if code:
            c=course(code,name or None,PID+'-warren-table-'+key,TABLE_URLS[key],institution='ucsd',unit='quarter_hours',category='human_context');courses[c['id']]=c;ids=[c['id']]
        rows.append(node('option-'+key+'-'+str(found),raw,'table-'+key,parent=parent,kind='note',course_ids=ids,summary='Printed approved option '+raw+(': '+name if name else' (title not supplied)')+'.'+(' Compound or annotated code preserved without inferred expansion.'if not ids else'')));found+=1
    if not found:raise ValueError('No public table rows')
    if key=='law'and not any(r['id'].endswith('law-two')for r in rows):raise ValueError('Law split missing')
    return dict(id=PID,curriculum_status='partial',courses=list(courses.values()),requirements=rows)


def parse_transfer(html):
    s=section(html,'Choosing Your Upper-Division Non-Contiguous Courses(UDNC)');v=text(s)
    guarded(v,['One four-unit, upper-division course','Education Abroad Program, or another UC campus','197, 198, or 199','Rady School of Management courses cannot be used'])
    rows=[node('transfer-udnc','Warren certified-transfer noncontiguous route','transfer',kind='note',summary='For the certified-transfer GE branch: one four-unit upper-division course outside the major’s discipline, taken at UCSD, UCEAP or another UC campus. P/NP permitted. No major overlap except noncontiguous double majors; an appropriate upper-division minor course may substitute. One noncontiguous Special Studies 197/198/199 may qualify. MGT does not qualify; environmental studies/FMPH needs advising. Prerequisites still apply.')]
    # Read only Step 2 subject lists; Step 1 classifies majors, not eligible courses.
    step=next((h for h in s.find_all(['h2','h3'])if text(h).startswith('Step 2')),None)
    if not step:raise ValueError('Transfer option list missing')
    block=step.find_parent('div',class_='panel').find('div',class_='panel-body')
    for h in block.find_all(['h3','h4']):
        label=text(h);listing=h.find_next('ul');values=[text(li)for li in listing.find_all('li',recursive=False)]
        rows.append(node('transfer-'+slug(label),label+' transfer predicates','transfer',kind='note',summary='Approved departments: '+'; '.join(values)+'. Choose outside the major discipline; these are department predicates, not a finite universal course list.'))
    return dict(id=PID,curriculum_status='partial',requirements=rows)
