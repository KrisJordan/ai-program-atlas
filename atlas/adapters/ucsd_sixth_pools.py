"""Sixth's dated GE sheet and current transfer/experiential policies."""
import re
from atlas.adapters.cmu_bs.common import course, slug, text
from atlas.adapters.ucsd_college_context import requirement
from atlas.adapters.ucsd_degree_policies import PID, guarded
from atlas.adapters.ucsd_revelle_pools import normal, section
PDF_URL='https://sixth.ucsd.edu/academics/requirements/GERequirements.pdf'
TRANSFER_URL='https://sixth.ucsd.edu/academics/requirements/transfer-requirements.html'
SECTIONS=[('Information Technology Fluency','Social Analysis',1,4),('Social Analysis','Narrative, Aesthetic, and Historical Reasoning',2,8),('Narrative, Aesthetic, and Historical Reasoning','Analytic Methodologies/Scientific Method',2,8),('Analytic Methodologies/Scientific Method','Structured Reasoning',2,8),('Structured Reasoning','Exploring Data',1,4),('Exploring Data','Art Making',1,4),('Art Making','Upper Division Requirements',None,8)]


def node(key,title,source='ge-pdf',**kw):
    return requirement(PID,'sixth-'+key,title,PID+'-sixth-'+source,unit='quarter_hours',category='human_context',**kw)


def parse_pdf_text(value):
    """Parse text extracted from a visually reviewed PDF; never a refresh/audit."""
    v=value.replace('\u200b','');guarded(v,['2026-2027 Academic Year','Updated August 12, 2026','two different academic departments','R versions of courses','8 units'])
    rows=[node('core-policy','Sixth core, overlap and residence',kind='note',summary='First-year CAT 1/2/3 must be completed in order after ELWR; no substitution from other institutions. CAT 1 is four units and CAT 2/3 six each. Major-department courses may overlap breadth; approved R versions count. The sheet calls breadth eleven courses, while Art Making is explicitly eight units rather than exactly two courses.'),node('upper','Sixth upper-division requirements',kind='note',summary='Complete four upper-division experiential-learning units and four units in CAT 125 or 125R. Some experiential options require a proposal in the preceding quarter; current track-specific rules must also be met.')];courses={}
    for title,end,count,units in SECTIONS:
        start=v.find(title+' (');stop=v.find(end, start+len(title))
        if start<0 or stop<0:raise ValueError('Sixth PDF category boundary changed')
        block=v[start:stop];lines=block.splitlines();matches=[i for i,line in enumerate(lines)if re.match(r'^[A-Za-z &,]+:',line.strip())]
        if not matches:raise ValueError('Sixth department rows missing')
        root=node('pool-'+slug(title),title,kind='choose_credits'if count is None else'choose_courses',count=count,credits=units,summary='Conditional Sixth breadth category. Social Analysis requires two different departments. Art Making uses an eight-unit total, not an inferred fixed two-course count.');rows.append(root)
        for j,i in enumerate(matches):
            finish=matches[j+1]if j+1<len(matches)else len(lines)
            raw=' '.join(line.strip()for line in lines[i:finish]if line.strip())
            raw=re.sub(r' Sixth College General Education Requirements Continued$','',raw)
            label,expr=raw.split(':',1);ids=[]
            for segment in expr.split('|'):
                m=re.match(r'\s*([A-Z]+)[- ](.*)',segment)
                if not m:continue
                dept,tail=m.groups()
                for item in tail.split(','):
                    code=normal(dept+'-'+item.strip())
                    if code:
                        c=course(code,None,PID+'-sixth-ge-pdf',PDF_URL,institution='ucsd',unit='quarter_hours',category='human_context');courses[c['id']]=c;ids.append(c['id'])
            rows.append(node('option-'+slug(title)+'-'+slug(label),label+' options',kind='note',parent=root['id'],course_ids=ids,summary='Published eligibility expression: '+expr.strip()+'. Ranges, paired lectures/labs and open language/literature predicates remain literal; isolated codes do not cancel their surrounding qualifications.'))
    rows.append(node('ap-routes','Sixth published AP breadth alternatives',kind='note',summary='IT: AP Computer Science A 4/5. Social Analysis: Economics, Government or Psychology 4/5. Humanities: African American Studies, Art History, History, non-English Language/Literature 3/4/5. Science: Biology, Chemistry or Physics 1/2/C 3/4/5, or Environmental Science 4/5. Math: Calculus AB/BC 3/4/5. Statistics: Statistics 3/4/5. Art Making: Art Studio or Music 3/4/5. “Can be used towards” an area is not assumed to satisfy its entire multi-course/unit requirement.'))
    return dict(id=PID,curriculum_status='partial',courses=list(courses.values()),requirements=rows)


