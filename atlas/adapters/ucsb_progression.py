"""UCSB public progression, transfer and approval policies; PDF review is explicit."""
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import text,requirement
from atlas.adapters.ucsb_policies import PID,body,guarded,GEAR_URL
BASE='https://engineering.ucsb.edu/'
TRANSFER_URL=BASE+'undergraduate/academic-advising/credit-transfers'
REPEAT_URL=BASE+'undergraduate/academic-advising/repeating-courses'
PROGRESS_URL=BASE+'minimum-cumulative-progress'
NOTICE_URL=BASE+'undergraduate/academic-advising/academic-probation-academic-disqualification'
PETITION_URL=BASE+'undergraduate/academic-advising/petitions'
FAQ_URL='https://ai.cs.ucsb.edu/faq'


def node(key,title,source,summary):
    return requirement(PID,'progress-'+key,title,PID+'-'+source,unit='quarter_hours',category='other',kind='note',summary=summary)


def output(rows):return dict(id=PID,curriculum_status='partial',requirements=rows)


def parse_transfer(html):
    v=body(html,'Transferring Credits from Courses Taken at Other Institutions')
    guarded(v,['grade of D- or greater','maximum of 105 transfer units','All courses taken at a community college are considered lower division','summer 2019 through now','International students must receive prior approval'])
    return output([
      node('transfer-general','Transfer credit, GPA and duplication','transfer-credit','Determine intended degree use before enrollment elsewhere. Non-UC courses can supply unit/subject credit but do not enter UC GPA; other UC grades do. Existing UCSB credit at D− or higher normally prevents duplicate external credit. An F permits external subject/unit credit but non-UC work does not replace the original UC GPA grade.'),
      node('transfer-community','Community-college transfer limits','transfer-credit','At most105 community-college quarter units transfer; later courses may earn subject credit only. All community-college credit is lower division even if its UCSB equivalent is upper division. California community-college articulation uses ASSIST; individual course suitability is not inferred from this general rule.'),
      node('transfer-repeat','Other UC repeat authorization','transfer-credit','Another UC course can be an authorized repeat for UCSB C− or lower when the offering department verifies identical material. Mathematics equivalencies for other UC courses from Summer2019 are stated to apply automatically, including repeat coding. Regular-term study at another UC needs advance advising and is rarely approved; summer enrollment follows its own process.'),
      node('concurrent','Concurrent enrollment and GE writing','transfer-credit','Domestic students in regular status can enroll concurrently elsewhere without college approval; academic-notice students need prior approval, often denied. International students need OISS approval. The general transfer page limits special-subject writing to UCSB; the separately reviewed petitions page expressly permits up to two approved UCEAP exceptions.')])


def parse_repeat(html):
    v=body(html,'Repeating Courses');guarded(v,['C-, D+, D, D-, F, or NP','first 16 units repeated','Second attempts of W graded courses','prior approval of their college provost or dean'])
    return output([node('repeat','Repeat eligibility and GPA calculation','repeats','Repeat only C−,D+,D,D−,F or NP. Major courses still require letter grading; NP cannot replace an earlier letter grade in GPA. Third enrollment needs prior college approval. Credit counts once and every grade stays on the transcript. For the first16 repeated units only the latest letter grade counts in GPA; beyond16 both attempts count. Second attempts after W do not consume the16-unit allowance. Cross-UC equivalency must be approved before repetition; identify repeats at registration.')])


def parse_progress(html):
    v=body(html,'Minimum Cumulative Progress');guarded(v,['90-105 units','less than 90 units or more than 105 units','previous two consecutive MCP quarters','12 regular quarters','9 regular quarters','215 units'])
    s=BeautifulSoup(html,'html.parser');table=next((t for t in s.find_all('table')if 'Units Completed'in text(t)),None)
    if not table:raise ValueError('MCP threshold table missing')
    thresholds=[]
    for tr in table.find_all('tr'):
        cells=[text(c)for c in tr.find_all(['th','td'])]
        if len(cells)==2 and cells[0].isdigit()and cells[1].isdigit():thresholds.append((int(cells[0]),int(cells[1])))
    if [q for q,_ in thresholds]!=list(range(1,13)):raise ValueError('MCP quarter inventory changed')
    return output([
      node('mcp-thresholds','Minimum cumulative progress table','progression','Regular-quarter minimum enrollment is12units. Published completed-unit targets by MCP quarter: '+', '.join(str(q)+': '+str(n)for q,n in thresholds)+'. Thresholds are progress targets, not additional degree-credit requirements.'),
      node('mcp-entry','MCP entry pathways','progression','First-year admits count only post-matriculation units for MCP; earlier AP/IB/college credit can still count toward graduation. Transfers entering with90–105units start at MCPquarter7 and count transferred units. Transfers below90or above105start at quarter1 and count units after first UCSB enrollment, including the immediately preceding UCSB summer.'),
      node('mcp-deficit','MCP deficit review','progression','Two consecutive MCP deficits can trigger an academic-notice contract; two further consecutive deficits can make the student subject to dismissal. An exception needs appropriate college approval; dismissal is not inferred automatically from an observed unit count.'),
      node('enrollment-limit','Enrollment quarter and unit limits','progression','Expected graduation within12regular quarters for first-year admits or9for junior transfers, and no more than215units. Pre-high-school-graduation credit, including AP/IB, is excluded from215. Summer does not consume regular quarters but its units count. Non-summer outside study after leaving can reduce available UCSB quarters proportionally. Further enrollment requires specific approval and a complete Proposed Schedule for Graduation; exceptions are limited.')])


