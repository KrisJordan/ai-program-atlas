"""Shared UC/UCSD rules and reviewed approval-table observations."""
import re
from atlas.adapters.cmu_bs.common import course, requirement, slug
from atlas.adapters.ucsd_degree_policies import PID, body, guarded
UC_WRITING_URL='https://admission.universityofcalifornia.edu/elwr/'
SENATE_URL='https://senate.ucsd.edu/Operating-Procedures/Senate-Manual/Regulations/600'
CLIMATE_URL='https://undergrad.ucsd.edu/academics/jtccer.html'
DEI_PDF='https://senate.ucsd.edu/media/513521/dei-list-of-courses.pdf'
CLIMATE_PDF='https://senate.ucsd.edu/media/742288/jtccer-course-list-fa25.pdf'
DEGREE_URL='https://catalog.ucsd.edu/undergraduate/degree-requirements/index.html'


def req(key,title,sid,**kw):
    return requirement(PID,'shared-'+key,title,PID+'-'+sid,unit='quarter_hours',category='human_context',**kw)


def parse_uc_writing(html):
    v=body(html,'Write well at UC')
    guarded(v,['63 or better on ACT English + Reading','same exam sitting','digital SAT are not approved','3 semester or 4 quarter units','grade of "C" or better','July 15'])
    rows=[req('elwr-tests','UC entry-writing test alternatives','uc-elwr',kind='note',summary='Qualify through AP English Language/Literature, Seminar or Research at least 3; IB English LanguageA higher level at least 5 or standard level at least 6; ACT ELA at least 30 or combined English+Reading at least 63 from one sitting; or pre-March 2024 paper SAT reading/writing at least 680. Digital SAT and ACT English alone do not satisfy ELWR. Official test scores are due July 15; these placement uses do not imply admission-test use.'),
      req('elwr-course','UC entry-writing pre-enrollment course alternative','uc-elwr',kind='note',summary='Before UC enrollment, earn C or better in a UC-transferable composition course worth 3 semester or 4 quarter units at an institution accredited by a former regional accreditor. Otherwise follow the campus placement/completion route; UCSD’s specific AWP timeline remains separately represented.')]
    return {'id':PID,'curriculum_status':'partial','requirements':rows}


def parse_senate(html):
    v=body(html,'Regulations')
    guarded(v,['600. Campuswide Graduation Requirements','Fall 2024 or thereafter','Transfer students are not required','50 percent or more','approved as a distance education program','minimum residence','35 of the final 90 units','including the final 12 units'])
    return {'id':PID,'curriculum_status':'partial','requirements':[
      req('climate-scope','Climate requirement applicability','senate600',kind='note',summary='Regulation 600H applies to first-year/lower-division entrants from Fall 2024. Transfers are exempt. Pass one approved one-quarter course at C− or P or better; no four-unit minimum is inferred from the DEI rule.'),
      req('distance','Distance-education unit ceiling','senate600',kind='note',summary='Regulation 600B4, enacted June 3, 2025, prohibits 50 percent or more of UCSD-earned units from designated distance courses unless the major is approved as a distance-education program. No AI exemption is presumed.'),
      req('residence','Residence and approved external-program exceptions','senate600',kind='note',summary='Minimum UC residence is three terms; a summer course of at least 2 units can count as half a term. Normally 35 of final 45 units must be resident. Students completing all requirements in an approved EAP/UCDC/UC Sacramento/NRS ecology program may use the preceding 45 units; faculty may alternatively permit 35 of final 90, including final 12, resident units. Roosevelt’s 36/44 catalog discrepancy remains visible.') ]}


def parse_climate(html):
    v=body(html,'Jane Teranes Climate Change Education Requirement (JTCCER)')
    guarded(v,['Test-based credit (AP/IB) does not fulfill JTCCER','Incoming transfer students are exempt','prior to Fall 2024','overlap with existing general education'])
    return {'id':PID,'curriculum_status':'partial','requirements':[req('climate-credit','Climate course credit and overlap','climate-policy',kind='note',summary='AP/IB does not satisfy the climate requirement, including AP-derived ESYS 10 credit. Approved courses may overlap GE, DEI, major or minor requirements. First-time first-year entrants from Fall 2024 are covered; earlier matriculants and incoming transfers are exempt. Term offering lists are scheduling information, not the complete approved pool.')]}


