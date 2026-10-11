"""Finite college-policy supplements with explicit conditional program scope."""
from bs4 import BeautifulSoup
from atlas.adapters.northeastern_policies import text, section, need
from atlas.adapters.national_curriculum_common import rule

PREFIX='northeastern-university-artificial-intelligence-and-'
CSSH_PROGRAMS={PREFIX+s+'-bs-boston-bs-degree' for s in ['criminal-justice','economics','international-affairs','philosophy','sociology']}
BUSINESS=PREFIX+'business-administration-bs-boston-bs-degree'
CSSH_CATALOG='https://catalog.northeastern.edu/undergraduate/social-sciences-humanities/'
CSSH_CHANGE='https://cssh.northeastern.edu/declare-a-major-and-minor/'
CSSH_PROGRESS='https://cssh.northeastern.edu/academic-progression-standards/'
BUSINESS_CATALOG='https://catalog.northeastern.edu/undergraduate/business/'


def catalog(html,title):
    soup=BeautifulSoup(html,'html.parser');heading=soup.select_one('#site-title h1');panel=soup.select_one('#textcontainer')
    if heading is None or text(heading)!=title or panel is None or '2026-2027' not in soup.get_text(' ',strip=True):
        raise ValueError('Expected current college catalog identity missing')
    return panel


def cssh_page(html,title):
    soup=BeautifulSoup(html,'html.parser')
    for node in soup.select('nav,aside,script,style,footer'):node.decompose()
    panel=soup.select_one('main#content');heading=panel.find('h1')if panel else None
    if heading is None or text(heading)!=title:raise ValueError('Expected CSSH advising policy identity missing')
    return panel


def observe_cssh(html,*,program_id,source):
    if program_id not in CSSH_PROGRAMS:raise ValueError('Unreviewed CSSH program scope')
    if source==CSSH_CATALOG:
        panel=catalog(html,'College of Social Sciences and Humanities')
        need(section(panel,'Graduation Clearance Process'),'required to meet with an academic advisor','Some departments also require a meeting with a faculty advisor','completed in the junior year')
        need(section(panel,'Experiential Liberal Arts Requirement'),'majors or combined majors entirely within CSSH')
        suffix='cssh-catalog-supplement';title='Conditional CSSH graduation clearance'
        summary='If subject to CSSH graduation-clearance rules, meet the academic advisor in the junior year to plan remaining requirements; some departments additionally require a faculty-advisor meeting. The catalog’s Experiential Liberal Arts course requirement is limited to majors/combined majors entirely within CSSH and is not imposed on this verified Khoury/CSSH combination. Universal progression and degree requirements are already represented.'
    elif source==CSSH_CHANGE:
        panel=cssh_page(html,'Declaring a CSSH Major or Minor');prose=text(panel)
        need(prose,'all international students must first submit their intent to change their major','F-1 & J-1 International Students','All students should book an appointment and meet with the CSSH academic advisor','strongly recommended','may be denied entrance','offered provisional acceptance','following International Affairs majors and combined majors')
        # The explicitly enumerated 2.500 rule is not broadened to AI/International Affairs.
        suffix='cssh-change-supplement';title='Conditional CSSH major-change process'
        summary='For a change into a CSSH major, meet the intended major’s academic advisor. F-1/J-1 students first submit the stated intent-to-change form. Meeting the faculty program director is strongly recommended, not mandatory. Students not meeting applicable entry/standing criteria may be denied, deferred until grades post or provisionally accepted. The page enumerates particular International Affairs combinations for its 2.500 entry/2.000–2.499 transition rule; it does not list AI and International Affairs, so those numeric criteria are not assigned to this degree.'
    elif source==CSSH_PROGRESS:
        panel=cssh_page(html,'Academic Progression Standards');prose=text(panel)
        need(prose,'minimum cumulative GPA of 1.8','minimum cumulative GPA of 2.0','minimum of 12 credits','after two full-term academic semesters','first day class offerings are posted on the web','schedule a meeting with a CSSH academic advisor','dismissed more than once may also appeal')
        suffix='cssh-reentry-supplement';title='Conditional CSSH dismissal appeal and re-entry'
        summary='For re-entry after dismissal to CSSH, submit its Academic Dismissal Appeal Form by the first day class offerings are posted for the intended return term, and arrange a CSSH advisor meeting for next steps. A first dismissal is appeal-eligible; additional dismissals may be appeal-eligible in some cases. Re-entry is not granted automatically. The page repeats university standing/probation thresholds, which are not added as duplicate degree obligations.'
    else:raise ValueError('Unreviewed CSSH policy source')
    return dict(id=program_id,courses=[],requirements=[rule(program_id+'-conditional-'+suffix,title,program_id+'-'+suffix,kind='note',summary=summary)],notes=['Conditional college process only; no home-college designation, individual approval or new required course inferred.'])


