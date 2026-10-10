"""Northwestern AI major observations with domain choices and open elective pools."""
from atlas.adapters.national_curriculum_common import content,clean,require_phrases
from atlas.adapters.degree_table_observations import Tables


def parse_northwestern(html,pid,url):
    root=content(html,'Artificial Intelligence Major, BS in Engineering')
    for sup in root.find_all('sup'):sup.decompose()
    require_phrases(root,['Requirements (48 units)','Core Courses (26 units)','Major Program (22 units)','4 advanced elective courses','Any 300-level or higher class','one course in five of the six categories','seven technical electives','Any 300- or 400-level COMP_SCI course','7 social sciences/humanities courses','5 unrestricted electives'])
    tables=root.find_all('table',class_='sc_courselist')
    if len(tables)!=10:raise ValueError('Northwestern major table structure changed')
    t=Tables('nw-bse',pid+'-catalog',url,unit='units')
    t.table(tables[0],'Listed mathematics and physics core')
    require_phrases(root,['PHYSICS 125-1','PHYSICS 140-1','GEN_ENG 212-0'])
    physics=next(r for r in t.rules if r['course_ids']==['nw-bse-physics-135-1'])
    physics.update(kind='note',summary='PHYSICS 135-1 may be replaced by PHYSICS 125-1, PHYSICS 140-1 or GEN_ENG 212-0. These substitute courses still need individual metadata records.')
    t.group('Remaining 26-unit core categories',kind='note',summary='The core includes four mathematics courses, four basic-science units, three engineering foundations courses, three design/communications/innovation courses, seven social sciences/humanities courses and five unrestricted electives. Three additional science units and the school-wide approved pools remain to be expanded.')
    t.table(tables[1],'Five required major course slots')
    t.group('Four advanced electives',kind='note',summary='Choose four advanced electives. Any course at level 300 or above is eligible, along with the introductory supporting courses explicitly listed in the catalog. The introductory exceptions are not yet fully mapped; this open pool must not be interpreted as a finite inventory.')
    breadth=t.group('Five of six breadth domains',kind='choose_courses',count=5,summary='Select five distinct domains and complete one listed course in each selected domain.')
    names=['Advanced ML/NLP','Theoretical Foundations','Symbolic AI','Software and Systems Engineering for AI','Systems that Interact with Humans','Systems that Navigate the World']
    for table,name in zip(tables[2:8],names):t.table(table,name,parent=breadth['id'],kind='alternative',interpret_choices=False)
    t.table(tables[8],'Societal impact: choose one',kind='alternative',interpret_choices=False)
    t.table(tables[9],'Seven technical electives: displayed additional pool',kind='choose_courses',count=7,interpret_choices=False)
    t.group('Open technical elective eligibility',kind='note',summary='Any 300- or 400-level COMP_SCI course may also satisfy a technical-elective slot. The displayed additional pool does not enumerate this open departmental category.')
    t.group('Degree-wide requirements remain applicable',kind='note',summary='The 48-unit degree consists of a 26-unit core and a 22-unit major. Students must also meet the Undergraduate Registration Requirement and home-school degree requirements. Full school and university policy mapping remains pending.')
    return dict(id=pid,title='Artificial Intelligence Major, BS in Engineering',award_level='BSE',program_kind='degree',courses=list(t.courses.values()),requirements=t.rules)