def parse_transfer(html):
    s=section(html,'General Education Requirements for Transfer Students');v=text(s)
    guarded(v,['Full IGETC or full Cal-GETC','missing only 1 or 2 IGETC courses','UC or 4-Year Reciprocity','reciprocity letter','evaluate your transfer courses individually','Experiential Learning and CAT-125'])
    return dict(id=PID,curriculum_status='partial',requirements=[node('transfer','Sixth transfer-certification branches','transfer',kind='note',summary='Full IGETC/CalGETC or certified UC/four-year reciprocity waives lower-division Sixth GE, but experiential learning and CAT 125 remain, as do major/university requirements. Certification must reach Admissions; a reciprocity letter must reach Sixth advising. Partial IGETC leaves one or two courses determined with advising. Without certification, individual transfer review/petitions establish remaining lower GE; upper-division experiential learning and CAT 125 still apply.')])

ELR_URL='https://docs.google.com/spreadsheets/u/0/d/e/2PACX-1vR7dTRWsk3I2X0t7p5IV-i19gVI3qRDpF5gdK6wA8p3G_H2qyDfkZASfQOEfoYy_-Tib_JlV_pjCjhv/pubhtml/sheet?headers=false&gid=1715831878'
PROPOSAL_URL='https://sixth.ucsd.edu/elr/course-proposal.html'
CAT90_URL='https://sixth.ucsd.edu/elr/cat-90.html'
CAT125_URL='https://sixth.ucsd.edu/cat/courses/cat-125-and-cat-125r.html'
TRACKS={slug(label):label for label in ['Community Engagement','Internship and Apprenticeship','Research and Design','Art and Performance','Global Experience']}
TRACK_BASE='https://sixth.ucsd.edu/elr/fulfillment-tracks/'


def parse_elr_table(html):
    from bs4 import BeautifulSoup
    s=BeautifulSoup(html,'html.parser');v=text(s)
    guarded(v,['Experiential Learning Requirement Approved Course List','at least four units','beginning in Fall 2026','Enrollment Requirements'])
    rows=[node('elr-pool','Sixth automatic experiential options','elr-table',kind='choose_courses',count=1,summary='Choose an eligible approved option for at least four units. All-department 195/197/198/199/GS entries are open course-family predicates; named examples do not restrict those families. The source introduction and current proposal page approve 198/199 from Fall 2026, despite Summer 2026 appearing in their offering cells. Course restrictions require catalog confirmation. CAT 90 is a separately documented exception route.')];courses={};found=0
    for tr in s.find_all('tr'):
        cells=[text(c).replace('\u200b','').strip()for c in tr.find_all('td')]
        if len(cells)!=6 or cells[0]=='Fulfillment Track':continue
        track,dept,raw,name,prereq,quarter=cells
        if not raw or not track:raise ValueError('Incomplete experiential option')
        ids=[];code=normal(raw)
        if code:
            c=course(code,name or None,PID+'-sixth-elr-table',ELR_URL,institution='ucsd',unit='quarter_hours',category='human_context');c['prerequisites']=prereq or None;courses[c['id']]=c;ids=[c['id']]
        rows.append(node('elr-option-'+str(found),raw,'elr-table',parent=rows[0]['id'],kind='note',course_ids=ids,summary='Approved '+track+' option in '+dept+': '+raw+' — '+name+'. Enrollment conditions: '+(prereq or'not stated')+'. Listed offering terms: '+(quarter or'not stated')+'. Offering terms do not override approval effective dates. Composite/paired and all-department options are not expanded into inferred independent alternatives.'));found+=1
    if not found:raise ValueError('No experiential rows')
    return dict(id=PID,curriculum_status='partial',courses=list(courses.values()),requirements=rows)