BUSINESS_RULES=[
 ('progression','Academic Progression Standards',['2.000 grade-point average in business courses','at least 32 semester hours','make up the difference prior to graduation','at least 16 semester hours','8 semester hours each in-school summer half semester','may be subject to dismissal'],
  'Where D’Amore-McKim progression rules govern the student, require business GPA2.000 in addition to university standards. First-year progression requires32 earned hours; any shortfall must be made up before graduation. After the first year, earn16 hours per in-school full semester and8 per in-school summer half-semester to advance class standing. Failure leads to probation and possible, not automatic, dismissal. These progression quantities are not extra courses added to degree totals.'),
 ('su','Satisfactory/Unsatisfactory Option',['nonbusiness courses that will count as open electives only'],
  'For D’Amore-McKim students, satisfactory/unsatisfactory grading is limited to nonbusiness courses counting only as open electives, subject to university policy; it cannot silently satisfy business requirements.'),
 ('coop-study','Taking Courses While on Co-op',['one class either online or in person','should not interfere','prior written approval of their co-op coordinator and academic advisor','maximum of two courses or 8 semester hours'],
  'While on co-op, a student may take one class online or in person without interfering with work duties/hours. Prior written approval from both the co-op coordinator and academic advisor permits at most two courses or8 hours. Approval availability is not approval granted.'),
 ('external-transfer','External Transfer to the D’Amore-McKim School of Business',['maximum of 50%','core business courses required','Normally, upper-division courses (3000 and 4000 level) are not transferable','Undergraduate Programs office'],
  'For external transfer into D’Amore-McKim, business transfer credit is capped at50% of required business-core credits in the student’s program. Upper-division3000/4000 coursework is normally not transferable; consult the Undergraduate Programs office for program-specific credit determinations. This is not a blanket ban or an equivalence approval.'),
 ('graduation','Graduation Requirements',['Bachelor of Science degree candidates must complete all prescribed work','A GPA of 2.000 and a C average in all business courses'],
  'If graduating under D’Amore-McKim rules, complete the prescribed degree curriculum, overall GPA2.000 and a C average in all business courses. The exact combined degree independently specifies its business GPA2.000 rule. College policy does not replace the program’s own eligible concentration list or change its BS award.'),
]


def observe_business(html,*,program_id):
    if program_id!=BUSINESS:raise ValueError('Unreviewed Business program scope')
    panel=catalog(html,"D'Amore-McKim School of Business");prose=text(panel)
    need(prose,'all students are required to complete a cooperative education plan','academic advisor and co-op coordinator','Students should consult their degree program and catalog term')
    sid=program_id+'-business-college-policy';root=program_id+'-conditional-business-policy'
    rows=[rule(root,'Conditional D’Amore-McKim college policies',sid,kind='note',summary='Apply these rules only when the student’s actual D’Amore-McKim college, enrollment and transfer circumstances make them applicable. Admissions verifies participation in this combined BS; it does not establish the student’s home-college/cohort assignment.')]
    for key,title,guards,summary in BUSINESS_RULES:
        need(section(panel,title),*guards)
        rows.append(rule(root+'-'+key,title,sid,parent=root,kind='note',summary=summary))
    rows.append(rule(root+'-coop-plan','Conditional cooperative education planning',sid,parent=root,kind='note',summary='The college requires a cooperative education plan developed with academic/co-op advising; eligibility and participation timing depend on the academic plan. Preserve this planning requirement alongside the degree’s explicitly allowed practicum, internship and co-op experience alternatives; do not invent a universal additional co-op placement or credit amount.'))
    return dict(id=program_id,courses=[],requirements=rows,notes=['D’Amore-McKim participation and published conditions are preserved without assigning a home college, granting approval or importing unrelated degree-specific rules.'])
