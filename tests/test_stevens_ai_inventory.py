import json
from pathlib import Path
import pytest
from atlas.adapters.stevens_ai_requirements import PID,parse
from atlas.adapters.stevens_ai_general_education import PREFIXES,OPTION_RULES,PROGRESSION,parse_general,parse_ap,parse_english,parse_school,parse_options,parse_progression,parse_graduate_course


def link(code):return '<a data-course-id="example">'+code+'</a>'
def panel(title,body):return '<button aria-controls="'+title+'">'+title+'</button><div id="'+title+'">'+body+'</div>'


def fixture():
    science='<p>two science courses and a science laboratory</p><table><tbody><tr><td>Example route</td><td>'+link('CH 115')+'</td><td>'+link('BIO 181')+'</td><td>'+link('CH 117')+' or '+link('BIO 182')+'</td></tr></tbody></table>'
    math='<p>complete two Math/Science electives. Any 3-credit Physics (PEP), Chemistry (CH), Biology (BIO) or Mathematics (MA) course; required course in the degree program; equivalent to another course counted towards the degree. MA 117. prior approval. following courses may also count</p>'+link('EN 250')
    tech='<p>complete 1 Technical electives from the following list. prior approval</p>'+link('CS 558 / CPE 558')+link('MA 661')
    gen='<p>complete 4 General Electives. Any 3+-credit course offered at Stevens; required course in the degree program; equivalent to another course counted towards the degree. prior approval</p><p>The following courses cannot be counted: '+link('CS 501')+'</p><p>Also, students may not count toward the major both courses: '+link('CS 306')+' and '+link('CS 396')+'</p>'
    success='<p>All students must complete '+link('PRV 101')+'</p><p>Students must complete three courses from '+''.join(link('PRV '+str(n)) for n in [201,202,203,204])+'</p>'
    return '<h1>Bachelor of Science in Artificial Intelligence</h1>'+''.join(panel(*x) for x in [('Math/Science Requirements',science),('Math/Science Electives',math),('Technical Electives',tech),('General Electives',gen),('SUCCESS Curriculum Requirements',success),('Humanities Requirements','<a href="/policy">Humanities Requirements</a>')])


def test_rendered_inventory_preserves_conditional_lab_crosslist_and_open_pools():
    r=parse(fixture());nodes={x['id']:x for x in r['requirements']};courses={x['code']:x for x in r['courses']}
    seq=nodes[PID+'-science-sequence-1'];lab=nodes[PID+'-science-sequence-1-lab']
    assert seq['course_ids']==['stevens-ch-115','stevens-bio-181']
    assert lab['parent_id']==seq['id'] and lab['kind']=='alternative'
    assert lab['course_ids']==['stevens-ch-117','stevens-bio-182']
    assert nodes[PID+'-technical-electives']['count']==1
    assert len(nodes[PID+'-technical-electives']['course_ids'])==2
    assert courses['CS 558 / CPE 558']['name'] is None
    assert nodes[PID+'-math-science-electives']['course_ids']==['stevens-en-250']
    assert nodes[PID+'-general-electives']['course_ids']==[]
    assert 'CS 501' not in courses and 'CS 396' not in courses
    assert not {'curriculum_audit','last_verified'} & r.keys()
    changed=parse(fixture().replace('CS 501','CS 599').replace('complete 1 Technical','complete 2 Technical'))
    assert next(x for x in changed['requirements'] if x['id'].endswith('technical-electives'))['count']==2
    assert 'CS 599' in next(x for x in changed['requirements'] if x['id'].endswith('general-exclusions'))['summary']


def test_unhydrated_missing_choice_and_changed_policy_fail():
    for html,match in [(fixture().replace('>CH 115<','>course<'),'rendering required'),(fixture().replace('Math/Science Electives','Different label'),'panel'),(fixture().replace(' or ',' and ',1),'condition changed'),(fixture().replace('Any 3+-credit','Any 2+-credit'),'condition changed')]:
        with pytest.raises(ValueError,match=match):parse(html)


def ge_fixture():
    rows=''.join('<tr><td>'+prefix+' example</td><td>MA '+str(101+i)+'</td><td>3</td><td>Example topic '+str(i)+'</td></tr>' for i,prefix in enumerate(PREFIXES))
    return '<article><h2>General Education</h2><table>'+rows+'</table><p>Total Credit Hours: 29-32. Clark Scholars can use CLK 183 to substitute for PRV 101; incoming international undergraduate students HASS 101, HASS 103 and HASS 105.</p></article>'


