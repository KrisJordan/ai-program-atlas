"""Guarded extraction of Miami's dated public Tableau PDF Master List.

PDFs must be obtained through the ordinary public export controls. PyMuPDF is an
optional local extraction dependency, not required by Atlas builds or refreshes.
No network requests are made. Parsed pool coverage is not a degree audit.
"""
import bisect
import re
import unicodedata
from collections import Counter

TITLE='Courses Eligible to be Used in Individualized Cognates'
DATE='Updated 10/2/2026'
AREAS={'Arts & Humanities','People & Society','STEM'}
HEADERS=['Subject','Course No.','Course Title','Area of Knowledge','Typically Offered','Course ID']


def clean(value):
    return ' '.join(unicodedata.normalize('NFKC', value).split())


def extract_master_pdf(path):
    import pymupdf
    document=pymupdf.open(path)
    pages=[]
    left_master=False
    for number,page in enumerate(document,1):
        text=clean(page.get_text())
        if TITLE not in text:
            left_master=True
            continue
        if left_master:raise ValueError('Master List pages are not contiguous')
        if DATE not in text:raise ValueError('Master List update label changed')
        words=page.get_text('words')
        subject_headers=[w for w in words if w[4]=='Subject']
        if len(subject_headers)!=1:raise ValueError('Subject column header missing/duplicated')
        y=subject_headers[0][1]
        header_words=sorted([w for w in words if abs(w[1]-y)<0.6],key=lambda w:w[0])
        groups={}
        for w in header_words:groups.setdefault((w[5],w[6]),[]).append(w)
        headers=[(min(w[0] for w in ws),clean(' '.join(w[4] for w in ws))) for ws in groups.values()]
        headers.sort()
        if [h[1] for h in headers]!=HEADERS:raise ValueError('PDF table columns changed')
        starts=[h[0] for h in headers]
        data=[w for w in words if w[1]>y+5 and w[0]>=starts[0]-1]
        ids=[w for w in data if w[0]>=starts[-1]-1 and re.fullmatch(r'\d{6}',w[4])]
        if not ids:raise ValueError('Empty Master List page')
        ids=sorted(ids,key=lambda w:w[1])
        row_cells=[[[] for _ in HEADERS] for _ in ids]
        for w in data:
            closest=min(range(len(ids)),key=lambda i:abs(ids[i][1]-w[1]))
            if abs(ids[closest][1]-w[1])>6.1:
                raise ValueError(f'Unaccounted PDF word on page {number}: {w[4]}')
            column=bisect.bisect_right(starts,w[0]+1)-1
            if not 0<=column<6:raise ValueError('Word outside reviewed table columns')
            row_cells[closest][column].append(w)
        rows=[[clean(' '.join(w[4] for w in sorted(ws,key=lambda w:(round(w[1],1),w[0]))))
               for ws in cells] for cells in row_cells]
        pages.append(dict(page=number,title=TITLE,updated='2026-10-02',headers=HEADERS,rows=rows))
    if len(pages)!=50 or len(document)!=112:
        raise ValueError('Reviewed export page accounting changed; inspect new export')
    return pages


