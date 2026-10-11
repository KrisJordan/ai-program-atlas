"""Public COLL eligibility criteria, without invented finite course pools."""
import hashlib
from functools import partial
from atlas.adapters.national_curriculum_common import clean,content,require_phrases,rule
from atlas.adapters.william_mary_ba_policy_review import PID

SPECS={
 'scope':('https://www.wm.edu/as/undergraduate/coll/index.php','The College Curriculum',[
  ('scope','COLL applies across undergraduate schools',['All W&M undergraduate students share the College Curriculum','not to replace COLL 100, 200, 300, 350, or 400'], 'The public overview expressly applies COLL to all W&M undergraduates, including this CDSP-hosted BA. AP/IB may support domain electives and proficiencies but do not replace the named COLL sequence. Specific transfer exceptions are mapped separately.'),
 ]),
 'guide':('https://www.wm.edu/as/undergraduate/coll/coll-planning-guide/index.php','COLL Planning Guide',[
  ('firstyear','First-year COLL requirements',['COLL 100 (one course, must pass with at least C-)','COLL 150 (one course, must pass with at least C-)','Take your COLL 100 and COLL 150 courses in the first year'], 'Complete one designated COLL100 and one COLL150 in the first year, each at C− or better, subject to the explicit incoming-transfer exceptions. These are designation criteria, not individual course identities.'),
  ('domains','COLL200 and separate domain electives',['Knowledge Domain Electives (3 courses)','ALV (minimum of 3 credits)','CSI (minimum of 3 credits)','NQR (minimum of 3 credits)','COLL 200 (9 total credits)'], 'Complete three knowledge-domain electives, at least three credits each in ALV, CSI and NQR. Separately, COLL200 requires nine credits with at least three in each domain. The same course cannot satisfy both a required COLL allocation and a domain elective; transfer exceptions may alter the applicable selection.'),
  ('upper','Upper COLL designation requirements',['COLL 300 (1 course or more, totaling 3 credits)','COLL 350 (1 course or more, totaling 3 credits)','COLL 400 (1 course, minimum of 3 credits)'], 'Complete at least one designated course totaling three credits for COLL300, similarly three credits for COLL350, and one COLL400 course of at least three credits. These open attribute criteria do not claim an exhaustive finite course pool or automatically equate the major capstone with COLL400.'),
  ('language','Foreign-language proficiency alternatives',['202 (Level IV)','Taking 4 years of a foreign language (one language) in high school','Receiving AP, IB or transfer credit for the 202 level or higher','Completing a college-level course at the 202 level or above','native language is not English'], 'Demonstrate natural-language proficiency other than English at level 202/IV through four high-school years in one language, qualifying AP/IB/transfer credit, a college 202-or-higher course, or an approved native-language exemption petition. Satisfying an alternative removes the general additional-language-course obligation; no student exemption is assumed.'),
  ('proficiencies','Mathematics, arts and overlap criteria',['Pre-matriculation transfer or test credit for a course in calculus or statistics','Any William & Mary course with the "MATH" attribute','"Arts Proficiency" attribute','a single course can fulfill both a proficiency and a COLL requirement','can\'t serve as both a required COLL course and a Knowledge Domain elective'], 'Mathematics proficiency accepts pre-matriculation calculus/statistics credit or a W&M MATH-attribute course. Creative/performing arts uses the Arts Proficiency attribute. A single course may satisfy a proficiency and COLL requirement, but cannot fill both a required COLL and a knowledge-domain elective. No extra fixed course is inferred when an approved proficiency alternative is met.'),
 ]),
 'other':('https://www.wm.edu/as/undergraduate/coll/other-requirements/','Other College Curriculum Requirements',[
  ('arts','Creative and performing arts minimum',['at least two credits','course that teaches a creative or performing art'], 'Creative/performing-arts proficiency requires at least two credits of instruction in an eligible art. Eligibility is the published attribute, not every course mentioning music, theatre or art.'),
  ('total','Published undergraduate total and pre-matriculation credit',['120 credits to graduate','can\'t be used as a substitute for COLL courses','ten semester rule','credit hour residency'], 'The public overview states 120 credits to graduate and permits qualifying AP/IB toward that total, domain electives, proficiencies and some major requirements. It points to the catalog for detailed ten-semester and credit-residence rules; those detailed conditions are not invented from this summary.'),
 ]),
 'transfer':('https://www.wm.edu/as/undergraduate/coll/bor-transfer-students/index.php','COLL Curriculum Rules and Requirements for Incoming Transfer Students',[
  ('general','General incoming-transfer COLL conditions',['at least two full-time college semesters post-high school','All students must take COLL 150 at W&M','graded with “C” 2.0 or higher','COLL 350 and 400','after matriculation'], 'The general transfer rules waive COLL100 after at least two full-time post-high-school semesters for entering social sophomores/juniors, require COLL150 at W&M, and place COLL350/400 after matriculation. A prior significant study-abroad/away experience may qualify for COLL300 by application with at least three transferable credits graded C/2.0 or better, transcript and syllabus. Specific tabulated pathways provide additional COLL200/domain exceptions.'),
  ('pathways','Source-specific incoming-transfer exceptions',['Transfers with VCCS Passport Designation on VCCS Transcript','Transfers with VCCS Uniform Certificate of General Studies','Two courses waived','One course waived','Student must take two COLL 200 courses','VCCS or RBC AA, AFA, AS, AA&S-holders'], 'The published tables waive mathematics proficiency and all three domain-elective allocations for VCCS Passport, VCCS Uniform Certificate and the listed post-high-school VCCS/RBC associate-degree groups. Passport retains all three COLL200 courses. Uniform Certificate with two post-high-school full-time semesters and the listed associate-degree holders retain one in-residence COLL200 in any domain. Other transfers with at least two such semesters retain two in-residence COLL200 courses in any domain and receive the domain-elective waivers, but no automatic math waiver. COLL150 remains at W&M; COLL350/400 follow matriculation; language/arts still need qualifying evidence. No pathway is assigned without its actual admission credential.'),
  ('standing','Transfer standing and proficiency scope',['junior standing (at least 54 credit hours)','first through course-by-course transfer credit evaluation','Effective Fall 2015','amended in Spring 2022'], 'The source, effective Fall 2015 and amended Spring 2022, grants eligible VCCS/RBC university-parallel associate holders junior standing with at least 54 credits through evaluation and if needed academic electives. Applicable transfer/test credits can support proficiencies and domains, but cannot replace COLL150/200/350/400 outside the explicit tabulated waivers. These source policy dates are not this program’s start date. Table language shorthand says three or four high-school years while the general planning guide specifies four; exact student language applicability still needs authoritative clarification.'),
 ]),
}


TRANSFER_TABLE_DIGEST='d5289e59c813728f277a84b3a0ea8f9a8fa1e9015b5f6ad04e669e1bff1e9e63'

def parse(html,key):
 url,heading,rows=SPECS[key];root=content(html,heading);out=[]
 if key=='transfer':
  tables=root.find_all('table')
  observed=hashlib.sha256('\n'.join(clean(t.get_text(' ',strip=True)) for t in tables).encode()).hexdigest()
  if len(tables)!=6 or observed!=TRANSFER_TABLE_DIGEST:raise ValueError('Transfer pathway tables changed; review exact exceptions')
 for suffix,title,phrases,summary in rows:
  require_phrases(root,phrases)
  out.append(rule(PID+'-coll-'+key+'-'+suffix,title,PID+'-coll-'+key,kind='note',summary=summary))
 return dict(id=PID,courses=[],requirements=out)


def register(parsers):
 for key,(url,_,_) in SPECS.items():
  if url in parsers:raise ValueError('Duplicate COLL source')
  parsers[url]=partial(parse,key=key)