def parse_notice(html):
    v=body(html,'Academic Probation & Academic Disqualification');guarded(v,['first two weeks of the quarter','less than 1.5 for that quarter','After two consecutive quarters on academic notice','Courses passed by examination','Courses graded IP'])
    return output([
      node('notice','Academic notice and review','academic-notice','Cumulative UC GPA below2.0 automatically triggers notice. The college may also act on major/upper-major GPA below2.0 or inadequate major progression. Meet advising in the first two weeks, obtain an approved schedule and enrollment agreement, and undergo end-of-quarter review.'),
      node('disqualification','Disqualification thresholds and appeal','academic-notice','Subject to disqualification after any quarter GPA below1.5, quarter GPA below2.0 while on notice, or cumulative UC GPA still below2.0 after two notice quarters. Advisors and Associate Dean review whether to continue notice or dismiss; thresholds do not mean automatic dismissal. Appeal requires Academic Self Assessment and Study Plan by the stated individual deadline. Regular-term reentry after dismissal requires reinstatement on notice.'),
      node('mcp-countable','MCP countable work and exceptions','academic-notice','MCP can count repeats of C−/D/F, courses passed by examination, IP work, and passed summer courses at UCSB or transferable accredited institutions. Exceptions to minimum progress require dean/designee approval for special circumstances.')])


def parse_petitions(html):
    v=body(html,'Forms');guarded(v,['more than 21 units','more than 16 while on academic notice','earn a B or higher','may petition up to two courses','This petition may not be used for UCSB courses','who do not intend to remain permanently'])
    return output([
      node('petition-ge','GE transfer substitution and EAP writing exception','petitions','Transferable courses may be petitioned for general areas A/D/E/F/G and special Ethnicity/World Cultures/European Traditions with a syllabus. The special writing requirement is UCSB-only except up to two UCEAP courses may be petitioned. An already-articulated or clearly eligible transfer/EAP course may not need a petition after advising confirmation. This petition cannot turn an unapproved UCSB course into GE: UCSB GE requires Academic Senate approval.'),
      node('petition-repeat','Second repeat approval','petitions','Third enrollment requires a rationale and study plan, is rarely approved, and carries an expectation of B or better. A major-course repeat needs both major and college approval; GE needs college approval. Cross-UC legal repeats require departmental equivalency evidence before taking the course and the legal-repeat petition after completion.'),
      node('petition-load','Excess and deficit enrollment approval','petitions','Excess approval is needed above21units, or16on academic notice, after Pass2 enrollment with an accurate Pass3 plan; scheduling conflicts are not approved. Below12units needs deficit approval for documented medical/family circumstances, at least20hours weekly employment while in good standing and on-time graduation plan, or the final quarter. International students use OISS reduced-course-load approval instead. Permanent/multiquarter deficits are generally not approved.'),
      node('petition-changes','Late enrollment and grade-option changes','petitions','Late adds/drops or grading-option changes require exceptional circumstances and review. Poor performance, changing interests/major or workload are not late-drop grounds; weeks8–10/retroactive requests receive greater scrutiny. Grade-option petitions apply only to optional-grading courses, never letter-only courses. A late graduate-course add also needs the signed undergraduate-in-graduate-course petition. Final add/drop decisions belong to the Associate Dean.'),
      node('petition-ahi','American History waiver qualification','petitions','F1/J1 or other nonimmigrant students who do not intend to remain permanently in the US may petition for an AHI waiver through Graduation Matters; the waiver is not automatic.'),
      node('petition-double','Double-major and extension approvals','petitions','Two Engineering degrees cannot be double majors. A cross-college double major requires receiving-major advising and a study plan. A plan for enrollment beyond12first-year/9transfer quarters or215units must account for all remaining requirements; incomplete or incorrect plans are denied. Approval is not guaranteed.')])


