"""Observe the Case AI BA and BS major tables; university requirements remain reviewed gaps."""
from atlas.adapters.national_curriculum_common import content, clean, require_phrases
from atlas.adapters.degree_table_observations import Tables, reviewed_outcomes
from atlas.adapters.case_degree_courses import classify_observed


def parse_case(html, program_id, award, url):
    root=content(html,'Artificial Intelligence, '+award)
    panel=root.find(id='programrequirementstextcontainer')
    if panel is None:raise ValueError('Program requirements panel missing')
    for sup in panel.find_all('sup'):sup.decompose()
    tables=panel.find_all('table',class_='sc_courselist')
    expected=9 if award=='BS' else 4
    if len(tables)!=expected:raise ValueError('Reviewed requirement table structure changed')
    sid=program_id+'-catalog';t=Tables('case-'+award.lower(),sid,url)
    if award=='BA':
        require_phrases(panel,['Choose three of the following','Choose one 3-4 credit course, or two 1.5 credit courses'])
        for i,title in enumerate(['Required courses','Societal impact course','Technical electives']):t.table(tables[i],title)
        ids=[cid for row in tables[3].find_all('tr') if (p:=t.row(row)) for cid in p['ids']]
        t.group('Application elective',kind='note',ids=ids,summary='Choose one listed course carrying 3–4 credits, or two listed courses carrying 1.5 credits each. Individual credits are not supplied in this pool; the two selection routes must not be conflated.')
    else:
        require_phrases(panel,['Four technical electives are required','at most two courses from Group 2','Courses may not be double counted','prior permission from the department chair','Any AI Breadth course','Any CSDS course'])
        for i,title in enumerate(['Mathematics and engineering','Science course route','AI core','Mathematical foundations','AI breadth','Societal impact','Secure computing']):
            if i==1:
                alt=t.group('Science requirement',kind='alternative')
                t.table(tables[i],title,parent=alt['id'])
                require_phrases(panel,['minor programs: Biology, Chemistry, or Geological Sciences','major programs: Biology, Biochemistry, Chemistry, Geological Sciences, or Neuroscience'])
                t.group('Completed science credential route',parent=alt['id'],kind='note',summary='An earned minor in biology, chemistry or geological sciences, or a major in biology, biochemistry, chemistry, geological sciences or neuroscience, may satisfy the science requirement instead of the listed physics route.')
            else:t.table(tables[i],title)
        pools=[]
        for index in [7,8]:
            ids=[cid for row in tables[index].find_all('tr') if (p:=t.row(row)) for cid in p['ids']]
            pools.append(ids)
        breadth=[cid for row in tables[4].find_all('tr') if (p:=t.row(row)) for cid in p['ids']]
        all_ids=list(dict.fromkeys(breadth+pools[0]+pools[1]))
        elective=t.group('Four technical electives',kind='choose_courses',count=4,ids=all_ids,summary='Choose four technical electives without double counting. At most two may come from Group 2. The displayed inventory is not exhaustive: Group 2 permits any CSDS course; unlisted AI-related courses need prior chair or designee approval.')
        t.group('Group 1 membership',parent=elective['id'],kind='note',ids=list(dict.fromkeys(breadth+pools[0])),summary='Group 1 includes the entire AI breadth pool and these additional listed courses.')
        t.group('Group 2 limit and open pool',parent=elective['id'],kind='note',ids=pools[1],summary='Group 2 includes any CSDS course and these listed courses. No more than two Group 2 courses may count toward the four technical electives; courses cannot be double counted.')
    outcomes=reviewed_outcomes(root,'Learning Outcomes',[
        (['analyze a complex computing problem','identify solutions'],'Analyze computing problems using computing and other relevant disciplines.'),
        (['design, implement, and evaluate','computing requirements'],'Develop and evaluate computing solutions against stated requirements.'),
        (['communicate effectively','professional contexts'],'Communicate effectively in professional settings.'),
        (['professional responsibilities','legal and ethical principles'],'Make professional computing decisions informed by law and ethics.'),
        (['member or leader','team'],'Contribute to and lead teams working in the discipline.'),
        (['theory, techniques, and tools','assumptions','societal benefits and risks',"stakeholders' needs"],'Apply AI methods with awareness of their assumptions, societal impacts and stakeholder needs.')],sid)
    return {'outcomes':outcomes,'id':program_id,'title':'Artificial Intelligence','award_level':award,'program_kind':'degree','courses':classify_observed(list(t.courses.values())),'requirements':t.rules}