def test_ge_reads_columns_preserves_examples_and_rejects_misalignment():
    result=parse_general(ge_fixture());assert len(result['requirements'])==9
    assert result['courses'][0]['name']=='Example topic 0'
    assert result['courses'][0]['credits']==3
    assert all(n['kind']=='note' for n in result['requirements'])
    with pytest.raises(ValueError,match='align'):parse_general(ge_fixture().replace('>3</td>','>3 4</td>',1))
    with pytest.raises(ValueError,match='category'):parse_general(ge_fixture().replace('First-Year Experience','Changed',1))


def test_ap_conditional_same_exam_multiple_schools_not_duplicate():
    html='<article><h2>Advanced Placement</h2><p>maximum of 30 credits; International Baccalaureate; Cambridge A-Level; transfer credits; directly from high school; not previously enrolled as matriculated students</p><table><tr><td>Example Exam (4,5)</td><td>SES: MA 121</td><td>2</td></tr><tr><td>Example Exam (4,5)</td><td>SB: MA 111</td><td>3</td></tr></table><p>QF majors receive transfer credit for ECON 242 with both AP Macroeconomics and AP Microeconomics</p></article>'
    r=parse_ap(html);assert len(r['requirements'])==4
    assert [n['credits'] for n in r['requirements'][1:3]]==[2,3]
    assert all(n['kind']=='note' for n in r['requirements'])
    with pytest.raises(ValueError,match='Duplicate'):parse_ap(html.replace('SB: MA 111','SES: MA 121'))
    with pytest.raises(ValueError,match='condition changed'):parse_ap(html.replace('30 credits','40 credits'))


@pytest.mark.parametrize('tab',list(PROGRESSION))
def test_progression_changes_fail_before_stale_observation(tab):
    title,_,phrases,_=PROGRESSION[tab]
    html='<article><h2>'+title+'</h2><p>'+'; '.join(phrases)+'</p></article>'
    assert len(parse_progression(html,tab)['requirements'])==1
    with pytest.raises(ValueError,match='condition changed'):parse_progression(html.replace(phrases[0],'changed'),tab)


def test_graduate_school_scope_is_courses_not_student_home():
    html='<article><h2>Course Options</h2>'+''.join('<p>'+phrase+'</p>' for _,_,phrases,_ in OPTION_RULES for phrase in phrases)+'</article>'
    r=parse_options(html)
    assert 'course’s school' in r['requirements'][0]['summary']
    with pytest.raises(ValueError,match='condition changed'):parse_options(html.replace('600-level or higher SES or SSB course','600-level course for SES or SSB students'))
    c='<h1>MA 661</h1><h2>Download as PDF</h2><h2>Example Title</h2><p>Engineering and Science; dynamic programming; statistical learning</p><h3>Credits</h3><div>4</div>'
    r=parse_graduate_course(c,'MA 661');assert r['courses'][0]['name']=='Example Title' and r['courses'][0]['credits']==4
    with pytest.raises(ValueError,match='condition changed'):parse_graduate_course(c.replace('Engineering and Science','Computing'),'MA 661')


def test_seed_structured_inventory_and_actual_remaining_applicability():
    d=json.loads(Path('data/programs/'+PID+'.json').read_text());nodes={r['id']:r for r in d['requirements']}
    assert len([k for k in nodes if k.startswith(PID+'-science-sequence-') and not k.endswith('-lab')])==6
    assert nodes[PID+'-technical-electives']['count']==6 and len(nodes[PID+'-technical-electives']['course_ids'])==11
    assert len([k for k in nodes if '-ap-row-' in k])==41
    assert nodes[PID+'-success-choice']['count']==3
    assert len(nodes[PID+'-success-choice']['course_ids'])==5
    assert d['curriculum_status']=='partial'
    assert any('AP Calculus' in x for x in d['curriculum_audit']['unresolved_requirements'])


def test_school_scope_and_international_route_require_explicit_evidence():
    html='<article><h2>Undergraduate Programs</h2><p>All undergraduate students must complete General Education credits; required Humanities courses and the SUCCESS Core. School of Computing offers</p><a href="/programs/qT6Ld1CzBAhQsVKYFNVv">AI degree</a></article>'
    assert len(parse_school(html)['requirements'])==1
    with pytest.raises(ValueError,match='AI degree'):parse_school(html.replace('qT6Ld1CzBAhQsVKYFNVv','other'))
    html='<article><h2>English Language Requirement for International Students</h2><p>international students will be placed in HASS 101 during their first semester. After successful completion of HASS 101 take HASS 103, followed by HASS 105. A diagnostic in the first week may transfer to HASS 103. HASS 101 counts as general or free elective. Take remaining humanities courses required for their degree program.</p></article>'
    assert parse_english(html)['courses'][0]['credits'] is None
    with pytest.raises(ValueError,match='condition changed'):parse_english(html.replace('general or free elective','no elective'))
