"""Current Muir theme lists; literal conditions preserve bundles and source typos."""
import re
from atlas.adapters.cmu_bs.common import slug, text
from atlas.adapters.ucsd_degree_policies import PID, guarded
from atlas.adapters.ucsd_revelle_pools import section, normal
from atlas.adapters.cmu_bs.common import course, requirement
URL='https://muir.ucsd.edu/academics/ge-information/ge-themes.html'
POLICY_URL='https://muir.ucsd.edu/academics/degree.html'


def node(key,title,policy=False,**kw):
    return requirement(PID,'muir-'+key,title,PID+('-muir-policy'if policy else'-muir-themes'),unit='quarter_hours',category='human_context',**kw)


def parse(html):
    s=section(html,'Approved Muir College General Education Courses');v=text(s)
    guarded(v,['two different areas','3 courses in a single language','placement exam or proficiency exam', 'such exceptions are not guaranteed','duplicates credits','grade of D or higher'])
    expected=['Muir College Writing Program','Math or Natural Sciences','Social Sciences','Fine Arts','Humanities','Language Other Than English']
    if [text(h)for h in s.find_all('h2')]!=expected:raise ValueError('Muir area boundaries changed')
    rows=[node('structure','Muir first-year GE structure',kind='note',summary='Conditional Muir route: writing sequence; three courses in one math/natural-science theme; three in one social-science theme; and three courses in each of two distinct areas chosen from fine arts, humanities and a single language. Each nonlanguage area uses one approved theme. Themes and areas below are alternatives, not all additional requirements. Nonwriting GE permits D or better or P. Prior AP/IB/transfer credit cannot be duplicated; enrollment prerequisites still apply; off-list petitions are possible but not guaranteed. Language needs college credit, not placement/proficiency exemption.')];courses={}
    for h in s.find_all('h3'):
        theme=text(h);area=text(h.find_previous('h2'));value=h.find_next_sibling('p')
        if value is None:raise ValueError('Missing theme course paragraph')
        root=node('theme-'+slug(theme),theme,kind='choose_courses',count=3,summary='Choose three approved options only if this theme is selected in '+area+'. Preserve combinations and alternatives printed in each option row.');rows.append(root)
        for i,raw in enumerate(text(value).split(',')):
            raw=raw.strip();ids=[];code=normal(re.sub(r'\s*-\s*','-',raw))
            # Only unambiguous whole single-code tokens become course records.
            # Composite AND/OR grammar and malformed codes remain literal options.
            if code:
                c=course(code,None,PID+'-muir-themes',URL,institution='ucsd',unit='quarter_hours',category='human_context');courses[c['id']]=c;ids=[c['id']]
            rows.append(node('theme-'+slug(theme)+'-'+str(i),raw,kind='note',parent=root['id'],course_ids=ids,summary='Published option: '+raw+'.'+(' Composite, qualified or malformed notation is preserved as one option; no independent-course interpretation is inferred.'if not ids else'')))
    writing=s.find('ol')
    if not writing:raise ValueError('Writing alternatives missing')
    for i,li in enumerate(writing.find_all('li',recursive=False),1):
        raw=text(li);codes=re.findall(r'MCWP-\d+[A-Z]*',raw);ids=[]
        for value in codes:
            code=normal(value);c=course(code,None,PID+'-muir-themes',URL,institution='ucsd',unit='quarter_hours',category='human_context');courses[c['id']]=c;ids.append(c['id'])
        if not ids:raise ValueError('Writing course choices missing')
        rows.append(node('writing-'+str(i),'Muir writing sequence step '+str(i),kind='choose_courses',count=1,course_ids=ids,summary='Choose one listed variant at this sequence step; letter grade D or better.'))
    return dict(id=PID,curriculum_status='partial',courses=list(courses.values()),requirements=rows)


def parse_policy(html):
    s=section(html,'Academic Requirements');v=text(s)
    guarded(v,['maximum of 3 courses from your major','MCWP 125 or MCWP 125R','remaining 1-2 requirements','through your 3rd quarter','through your 6th quarter','Courses must be taken in order','not cleared by AP, IB, or community college credits'])
    return dict(id=PID,curriculum_status='partial',requirements=[
        node('overlap','Muir GE overlap and writing sequence',True,kind='note',summary='At most three major courses may count toward Muir GE in total. Complete writing in order at D or better with letter grading; AP/IB/community-college credit does not clear it. First-pass enrollment priority lasts through quarter six for the two-course writing route. Other GE allows D/P and applicable AP/IB/transfer credit.'),
        node('transfer','Muir transfer-certification branches',True,kind='note',summary='IGETC or CalGETC transfers take MCWP 125 or 125R at letter grade D or better, with first-pass priority through quarter three. Partial IGETC also requires the remaining one or two certified areas. Transfers who completed another campus’s GE take the two-course Muir writing sequence but may petition prior writing for partial/full fulfillment. Other transfers follow first-year requirements, with transcript review. The catalog’s possible MCWP 50 substitution is not repeated by this current page; no automatic substitution is assumed.')])
