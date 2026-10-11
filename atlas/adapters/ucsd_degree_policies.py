"""UCSD breadth tags and degree policies; college pathways are conditional."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, requirement, slug, text
PID='university-of-california-san-diego-artificial-intelligence-bs-degree'
DEGREE_URL='https://catalog.ucsd.edu/undergraduate/degree-requirements/index.html'
COURSES_URL='https://catalog.ucsd.edu/courses/CSE.html'
DEPARTMENT_URL='https://cse.ucsd.edu/undergraduate/bs-artificial-intelligence-cse-bs-004'
COLLEGE_BASE='https://catalog.ucsd.edu/undergraduate/colleges/'


def guarded(value, clauses):
    if any(c not in value for c in clauses):raise ValueError('UCSD policy changed; review required')


def body(html,heading):
    s=BeautifulSoup(html,'html.parser')
    if not any(text(h)==heading for h in s.find_all(['h1','h2','h3'])):raise ValueError('UCSD heading missing: '+heading)
    return text(s.find('main')or s)


def node(key,title,source,**kw):
    return requirement(PID,'policy-'+key,title,PID+'-'+source,unit='quarter_hours',category='other',**kw)


def parse_tags(html):
    s=BeautifulSoup(html,'html.parser');courses={};tags={k:[] for k in ['Systems','Theory/Abstraction','Applications of Computing']}
    for p in s.find_all('p', class_='course-name'):
        v=text(p)
        if not re.search(r'\bTags?:',v):continue
        m=re.fullmatch(r'(CSE \d+[A-Z]*)\. (.*?) \((\d+)\) Tags?: (.*)',v)
        if not m:raise ValueError('Tagged course heading changed')
        code,name,units,raw=m.groups();found=[x.strip() for x in raw.split(',')]
        if any(t not in tags for t in found):raise ValueError('Unknown breadth tag')
        c=course(code,name,PID+'-courses',COURSES_URL,institution='ucsd',unit='quarter_hours',credits=int(units),category='electives');courses[c['id']]=c
        for tag in found:tags[tag].append(c['id'])
    if any(not v for v in tags.values()):raise ValueError('Missing CSE breadth tag category')
    rows=[requirement(PID,'tag-pool-'+slug(k),k+' CSE course tags',PID+'-courses',parent=PID+'-breadth-'+slug(k),kind='note',course_ids=v,category='electives',unit='quarter_hours',summary='Observed tags in course headings. A course already used for core, AI electives or another breadth requirement cannot count again; CSE 190 topics require offering-specific review.')for k,v in tags.items()]
    return {'id':PID,'curriculum_status':'partial','courses':list(courses.values()),'requirements':rows}


def parse_degree(html):
    v=body(html,'Undergraduate Degree Requirements')
    guarded(v,['at least 180 units','not less than 60 units','thirty-five of the final forty-five',
        'twelve quarters','six quarters','three consecutive quarters','five consecutive quarters',
        'grade not lower than C– or P','at least ten upper-division courses','more than two years'])
    specs=[
      ('minimum','University degree minimums','Complete at least 180 quarter units, including 60 upper-division units, an approved major, and the enrolled college’s requirements. These degree totals include the major; they are not added to its 124 units.'),
      ('residence','Senior residence','Complete 35 of the final 45 units in residence in the degree-awarding UC college/school. Provost exceptions may cover approved UC visitors, Education Abroad, UCDC or UC Sacramento. UCSD Extension concurrent enrollment does not qualify. Roosevelt publishes a different 36/44 rule, retained separately.'),
      ('dei','Diversity, equity and inclusion','Pass one approved four-unit course at C− or P or better; an articulated equivalent transfer course can qualify. Applies to lower-division entrants from Fall 2011 and upper-division entrants from Fall 2013. Approved finite course pool remains unreviewed.'),
      ('ahi','American History and Institutions alternatives','Qualify through C or better high-school US history (one unit, or half history plus half civics/government), an approved UCSD course at C−/P, AP US history/government at least 3, IB higher History of Americas at least 5, the page’s historical SAT II threshold 550, prior accepted California-college satisfaction, or acceptable college history/government at C or better. F-1/J-1 temporary residents may petition the college provost. Approved course pool remains unreviewed.'),
      ('elwr','Entry writing placement and completion','Complete placement before enrollment if entry writing is unsatisfied. College-writing placement satisfies the requirement. AWP 3 allows three consecutive quarters; AWP 4A allows three, then 4B follows immediately. Failure of the 4B portfolio leads to AWP 3, with at most three more consecutive quarters or five total. Earn C or better in AWP 3 or 4B before college writing. External UC entry-qualification alternatives remain to be inventoried.'),
      ('quarters','Completion-time limits from Fall 2019','First-year entrants have twelve quarters and transfers six. Beyond the limit, an approved college completion plan is required. Summer, approved part-time quarters, and quarters withdrawn from all courses do not count. Earlier-entry unit-limit rules are distinct.'),
      ('application','Graduation application','File the degree/diploma application with the college by its deadline; late filing needs special approval. Finish all coursework by the filed quarter’s end, otherwise submit a new application.'),
      ('double-major','Double-major approvals and unique work','Good-standing students need both departments and the college provost to approve. Each major needs at least ten unique upper-division courses (40 units); lower-division overlap is unrestricted. Two Engineering majors are not allowed, nor ordinarily two within one department. Additional major-specific prohibitions must also be checked.'),
      ('changes','Continuing-student protection','Requirement changes should not substantially obstruct continuing students. Colleges/departments may deny this protection after an interruption longer than two years; no automatic mapping of the tentative 2026 AI plan onto earlier entrants.')]
    return {'id':PID,'curriculum_status':'partial','requirements':[node(k,t,'degree-policies',kind='note',summary=s)for k,t,s in specs]}


def parse_department(html):
    v=body(html,'B.S. Artificial Intelligence (CSE-BS-004)')
    guarded(v,['Updated August 3rd, 2026','tentative and subject to change','only students admitted directly',
        'will not be able to switch back','C- or better','instructor\'s permission and departmental approval',
        'Each course can only fulfill one major requirement'])
    return {'id':PID,'curriculum_status':'partial','requirements':[
      node('admission-2026','2026–27 direct-admit restriction','department',kind='note',summary='The dated tentative department page admits only students directly placed in AI by Admissions in 2026–27. Internal switches and selective-major entry into AI are unavailable. AI students may leave for another CSE major but cannot switch back under this policy; review is planned in 2027, without a guarantee of changed eligibility.'),
      node('department-grades','Department grade and overlap policy','department',kind='note',summary='The department requires C− or better and letter grading for major work except its specified P/NP-only exceptions (CSE 89, 91, 95, 109, 197, 198, 199). Each course serves only one core, AI elective, breadth or open-elective requirement. Graduate enrollment needs instructor and departmental TEA approval; similar undergraduate/graduate credit may require petition. Tentative-page course eligibility differences remain explicit.') ]}

# Bounded summaries of the inspected catalog GE sections, not approved-list inventions.
COLLEGES={
 'revelle-college':('Revelle College',['Five courses','Three courses in mathematics','Five courses in the physical','HUM 100'], 'For first-year entrants: five-course humanities sequence; one fine arts; two social sciences; three mathematics including calculus; five sciences including biology, chemistry and physics; and fourth-quarter language proficiency or approved exam/native-language route. IGETC transfers retain mathematics, science and HUM 100; from Fall 2024 transfers need HUM 100, and transfers without UC reciprocity need four sciences. UC reciprocity exempts lower-division GE. Finite lists remain unreviewed.'),
 'john-muir-college':('John Muir College',['forty-eight units','MCWP 40 and MCWP 50','Up to three courses','MCWP 125'], 'Complete four approved three-course sequences: social science; mathematics or natural science; and two of fine arts, humanities and languages (48 units). At most three major courses overlap GE. Complete letter-graded MCWP 40 and 50 (8 units), without AP/IB substitution. IGETC or UC-reciprocity transfers may waive GE sequences; IGETC transfers still take MCWP 125 or request MCWP 50. Finite sequence lists remain unreviewed.'),
 'thurgood-marshall-college':('Thurgood Marshall College',['DISCIPLINARY BREADTH','Two of these courses must be upper division','one four-unit upper-division'], 'First-year GE: three-course Dimensions of Culture at UCSD for letter grades; one nonperformance fine art; biology, chemistry and physics; two mathematics/statistics/logic courses in the stated allowable combinations; two approved humanities/cultural studies; and four courses outside the major, including two upper-division and at least one upper-division writing course. Optional four-unit public service may replace one breadth and meet writing. Transfers retain one approved upper-division writing and one noncontiguous upper-division breadth course, with additional needs determined from credit. Approved lists remain unreviewed.'),
 'earl-warren-college':('Earl Warren College',['WCWP 10A-B','For BS engineering majors','A minimum of two courses must be upper division','WCWP 100'], 'Complete letter-graded WCWP 10A–B and the two Ethics and Society choices PHIL/POLI 27 and 28; two approved formal-skills courses. BS Engineering students complete two three-course area studies outside the major, one humanities/fine arts and one social sciences, each with at least two upper-division courses. Interdisciplinary studies require college approval; a minor may substitute. AP/IB may supply at most four units per area study. Certified transfers take WCWP 100 plus one upper-division course outside the major; other transfers take WCWP 100 and area studies. AI-specific engineering area-study applicability and finite pools need confirmation.'),
 'eleanor-roosevelt-college':('Eleanor Roosevelt College',['five quarters','Regional Specialization (three quarters)','thirty-six of the final forty-four','CalGETC LOTE'], 'First-year GE: five MMW courses; two natural sciences; two quantitative methods; language through fourth quarter or proficiency; one four-unit fine art; three courses in one geographic region including two upper-division; and qualifying upper-division written work graded C− or better. Transfer pathways use MMW 121/121R/122 with additional language/GE conditions based on certification; unmet first-year writing adds MMW 12/13. The college prints residence 36 of final 44 units, unlike university 35/45. Approved pools and full transfer conditions remain unresolved.'),
 'sixth-college':('Sixth College',['CAT 1, 2, and 3','Modes of Inquiry: Seven courses','CAT 125 or CAT 125R'], 'Complete CAT 1–3; one information-technology fluency; seven inquiry courses (two social sciences, two humanities, two natural sciences, one math/logic); one statistics; two art-making; four-unit upper-division experiential learning; and four-unit upper-division CAT 125 or 125R. Transfer agreements may meet some lower-division requirements; approved pools and exact transfer applicability remain unreviewed.'),
 'seventh-college':('Seventh College',['SYN 1/1R and SYN 2/2R','SYN 100','two courses from each of five areas','SYN 150'], 'Complete SYN 1/1R, SYN 2/2R and SYN 100; two approved courses each in arts, humanities, natural sciences/engineering, quantitative reasoning and social sciences; and one 2–4 unit high-impact experience. Alternatives/high-impact may overlap major, minor and university requirements. All transfers retain SYN 100 and high-impact; recommended SYN 150 can satisfy high-impact if letter graded. Approved pools and additional transfer needs remain unreviewed.'),
 'eighth-college':('Eighth College',['CCE 120','two courses from each of five areas','Critical Community Engagement 110 and 120','FA24 admits or later'], 'Complete CCE 1, 2, 3 and 120, plus two approved courses each in arts, humanities, natural sciences, quantitative methods/engineering and social sciences. Breadth may overlap major, minor and university requirements. Certified transfers retain CCE 110 and 120; others receive individual credit evaluation. CCE courses require letter grades. The catalog explicitly lists the climate-change requirement for Fall 2024 and later admits; its approved pool remains unreviewed.')}


def parse_college(html, key):
    name, guards, summary=COLLEGES[key];v=body(html,name);guarded(v,guards)
    return {'id':PID,'curriculum_status':'partial','requirements':[node('college-'+key,name+' pathway (only if enrolled here)','college-'+key,kind='note',summary=summary)]}
