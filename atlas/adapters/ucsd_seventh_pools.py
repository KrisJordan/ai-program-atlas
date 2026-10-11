"""Seventh alternatives, high-impact routes and transfer rules from public pages."""
import re
from atlas.adapters.cmu_bs.common import course, slug, text
from atlas.adapters.ucsd_college_context import requirement
from atlas.adapters.ucsd_degree_policies import PID, guarded
from atlas.adapters.ucsd_revelle_pools import section, normal
BASE='https://seventh.ucsd.edu/academics/degree-requirements/degree-requirements-'
FIRST_URL=BASE+'first.html'
TRANSFER_URL=BASE+'transfers.html'
AREAS=['Arts','Humanities','Natural Sciences and Engineering','Quantitative Reasoning','Social Sciences']


def node(key,title,source='first',**kw):
    return requirement(PID,'seventh-'+key,title,PID+'-seventh-'+source,unit='quarter_hours',category='human_context',**kw)


def block(s,label):
    h=next((h for h in s.find_all('h2')if text(h)==label),None)
    if not h or not h.find_next_sibling('div'):raise ValueError('Seventh pool section missing: '+label)
    return h.find_next_sibling('div')


def parse_pool(s,label,key,count=None):
    b=block(s,label)
    for br in b.find_all('br'):br.replace_with('\n')
    lines=[re.sub(r'\s+',' ',line).strip()for p in b.find_all('p')for line in p.get_text().splitlines()]
    root=node(key,label,kind='choose_courses'if count else'note',count=count,summary='Conditional Seventh approved option pool, not an additional requirement beyond its component. Original compounds/annotations stay qualified; missing credits remain unknown.')
    rows=[root];courses={};i=0
    for line in lines:
        if not re.match(r'\*?[A-Z]+-\d',line):continue
        parts=re.split(r'\s+-\s+',line,maxsplit=1)
        if len(parts)!=2:raise ValueError('Seventh option structure changed: '+line)
        raw,title=parts;code=normal(raw.lstrip('*'));ids=[]
        if code:
            name=re.sub(r'\s*\((?:also DEI|no prerequisites|by petition.*|by TEA request only)\)','',title).strip()
            c=course(code,name,PID+'-seventh-first',FIRST_URL,institution='ucsd',unit='quarter_hours',category='human_context')
            if 'no prerequisites'in title:c['prerequisites']='None stated by this college list.'
            if raw.startswith('*'):c['prerequisites']='EDS 139 requires one published corequisite: EDS 128A–B, 129A–B–C, 130, 131, 133, 136, 137, 140, 141, 145, or 146. Sequence notation retained.'
            courses[c['id']]=c;ids=[c['id']]
        detail='Published option '+line+'.'
        if not ids:detail+=' Printed bundle remains one qualified row; no guessed alternatives, independent course credits or correction of source notation.'
        if raw.startswith('*'):detail+=' EDS139 requires one listed corequisite: EDS128A–B,129A–B–C,130,131,133,136,137,140,141,145or146; sequence notation retained.'
        rows.append(node(key+'-row-'+str(i),raw,parent=root['id'],kind='note',course_ids=ids,summary=detail));i+=1
    if not i:raise ValueError('Seventh empty pool: '+label)
    return courses,rows


def parse_first(html):
    s=section(html,'Degree Requirements for First Year Students');v=text(s)
    guarded(v,['Remote "R" versions','Select two courses of interest','upper-division standing','Any 2-4 unit course numbered 195 to 199','Other credit-bearing experiential learning opportunities','35 of the final 45'])
    rows=[];courses={}
    for label in AREAS:
        c,n=parse_pool(s,label+' - 2 courses','alternatives-'+slug(label),2);courses.update(c);rows.extend(n)
    c,n=parse_pool(s,'Department/Program Courses','high-impact-pool');courses.update(c);rows.extend(n)
    rows.extend([
      node('synthesis','Seventh first-year Synthesis sequence',kind='note',summary='SYN1 or1R, then SYN2 or2R, then SYN100; all at UCSD and letter graded. SYN1 requires Seventh membership and ELWR; SYN2 requires SYN1/1R; SYN100 requires Seventh membership, upper-division standing and completion of1/1R and2/2R. No credit for both normal and R version. SYN1/1R satisfies climate for lower-division entrants from Fall2024.'),
      node('alternatives-policy','Seventh alternatives policy',kind='note',summary='Two courses in each of five areas. Approved R variants, AP/IB and transfer credit apply; letter or P/NP grading, and major/minor/university overlap are permitted. Upper-division language is an open Humanities route with college advising; not every language course is separately enumerated.'),
      node('high-impact-policy','Seventh High-Impact qualification',kind='note',summary='One two-to-four-unit experiential course; may overlap major/minor/university requirements, letter or P/NP. The finite department pool retains petitions (MAE190,VIS108), CAT124 TEA request and EDS139 corequisite bundle. Any two-to-four-unit course numbered195–199 qualifies; no inventory of every such offering is implied.'),
      node('high-impact-open','Seventh approved experiential routes',kind='note',summary='Any upper-division AIP internship, any two-to-four-unit EAP/OAP/Global Seminar course, or completion of California Ecology and Conservation can fulfill High-Impact. Other credit-bearing experiences require a petition. UCDC research seminar may count toward Alternatives by petition. These are open approved routes, not finite missing course lists.'),
      node('degree-policy','Seventh current degree policy',kind='note',summary='Current page:180 total/60 upper-division units, UC GPA at least2.0, no more than25% UCSD units P/NP, and35of final45units atUCSD. Its end-of-final-quarter F1/J1 AHI waiver wording is retained separately from the university petition wording.')])
    return dict(id=PID,curriculum_status='partial',courses=list(courses.values()),requirements=rows)


def parse_transfer(html):
    s=section(html,'Degree Requirements for Transfer Students');v=text(s)
    guarded(v,['All transfer students must complete SYN 100 and High-Impact','Missing no more than two IGETC requirements','letter grade of C- or better','Winter Quarter of their first year','cannot be taken after SYN 100','Synthesis 100 (4 units)'])
    return dict(id=PID,curriculum_status='partial',courses=[course('SYN 100',None,PID+'-seventh-transfer',TRANSFER_URL,institution='ucsd',unit='quarter_hours',credits=4,category='human_context')],requirements=[
      node('transfer-certified','Seventh IGETC/reciprocity transfer route','transfer',kind='note',summary='All transfers complete SYN100 (four units, at UCSD and letter graded) plus one two-to-four-unit High-Impact course (letter/P-NP except SYN150 requires letter). Full pre-transfer IGETC certification or official UC/four-year reciprocity waives lower-division GE; documentation is required. This page names IGETC and does not independently establish CalGETC treatment; no inferred substitution.'),
      node('transfer-partial','Seventh partial or uncertified transfer route','transfer',kind='note',summary='Partial IGETC may leave at most two requirements, completed at P or C− or better, plus SYN100 and High-Impact. Without an agreement, course-by-course review and petitions determine remaining GE after prior coursework/tests. Agreements apply only to students admitted as transfers.'),
      node('transfer-synthesis','Seventh transfer enrollment and optional preparation','transfer',kind='note',summary='Transfers are stated to meet SYN100 prerequisites and receive preauthorization from winter of their first UCSD year. Optional SYN150/150R is transfer-only and must precede SYN100; it can satisfy High-Impact only for letter grade. No credit for both150and150R. It is recommended preparation, not an added mandatory course.')])