def parse_faq(html):
    v=body(html,'FAQ');guarded(v,['Transfer admits into the AI major will start in 2028','Starting in the 2028–29 academic year','No. All requirements are listed on the Curriculum page','No. The degree is designed as a cohesive program','AI and machine learning engineering','AI safety, ethics, and policy'])
    r=output([node('ai-entry','AI program entry and double-major restrictions','faq','Fall2026 entry is through the initial interest process for admitted CS students. Current-student change applications and transfer AI admission begin in2028–29/2028. The FAQ warns Fall2026 admits will have too many quarters to change into CS by2028. CS+AI double major is prohibited. No formal emphases/tracks are offered.'),node('ai-curriculum','AI FAQ curriculum scope','faq','The FAQ states that all degree requirements are listed on the Curriculum page and there are no hidden additional requirements. Its generic curriculum capstone description still lacks an identified course/rule; this is retained as an unresolved interpretation, not an invented extra requirement.')])
    r['outcomes']=[dict(text='The program presents AI/ML engineering, applied AI, research, and AI safety/ethics/policy as possible career directions, and describes preparation for further AI study.',kind='source_stated',statement_type='career_pathway',source_id=PID+'-faq',locator='FAQ: Will this limit my career options?')]
    return r


def parse_gear_ahi_observation(rows):
    """Reviewer-transcribed PDF13 entries; never an automatic HTML refresh."""
    if not rows or any(len(r)!=2 or not all(r)for r in rows):raise ValueError('Invalid reviewed AHI rows')
    nodes=[node('ahi-pool','GEAR American History approved course expressions','gear-2026','One four-unit approved course can satisfy AHI. Department lists preserve ranges/suffix sequences literally; they do not imply that every course in a bundle must be taken. Credits, titles and enrollment eligibility for individual entries remain unknown.')]
    for i,(department,expression)in enumerate(rows):nodes.append(node('ahi-row-'+str(i),department+' approved AHI options','gear-2026','GEAR PDF page13 approved expression: '+department+' '+expression+'. Preserve original suffix/range notation and verify the chosen individual course; no invented expansion of AA–ZZ or AL–S ranges.'))
    nodes.extend([node('gear-igetc','Engineering IGETC substitution','gear-2026','GEAR PDFpage13 explicitly permits completed IGETC to substitute for the entire Engineering GE pattern for transfers; it does not satisfy AHI. This is a conditional GE route, not a waiver of major or other university requirements. The page does not establish CalGETC treatment.'),node('gear-ahi-ap','Current GEAR AHI exam route','gear-2026','GEAR PDFpage13 includes AP African American Studies, US Government and Politics, or US History at score3or higher. The older college HTML omits African American Studies; retain the more specifically dated source qualification.'),node('gear-area-a','GEAR Area A grading','gear-2026','GEAR PDFpage14 expressly requires both Area A writing courses to be letter graded. The later general GE P/NP permission is subject to this specific requirement, rather than an unrestricted waiver.')])
    return output(nodes)

WRITING_URL='https://writing.ucsb.edu/writing-requirements/required-writing-courses-guide/writing-1'
GUIDANCE_URL='https://docs.google.com/document/d/1xv_XkiaO96-auzyBcvjVDXFWX8yhDzl9fHB8XVxeWYQ/edit?usp=sharing'


def parse_writing(html):
    import re
    from atlas.adapters.cmu_bs.common import course
    body(html,'Writing 1');s=BeautifulSoup(html,'html.parser');courses=[]
    for h in s.find_all('h3'):
        m=re.fullmatch(r'Writing (1E?)\. (.+)',text(h))
        if not m:continue
        b=h.find_next_sibling('p');v=text(b);u=re.search(r'(\d+) units',v)
        pre=b.find('em')if b else None
        if not u or not pre:raise ValueError('Writing course credit/prerequisite layout changed')
        c=course('WRIT '+m[1],m[2],PID+'-writing-course',WRITING_URL,institution='ucsb',unit='quarter_hours',credits=int(u[1]),category='human_context')
        c['prerequisites']=text(pre).removeprefix('Prerequisite:').strip()
        courses.append(c)
    if {c['code']for c in courses}!={'WRIT 1','WRIT 1E'}:raise ValueError('Writing1 course inventory changed')
    r=output([node('writing-course','Entry writing course alternatives','writing-course','WRIT1 and1E each carry four units and satisfy ELWR. They are placement-dependent alternatives, not both required. WRIT1 excludes credit after English1,WRIT1E or1LK; WRIT1E requires Engineering enrollment. Minimum-grade and timing rules remain in the separately reviewed university policy.')]);r['courses']=courses;return r


def parse_guidance_observation(value):
    """Review of a public two-page document export, not its unreadable HTML shell."""
    guarded(value,['Writing Requirement Petition Information Sheet','at least 25%','Papers in languages other than English','10/2025','individual student basis'])
    return output([node('writing-eap-guidance','UCEAP writing petition evidence','writing-guidance','October2025 guidance permits at most two UCEAP writing substitutions for Fall1999-onward admits, individually approved and not transferable to classmates. Supply the term syllabus, every paper and a short explanation of writing instruction/feedback. One-to-three non-exam papers must total at least1800words excluding ancillary material and represent at least25% of the course grade; evidence must show writing instruction or feedback and proficiency in the writing outcomes. Non-English papers may be considered. Unapproved UCSB courses cannot use this petition.')])