def parse_approval_rows(rows, kind):
    """Parse reviewer-extracted PDF table cells; never an automatic PDF freshness claim.

    Every row retains its full printed code/approval qualifier. Complex aliases,
    paired service-learning codes and source typos stay row notes instead of
    guessed independent course identities or all-of/one-of rules.
    """
    if kind not in ['dei','climate']:raise ValueError('Unknown approval pool')
    sid=kind+'-approved-pdf';url=DEI_PDF if kind=='dei'else CLIMATE_PDF
    root=req(kind+'-pool',kind.upper()+' approved options with date restrictions',sid,
             kind='choose_courses',count=1,credits=4 if kind=='dei'else None,
             summary='Select one eligible approved option under its stated date, prerequisite and enrollment conditions. Historical expired and future approvals are retained for their stated periods, not asserted currently usable. Complex printed rows retain their unresolved internal notation.')
    courses={};nodes=[root];seen=set()
    for row in rows:
        if len(row['cells'])!=5 or not row['cells'][1]:raise ValueError('Approval row structure changed')
        _,code,name,prereq,date=[' '.join((x or '').split())for x in row['cells']]
        if not code or not name or not date:raise ValueError('Incomplete approval evidence')
        key=slug(code);key=key if key not in seen else key+'-'+str(row['page']);seen.add(key)
        ids=[]
        if re.fullmatch(r'[A-Z]+ \d+[A-Z]*',code):
            c=course(code,name,PID+'-'+sid,url,institution='ucsd',unit='quarter_hours',category='human_context')
            c['prerequisites']=prereq or None;courses[c['id']]=c;ids=[c['id']]
        summary=f'PDF page {row["page"]}, printed option {code}: {name}. Approval date/qualification: {date}.'
        if prereq:summary+=' Listed prerequisite/enrollment condition: '+prereq+'.'
        if not ids:summary+=' Composite notation is retained exactly; its courses are not expanded into inferred independent alternatives.'
        nodes.append(req(kind+'-option-'+key,code+' — approved option',sid,parent=root['id'],kind='note',course_ids=ids,summary=summary))
    if not rows:raise ValueError('Empty approval list')
    return {'id':PID,'curriculum_status':'partial','courses':list(courses.values()),'requirements':nodes}


def parse_ahi(html):
    v=body(html,'Undergraduate Degree Requirements')
    m=re.search(r'Any of the following courses are suitable for fulfilling the requirement: (.*?)\. By presenting proof',v)
    if not m:raise ValueError('AHI approved list missing')
    raw=m[1];guarded(raw,['any course listed under HIUS (other than HIUS colloquia)','HILD','USP'])
    records={}
    for section in raw.split(';'):
        section=re.sub(r',? or any course listed under HIUS \(other than HIUS colloquia\)','',section).strip()
        section=re.sub(r'^and ','',section);match=re.match(r'([A-Z]+) (.*)',section)
        if not match:raise ValueError('AHI department boundary changed')
        dept,tail=match.groups()
        for item in tail.split(','):
            item=re.sub(r'^'+dept+r'\s+','',item.strip());mcode=re.fullmatch(r'(\d+)([A-Z]*)(?:-([A-Z]+(?:-[A-Z]+)*))?',item)
            if not mcode:raise ValueError('AHI code notation changed: '+item)
            number,suffix,rest=mcode.groups();suffixes=[suffix]+(rest.split('-')if rest else[])
            for end in suffixes:
                code=dept+' '+number+end;c=course(code,None,PID+'-degree-policies',DEGREE_URL,institution='ucsd',unit='quarter_hours',category='human_context');records[c['id']]=c
    rows=[req('ahi-pool','American History and Institutions course options','degree-policies',kind='choose_courses',count=1,course_ids=list(records),summary='One listed course or a HIUS course other than a colloquium, at C− or P or better. The open HIUS predicate is source-stated; it does not require enumerating every changing HIUS offering. Other documented non-course routes remain alternatives.')]
    return {'id':PID,'curriculum_status':'partial','courses':list(records.values()),'requirements':rows}