def parse_master_pages(pages):
    records={};code_identity={};accounting=[];memberships=set();physical_rows=0
    pending=None

    def save():
        if pending is None:return
        code,identity=pending['code'],pending['identity']
        title=clean(' '.join(pending['titles']))
        key=(code,identity)
        if code in code_identity and code_identity[code]!=identity:
            raise ValueError('One code has multiple source identities; review required')
        code_identity[code]=identity
        r=records.setdefault(key,dict(code=code,source_course_id=identity,
            name=None if '..' in title or '…' in title else title,
            display_title=title,areas=[],pages=[],row_locators=[],typically_offered=[]))
        if r['display_title']!=title:raise ValueError('Repeated identity has conflicting title: '+code+' '+repr((r['display_title'],title)))
        for area,offered,page,row in pending['rows']:
            if area not in r['areas']:r['areas'].append(area)
            if page not in r['pages']:r['pages'].append(page)
            r['row_locators'].append(dict(page=page,row=row,area=area))
            if offered not in r['typically_offered']:r['typically_offered'].append(offered)

    subject=None
    for expected,page in enumerate(pages,1):
        if page['page']!=expected or page['title']!=TITLE or page['updated']!='2026-10-02' or page['headers']!=HEADERS:
            raise ValueError('Master List page sequence/identity/schema changed')
        page_new=page_repeated=0
        if not page['rows']:raise ValueError('Empty Master List page')
        for row_number,cells in enumerate(page['rows'],1):
            if len(cells)!=6:raise ValueError('Malformed row width')
            sub,num,name,area,offered,identity=map(clean,cells)
            if sub:
                if not re.fullmatch('[A-Z]{2,5}',sub):raise ValueError('Unreviewed subject code')
                subject=sub
            if num:
                if not re.fullmatch(r'(?:\d{3}[A-Z]?|[A-Z]{2,4})',num):raise ValueError('Unreviewed course-number format')
                if not subject or not name:raise ValueError('New course missing subject/title')
                save()
                pending=dict(code=subject+' '+num,identity=identity,titles=[name],rows=[])
            elif pending is None or pending['identity']!=identity:
                raise ValueError('Continuation without the same course identity')
            elif name:
                pending['titles'].append(name) # A wrapped title in a spanning cell.
            if area not in AREAS or not offered or not re.fullmatch(r'\d{6}',identity):
                raise ValueError('Incomplete identity, area or context row')
            pending['rows'].append((area,offered,page['page'],row_number))
            membership=(pending['code'],identity,area)
            if membership in memberships:page_repeated+=1
            else:page_new+=1;memberships.add(membership)
            physical_rows+=1
        accounting.append(dict(page=page['page'],physical_rows=len(page['rows']),new_area_memberships=page_new,repeated_area_memberships=page_repeated))
    save()
    if not records:raise ValueError('Empty Master List')
    rows=list(records.values())
    return dict(rows=rows,page_accounting=accounting,counts=dict(pages=len(pages),
        physical_rows=physical_rows,course_identities=len(rows),area_memberships=len(memberships),
        repeated_area_memberships=physical_rows-len(memberships),
        truncated_names=sum(r['name'] is None for r in rows),
        by_area=dict(Counter(a for r in rows for a in r['areas']))))


def full_individualized_observation(result, *, pid):
    """Attach applicable AH/PS snapshot candidates, preserving conditional use."""
    from atlas.adapters.national_curriculum_common import course,rule
    from atlas.adapters.miami_cognate_pools import DIRECTORY,SID
    counts=result['counts'];rows=result['rows']
    if counts['pages']!=50 or len(result['page_accounting'])!=50:
        raise ValueError('Full snapshot observation requires all 50 Master List pages')
    if sum(p['physical_rows'] for p in result['page_accounting'])!=counts['physical_rows']:
        raise ValueError('Unreconciled page/row accounting')
    if sum(len(r['areas']) for r in rows)!=counts['area_memberships'] or len(rows)!=counts['course_identities']:
        raise ValueError('Unreconciled identity/membership accounting')
    root=pid+'-cognate-directory-sample' # Stable ID retained from initial capture.
    requirements=[rule(root,'Individualized cognates: full dated Master List evidence',SID,
        parent=pid+'-supplement-individualized-overlap',kind='note',summary=
        f"All 50 Master List pages of the public export updated October 2, 2026 are captured: {counts['course_identities']} unique course identities and {counts['area_memberships']} area memberships. Arts & Humanities and People & Society candidates are attached; this AI major already supplies STEM. An individualized cognate needs at least three courses/nine credits in one area and the current CaneLink attribute. No selected course may satisfy another degree requirement, including quantitative proficiency; one course cannot satisfy two area cognates. Transfer-equivalency codes require accepted applicable transfer/test credit and are not guaranteed Miami offerings. This dated pool does not certify enrollment eligibility, current availability, or a student's degree completion. Credits and prerequisites are unknown in this directory.")]
    courses={}
    for area,key in [('Arts & Humanities','ah'),('People & Society','ps')]:
        selected=[r for r in rows if area in r['areas']]
        ids=[]
        for r in selected:
            c=course(pid,r['code'],r['name'],SID,DIRECTORY,unit='unknown',category='human_context')
            courses[c['id']]=c;ids.append(c['id'])
        requirements.append(rule(root+'-'+key,area+' — dated attribute pool',SID,ids,
            parent=root,kind='note',category='human_context',summary=
            f"{len(selected)} identities in the October 2, 2026 Master List carry this attribute. Multiple area memberships do not duplicate a course or permit double-counting. Current CaneLink designation and individualized no-other-degree-requirement restrictions still apply. Source titles clipped with ellipses remain unknown; generic topics and transfer codes are not blanket approvals of every section or external course."))
    from atlas.adapters.miami_limited_identity_reviews import apply_observed_categories
    return apply_observed_categories(dict(id=pid,courses=list(courses.values()),requirements=requirements))
