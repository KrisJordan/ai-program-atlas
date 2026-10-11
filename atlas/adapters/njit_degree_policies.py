"""Observed NJIT GER pools and degree policies; never a completeness audit."""
import re
from functools import partial
from urllib.parse import urljoin
from atlas.adapters.national_curriculum_common import content, clean, course, rule, require_phrases

PID = 'new-jersey-institute-of-technology-business-with-ai-bs-degree'
BASE = 'https://catalog.njit.edu/undergraduate/academic-policies-procedures/'
POOLS = {
 'njit-ger-200': ('ger-200-level/', 'History and Humanities GER 200 level', 3),
 'njit-ger-300': ('ger-300-level/', 'History and Humanities GER 300+ level', 6),
 'njit-natural': ('natural-science-ger/', 'Scientific Literacy GER', 7),
 'njit-capstone': ('hss-capstone/', 'HSS Senior Seminar', 3),
}

def observed(requirements, courses=()):
 return dict(id=PID, curriculum_status='partial', requirements=requirements, courses=list(courses))


def parse_pool(html, key):
 path, heading, credits = POOLS[key]
 url = BASE+'general-education-requirements/'+path
 root = content(html, heading)
 table = root.find('table', class_='sc_courselist')
 if table is None: raise ValueError('NJIT approved course table missing')
 sid=PID+'-'+key; courses=[]; wildcards=[]
 for row in table.find_all('tr'):
  cells=row.find_all('td',recursive=False)
  codecell=row.find('td',class_='codecol')
  if codecell is None: continue
  code=clean(codecell.get_text(' ',strip=True)); name=clean(cells[1].get_text(' ',strip=True))
  if re.fullmatch(r'[A-Z]+\d* [23]\*\*',code):
   wildcards.append(code+' — '+name);continue
  if not re.fullmatch(r'[A-Z]+\d* \d+[A-Z]?',code): raise ValueError('Unexpected approved course code: '+code)
  hours=clean(cells[-1].get_text(' ',strip=True))
  if hours and not re.fullmatch(r'\d+',hours): raise ValueError('Unexpected approved course credit')
  courses.append(course('njit',code,name,sid,url,credits=int(hours) if hours else None,category='human_context' if key!='njit-natural' else 'other'))
 if not courses: raise ValueError('Empty approved course pool')
 if len({c['id'] for c in courses})!=len(courses): raise ValueError('Duplicate approved course')
 summary='Approved options for the corresponding GER allocation; this pool does not add credits to the 120-credit degree plan. Individual credit amounts remain unknown where the table leaves them blank.'
 if key=='njit-natural': summary+=' The GER requires laboratory experience; listed courses are options, not interchangeable lecture/lab combinations. Published R216 206 value is retained as 3 credits.'
 if wildcards: summary+=' The source also permits these open subject/level categories: '+'; '.join(wildcards)+'. These are eligibility rules, not individual courses.'
 return observed([rule(PID+'-'+key,heading+' approved options',sid,[c['id'] for c in courses],kind='note',credits=credits,summary=summary)],courses)

