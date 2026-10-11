"""Linked Revelle transfer inventory and Marshall service substitutions."""
from atlas.adapters.cmu_bs.common import requirement,text
from atlas.adapters.ucsd_degree_policies import PID,guarded
from atlas.adapters.ucsd_revelle_pools import section
HUM_URL='https://revelle.ucsd.edu/humanities/transfer-course-policy/index.html'
REVELLE_URL='https://revelle.ucsd.edu/academics/general-education/gen-ed-tran-students.html'
MARSHALL_URL='https://marshall.ucsd.edu/academics/academic-opportunities/index.html'


def node(key,title,source,**kw):
    return requirement(PID,'transfer-options-'+key,title,PID+'-transfer-options-'+source,unit='quarter_hours',category='human_context',kind='note',**kw)


def parse_humanities(html):
    s=section(html,'Humanities Transfer Course Policy');v=text(s)
    guarded(v,['All freshmen entering Revelle Fall 2017 and after','three approved quarter courses, two approved semester courses','All institutions are on the semester system except for De Anza and Foothill','Credit is allowed for only one of HUM 200 and HUM 204'])
    rows=[node('humanities-entry','Revelle humanities substitution limits','humanities',summary='First-year entrants from Fall2017 take HUM1/2/3 and at least one of4/5 at UCSD; only one of4/5 can be an approved transfer substitution. Earlier first-year entrants through Fall2016 take1/2 and at least one of3/4/5 at UCSD, allowing up to two approved substitutions. Transfer entrants can fulfill HUM3–5 with three approved quarter courses, two semester courses, or one semester course plus one UCSD HUM3/4/5. This transfer-policy wording differs from the current transfer GE page choosing two of HUM3/4/5; preserve the discrepancy.'),node('humanities-policy','Revelle humanities transfer grading and review','humanities',summary='Letter grades required for UCSD and transferred humanities. Prior-to-matriculation philosophy/history/literature/humanities receives summer evaluation without petition. After UCSD enrollment use this approved list or petition with syllabus/course description; off-list approval is rare, not guaranteed. ASSIST listings alone are insufficient from Fall2017. Content duplication normally yields no additional units, though subject-credit review is possible.'),node('humanities-exceptions','Revelle humanities duplicate-content exceptions','humanities',summary='One course normally allowed from each Introduction and History list, subject to repetition rules. Foothill HUMN5and6 both count only without prior equivalent1400s-to-present credit. DeAnza HIST6B can accompany another listed course; both6B/6C can count only without prior History-category credit. CSU Dominguez Hills HUM200 was renumbered HUM204 in Fall2021 and only one can count. DeAnza/Foothill use quarters; others on these lists use semesters. No conversion or course units are inferred.')]
    tables=s.find_all('table')
    if len(tables)!=2:raise ValueError('Humanities transfer table structure changed')
    for i,t in enumerate(tables):
        n=0
        for tr in t.find_all('tr'):
            cells=[text(c)for c in tr.find_all(['td','th'])]
            if len(cells)!=3 or cells[0]=='Institution':continue
            rows.append(node('humanities-'+str(i)+'-'+str(n),cells[0]+' — '+cells[1],'humanities',summary='Approved '+('Introduction to Humanities'if i==0 else'History')+' transfer row: '+cells[0]+' | '+cells[1]+' | '+cells[2]+'. Footnotes retain the separately stated duplicate-content and quarter/semester conditions. This is an external-institution option, not a UCSD course.'));n+=1
        if not n:raise ValueError('Empty humanities transfer category')
    return dict(id=PID,curriculum_status='partial',requirements=rows)


def parse_revelle_transfer(html):
    s=section(html,'General Education Requirements for Transfer Students');v=text(s)
    guarded(v,['With Cal-GETC:','Starting Fall 2025, UC Reciprocity','pick two courses','Completion of the optional LOTE certification','Three courses, selected from the approved lists'])
    return dict(id=PID,curriculum_status='partial',requirements=[
      node('revelle-certified','Revelle IGETC/CalGETC transfer requirements','revelle',summary='Current transfer GE page: all incoming transfers from Fall2024 take HUM100. Full IGETC still leaves mathematics and three sciences. Math alternatives: two semesters calculus; one semester calculus plus statistics/approved math; or MATH10A/20A plus two approved quarter courses. Science: two different biology/chemistry/physics disciplines plus one approved science. CalGETC also leaves language: two quarter/semester courses, waived by optional LOTE certification. Official certification is needed; these agreements are not for first-year admits.'),
      node('revelle-partial','Revelle partial IGETC and reciprocity','revelle',summary='Partial IGETC permits one or two missing areas, determined by advising, in addition to HUM100/math/science. Starting Fall2025 UC reciprocity satisfies lower-division Revelle GE, with HUM100 still required; official UC reciprocity letter needed. Continuing students consult advising. This is a college GE waiver, not a major/university waiver.'),
      node('revelle-other','Revelle transfer without certification','revelle',summary='Current page lists HUM100; HUM1and2 (often already fulfilled); two selected from HUM3/4/5; three math courses; three natural sciences; two social sciences; one fine art; and two quarter/semester language courses. Individual review determines prior satisfaction and petitions. HUM3/4/5 two-course wording differs from the linked Humanities transfer policy three-quarter/two-semester route; science3 differs from the catalog4 and the component page cohort qualifiers. Do not reconcile by assumption.')])


def parse_marshall_service(html):
    s=section(html,'Academic Opportunities');v=text(s)
    guarded(v,['Public Service Option for Disciplinary Breadth','(AIP 197P)','(TMC 120)','130, 131, 133, 135, 136, 137, 145 and 146','exception of 135, which is six units','ENG 100D + 100L + project'])
    rows=[node('marshall-scope','Marshall public-service breadth substitution','marshall',summary='One upper-division disciplinary breadth requirement may be satisfied regardless of major discipline. For a single major the course cannot also fulfill that major; double-major students require advising clarification. This is an alternative within breadth, not an extra course.'),node('marshall-aip','Marshall AIP197P or TMC120 service option','marshall',summary='AIP197P public-service internship or TMC120 partnership-school work may satisfy one non-significant-writing disciplinary breadth requirement, regardless of major discipline.'),node('marshall-pal','Marshall Partners at Learning options','marshall',summary='Choose EDS130,131,133,135,136,137,145or146 for one disciplinary breadth slot, with or without significant writing. Each requires EDS139 as corequisite except EDS135, which is a six-unit standalone option. The public-service wording does not by itself certify every pairing as significant writing; apply the writing list/policy separately.'),node('marshall-ties','Marshall Global TIES option','marshall',summary='ENG100D plus100L plus a project can fulfill one upper-division disciplinary breadth requirement with writing, regardless of major discipline, under service-overlap rules. Preserve the complete bundle rather than treating its courses as independent choices.')]
    return dict(id=PID,curriculum_status='partial',requirements=rows)