def parse_track(html,key):
    s=section(html,TRACKS[key]);v=text(s)
    guarded(v,['updated approved course list went into effect in Fall 2024','prior to Fall 2024','at least four units'])
    summary='Current approved list applies from Fall 2024. Earlier entrants may request an exception for a formerly approved course after enrolling; no automatic grandfathering is assumed. Approved courses need at least four units; listed opportunities are not automatically approved. '
    if key=='global-experience':
        guarded(v,['at least four weeks','upon your return']);summary+='Global Seminar courses are automatic; other study abroad of at least four weeks needs a proposal after return and the detailed eligibility criteria.'
    else:
        guarded(v,['CAT-090','Fall quarter offerings only']);summary+='CAT 90 is an alternative only in fall under its separately documented eligibility rules.'
    return dict(id=PID,curriculum_status='partial',requirements=[node('track-'+key,TRACKS[key]+' eligibility','track-'+key,kind='note',summary=summary)])


def parse_proposal(html):
    s=section(html,'Course Proposal');v=text(s)
    guarded(v,['Friday of Week 8 of the quarter after','Friday of Week 8 of the quarter before','As of Fall 2026','All 198 and 199 courses','at least four weeks','a single course cannot be used','any other piece of academic writing'])
    return dict(id=PID,curriculum_status='partial',requirements=[node('proposal-study','Sixth study-abroad proposal criteria','proposal',kind='note',summary='Nonautomatic study-abroad work needs faculty supervision, at least four upper-division UC-transferable units appearing on the UCSD transcript, a passing grade and at least four in-person weeks; virtual exchanges do not qualify. Lower-division-only plans need special consideration. Do not reuse the course for another Sixth GE. Submit the Navigating Reentry activities worksheet and completion certificate by Friday of week eight in the quarter after return; decision by week ten. Proposals must be original student writing; AI-generated submissions are disallowed.'),node('proposal-campus','Sixth off-list UCSD course proposal','proposal',kind='note',summary='Faculty-supervised upper-division work of at least four units must have substantial sustained experiential activity in a fulfillment track, active independent work, reflection and a final deliverable. These criteria are necessary but approval is not guaranteed. Supply the syllabus by Friday of week eight in the preceding quarter; decision by week ten. From Fall 2026, all four-unit 198/199 courses qualify automatically and need no proposal.')])


def parse_cat90(html):
    s=section(html,'CAT-090');v=text(s)
    guarded(v,['one-unit reflection seminar','eighty hours','at least five weeks','no earlier than July 1 and no later than October 1','end of Week 1','must not receive academic credit','regardless of whether you have lower- or upper-division standing','pass/no pass'])
    c=course('CAT 90','Experiential Learning Seminar',PID+'-sixth-cat90',CAT90_URL,institution='ucsd',unit='quarter_hours',credits=1,category='human_context')
    return dict(id=PID,curriculum_status='partial',courses=[c],requirements=[node('cat90','Explicit one-unit experiential alternative','cat90',kind='note',course_ids=[c['id']],summary='Passing fall-only CAT 90 fulfills experiential learning despite the ordinary four-upper-division-unit route. It is one unit, P/NP only, available at either class standing after an approved summer activity of at least 80 hours across five weeks, ending July 1–October 1 and not continuing in fall. No other academic credit for the activity. Obtain preauthorization and eligibility review; submit supervisor confirmation by end of week one. Paid, unpaid and co-curricular-record activities may qualify; failure leaves the requirement incomplete.')])


def parse_cat125(html):
    s=section(html,'CAT-125 and CAT-125R');v=text(s)
    guarded(v,['four units','CAT-125GS','lower-division writing sequence','upper-division standing','only one of these two courses'])
    courses=[course(code,'Public Rhetoric and Practical Communication',PID+'-sixth-cat125',CAT125_URL,institution='ucsd',unit='quarter_hours',credits=4,category='human_context')for code in ['CAT 125','CAT 125R']]
    for c in courses:c['prerequisites']='Completed lower-division writing sequence and upper-division standing.'
    gs=course('CAT 125GS',None,PID+'-sixth-cat125',CAT125_URL,institution='ucsd',unit='quarter_hours',category='human_context');courses.append(gs)
    return dict(id=PID,curriculum_status='partial',courses=courses,requirements=[node('cat125-options','Sixth upper-division writing alternatives','cat125',kind='choose_courses',count=1,course_ids=[c['id']for c in courses],summary='One CAT 125, online CAT 125R, or the explicitly allowed Global Seminar CAT 125GS variant meets writing. CAT 125/125R require completed lower-division writing and upper-division standing. No automatic permission to reuse one GS course for experiential learning and another Sixth GE is inferred.')])