# Each material rule is guarded against changed source wording; numeric changes fail review.
GER_RULES = [
 ('computing','Computing literacy',['minimum of 3 credits','introductory computing course covering the foundations of computational thinking'], 'Complete at least 3 credits in introductory computational thinking; consult the linked approved list. The degree plan specifies its own computing courses.'),
 ('cultural','History and humanities progression',['minimum of 18 credits','6 credits of introductory communication','3 credits of History and Humanities courses at the 200 level','6 credits of History and Humanities courses at the 300 level','3 credits of an HSS senior seminar'], 'At least 18 credits: ENGL 101 and 102 (6), 200-level history/humanities (3), 300-level history/humanities (6), and HSS senior seminar (3). These describe the plan’s GER allocations, not additional requirements to sum again.'),
 ('quantitative','Quantitative reasoning',['minimum of 6 credits','one course having content in probability and statistics'], 'At least 6 introductory quantitative-reasoning credits, including probability/statistics content in one course; degree-specific mathematics/statistics courses remain in the plan.'),
 ('science','Scientific literacy laboratory condition',['minimum of 7 credits','including a laboratory experience'], 'At least 7 natural-science credits including laboratory experience. The plan divides these into 3-credit and 4-credit slots; the source does not provide a blanket lecture/lab pairing rule.'),
 ('social','Social science literacy',['minimum of 3 credits','social science or management-related course'], 'At least 3 credits in appropriate social science or management-related study; consult the approved list and degree-specific courses.'),
 ('seminar','First-year seminar',['All first-time, full-time freshman students','required to attend a first year seminar'], 'First-time full-time freshmen must attend first-year seminar; the plan lists FYS SEM at zero credits.'),
 ('scope','GER minima and degree-specific requirements',['Each college or department may set additional requirements that exceed the GER'], 'GERs are university minima. College and department requirements may exceed them; neither an eligible pool nor a minimum certifies permission to reuse one course in multiple degree slots.'),
]
POLICY_RULES = [
 ('graduation','Graduation and major GPA',['cumulative grade point average of 2.0','cumulative GPA of 2.0 in the upper division course requirements','file an application for graduation'], 'Complete the curriculum, attain a cumulative 2.0 GPA in its required courses and a 2.0 GPA in department-defined upper-division major requirements, and submit the graduation application by the university deadline.'),
 ('residency','Transfer-student upper-division residency',['in residence at NJIT, at least 33 credits in upper division courses approved by the department'], 'Transfer students must complete at NJIT at least 33 upper-division credits approved by their major department.'),
 ('transfer','Transfer equivalence and grades',['does not have a specific credit limit','minimum grade of C','official transcript'], 'Transfer credit requires course equivalence, a minimum C grade and official transcript documentation. There is no general transfer-credit cap, but the NJIT upper-division residency requirement applies. Foreign coursework needs the stated evaluation and descriptions.'),
 ('outside','Courses taken at another institution',['prior to enrolling in the course','grade earned is a "C" or higher','maximum of two (2) humanities or social science GER-equivalent courses','capstone seminar in humanities and social science must be taken at NJIT','only if the course(s) is (are) not offered at NJIT during the summer','eight (8) weeks or more','six (6) weeks or more'], 'Outside the cross-registration program, obtain prior department approval and the registrar/home-department signatures, then provide an official transcript with C or higher. At most two humanities/social-science GER equivalents may be taken elsewhere during summers; the HSS capstone must be at NJIT. Summer Rutgers-Newark/Essex courses are permitted only when unavailable at NJIT. Summer calculus I/II courses elsewhere must span at least eight weeks and physics I/II at least six.'),
 ('repetition','Course repetition limit',['no more than four times','including withdrawals','permanently ineligible for that program'], 'A course may be attempted at most four times across NJIT and other institutions, including withdrawals. Four unsuccessful attempts at a required course make the student ineligible for programs requiring it. Repeating excludes only the lowest grade from the cumulative GPA; other grades remain. Forgoing incoming transfer credit is irreversible.'),
 ('expiration','Expiration of earned credits',['course credits normally expire ten years','extension of these course credits','over 10 years old','evaluated by the relevant academic department'], 'NJIT course credits normally expire after ten years and must be replaced unless the offering/approving department grants an extension. External coursework older than ten years requires departmental applicability review; transfer-credit procedures depend on associate-degree status.'),
 ('unsatisfactory','Unsatisfactory work earns no degree credit',['Credits for courses in which U is received cannot count toward a degree'], 'U grades do not earn degree credit. S/U reports progress in the specified co-op, teaching methods, ESL and physical education courses; this is not a general elective pass/fail permission.'),
]

def parse_rules(html, kind):
 rows=GER_RULES if kind=='ger' else POLICY_RULES
 heading='General Education Requirements' if kind=='ger' else 'Academic Policies and Procedures'
 root=content(html,heading);sid=PID+'-njit-'+kind
 result=[]
 for suffix,title,phrases,summary in rows:
  require_phrases(root,phrases)
  result.append(rule(PID+'-njit-'+kind+'-'+suffix,title,sid,kind='note',summary=summary))
 return observed(result)

SOURCE_PARSERS={BASE+'general-education-requirements/'+v[0]:partial(parse_pool,key=k) for k,v in POOLS.items()}
SOURCE_PARSERS[BASE+'general-education-requirements/']=partial(parse_rules,kind='ger')
SOURCE_PARSERS[BASE]=partial(parse_rules,kind='policies')
