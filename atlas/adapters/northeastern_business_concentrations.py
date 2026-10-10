"""Observe the finite concentration choices linked by Northeastern's AI/Business BS.

A source observation is a conditional concentration subtree, not a separate AI award.
The degree's own list controls eligibility; school navigation is never used as a pool.
"""
from copy import deepcopy
from functools import partial
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from atlas.adapters.northeastern_courseleaf import clean, slug, parse_catalog

PID = 'northeastern-university-artificial-intelligence-and-business-administration-bs-boston-bs-degree'
BASE = 'https://catalog.northeastern.edu/undergraduate/business/concentrations/'
PROFILES = {
    'Accounting': 'accounting',
    'Accounting and Advisory Services': 'accounting-advisory-services/index.html',
    'Brand Management': 'brand-management/',
    'Corporate Innovation': 'corporate-innovation/',
    'Entrepreneurial Startups': 'entrepreneurial-startups/',
    'Finance': 'finance',
    'Fintech': 'fintech/',
    'Healthcare Management and Consulting': 'healthcare-management-consulting/',
    'International Business': 'international-business/',
    'Management': 'management',
    'Marketing': 'marketing',
    'Marketing Analytics': 'marketing-analytics/',
    'Social Innovation and Entrepreneurship': 'social-innovation-entrepreneurship/',
    'Supply Chain Management': 'supply-chain-management',
}


def node(key, title, source_id, *, parent=None, kind='note', summary='', count=None, course_ids=None):
    return dict(id=PID+'-req-'+key, parent_id=parent, title=title, kind=kind,
                count=count, credits=None, credit_unit='semester_hours', category='applications',
                source_id=source_id, source_text=None, summary=summary, course_ids=course_ids or [])


def selection_rules(html):
    """Observe required-versus-second-only options and degree-specific conditions."""
    soup=BeautifulSoup(html,'html.parser')
    container=soup.find(id='site-title')
    heading=container.find('h1') if container else None
    if not heading or clean(heading)!='Artificial Intelligence and Business Administration, BS (Boston)':
        raise ValueError('Expected AI/Business degree identity')
    panel=soup.find(id='programrequirementstextcontainer')
    heading=next((h for h in panel.find_all('h2') if clean(h)=='Business Concentration'),None) if panel else None
    if not heading: raise ValueError('Business Concentration section missing')
    parts=[]; links={}
    for sibling in heading.next_siblings:
        if getattr(sibling,'name',None)=='h2': break
        if not getattr(sibling,'find_all',None): continue
        parts.append(clean(sibling))
        for a in sibling.find_all('a',href=True):
            links[clean(a)]=urljoin(BASE,a['href'].strip())
    body=' '.join(parts)
    if links!={title:BASE+path for title,path in PROFILES.items()}:
        raise ValueError('Degree concentration eligibility list changed')
    if 'Complete at least one business concentration' not in body:
        raise ValueError('Concentration selection minimum changed')
    if 'International Business (available only as a second concentration)' not in body:
        raise ValueError('International Business second-only condition changed')
    if 'If the Marketing Analytics concentration is selected, an additional general elective is required.' not in body:
        raise ValueError('Marketing Analytics general-elective condition changed')
    sid=PID+'-catalog'; parent=PID+'-req-business-concentration'
    return [node('business-concentration-options','Required business concentration options',sid,parent=parent,kind='alternative',
                 summary='Complete at least one of these 13 eligible concentrations. Additional concentrations are possible; International Business is available only as a second concentration. Courses in unselected concentrations are not required.'),
            node('business-concentration-second-only','Optional second concentration: International Business',sid,parent=parent,
                 summary='International Business may be selected only as a second concentration, after another eligible business concentration. The nested requirements apply only if selected.')]


def parse_concentration(html, *, title):
    namespace=PID+'-concentration-'+slug(title)
    url=BASE+PROFILES[title]
    result=parse_catalog(html,program_id=namespace,title=title,url=url,
        required_sections=['Concentration in '+title],pooled_subheaders=('Electives',),
        requirement_scope='business_concentration')
    if not result['catalog_year']: raise ValueError('Concentration catalog edition missing')
    sid=namespace+'-catalog'
    remap={c['id']:PID+'-'+slug(c['code']) for c in result['courses']}
    for c in result['courses']:c['id']=remap[c['id']]
    for r in result['requirements']:
        r['course_ids']=[remap[cid] for cid in r['course_ids']]
        r['category']='applications'
    root=result['requirements'][0]
    root['title']=title+' concentration (if selected)'
    root['summary']='Conditional concentration requirements linked by the AI/Business degree. Northeastern undergraduate catalog Hours are semester hours; overlap and approval conditions remain controlling.'
    if title=='International Business':
        _international_paths(result,namespace,sid)
    if title in {'Corporate Innovation','Entrepreneurial Startups','Social Innovation and Entrepreneurship'}:
        panel=BeautifulSoup(html,'html.parser').find(id='concentrationrequirementstextcontainer')
        subgroup=next((r for r in result['requirements'] if r['title']=='Additional Electives'),None)
        if not subgroup: raise ValueError('Additional elective subgroup missing')
        choice=next(r for r in result['requirements'] if r['id']==subgroup['parent_id'])
        if 'one of which may come from the additional' not in choice['summary'].lower() or 'One course from an approved Dialogue may count toward the additional elective.' not in clean(panel):
            raise ValueError('Additional elective maximum or approval policy changed')
        active=False; codes=[]
        for tr in panel.find_all('tr'):
            if 'Additional Electives'==clean(tr):active=True;continue
            if active and 'areaheader' in tr.get('class',[]):break
            if active:
                codes.extend(clean(a) for td in tr.find_all('td',class_='codecol') for a in td.find_all('a',class_='code'))
        if not codes: raise ValueError('Additional elective pool missing')
        subgroup['course_ids']=[PID+'-'+slug(code) for code in codes]
        subgroup['summary']=f"At most one of the {choice['count']} elective selections may come from this additional pool. An approved Dialogue course may replace that additional elective; individual approval is required."
    return {'id':PID,'catalog_year':result['catalog_year'],'curriculum_status':'partial',
            'courses':result['courses'],'requirements':result['requirements']}


def _international_paths(result,namespace,sid):
    """One/both intermediate courses changes the number of elective courses."""
    rows=result['requirements']; prefix=namespace+'-req-'
    core=next((r for r in rows if r['kind']=='choose_courses' and 'one or both' in r['summary']),None)
    electives=next((r for r in rows if r['kind']=='choose_courses' and 'one if both courses above selected' in r['summary']),None)
    if not core or not electives or core['count']!=1 or electives['count']!=2:
        raise ValueError('International Business conditional counts changed')
    children=lambda rid:[r for r in rows if r['parent_id']==rid]
    core_children=children(core['id'])
    if sorted(c for r in core_children for c in r['course_ids'])!=[PID+'-intb-2501',PID+'-intb-3310']:
        raise ValueError('International Business intermediate-course pool changed')
    # The alternative replaces only the two linked selections, leaving required INTB 1203/1209 intact.
    choice=node('international-business-paths','International Business course distribution',sid,
        parent=core['parent_id'],kind='alternative',summary='Choose either one intermediate course plus two electives, or both intermediate courses plus one elective.')
    removed={core['id'],electives['id']}
    def descendants(rid):
        found=[]
        for child in children(rid):found.append(child);found.extend(descendants(child['id']))
        return found
    core_rows=descendants(core['id']); elective_rows=descendants(electives['id'])
    removed.update(r['id'] for r in core_rows+elective_rows)
    result['requirements']=[r for r in rows if r['id'] not in removed]+[choice]
    for number,core_count,elective_count in [(1,1,2),(2,2,1)]:
        path=node('international-business-path-'+str(number),f'Path {number}: {core_count} intermediate and {elective_count} elective courses',sid,parent=choice['id'],kind='all')
        result['requirements'].append(path)
        for source,children_rows,count in [(core,core_rows,core_count),(electives,elective_rows,elective_count)]:
            originals=[source]+children_rows
            mapping={r['id']:r['id']+'-path-'+str(number) for r in originals}
            for original in originals:
                r=deepcopy(original);r['id']=mapping[original['id']]
                r['parent_id']=path['id'] if original is source else mapping[original['parent_id']]
                if original is source:
                    r['count']=count;r['credits']=None
                    r['summary']=f'Choose {count} courses from this pool in this path; approved exceptions and overlap limits remain applicable.'
                result['requirements'].append(r)


SOURCE_PARSERS={BASE+path:partial(parse_concentration,title=title) for title,path in PROFILES.items()}


def enrich_degree_observation(observed,html):
    rules=selection_rules(html)
    for r in observed['requirements']:
        if 'individual concentration curricula remain unexpanded' in r['summary']:
            r['summary']='The degree links the finite concentration options below; their current requirements are observed independently from each linked concentration page.'
    observed['requirements'].extend(rules)
    return observed
