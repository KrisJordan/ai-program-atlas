"""Synthetic policy changes and scope checks; no seed or cached-source replay."""
import pytest
from atlas.adapters.northeastern_policies import parse_policy,PROFILES
from atlas.requirements import validate_requirements


def page(profile,content):
    _,heading,panel=PROFILES[profile]
    return f'<header id="site-title"><h1>{heading}</h1></header><nav>Unrelated 999 hours</nav><div id="{panel}">{content}</div>'


def parse(profile,content):return parse_policy(page(profile,content),program_id='test-program',profile=profile)


UNIVERSITY='''<p>Individual program requirements may exceed these minima.</p>
<p>Minimum 128 total semester hours required</p><p>Minimum 2.000 GPA required</p>
<p>Students must earn a minimum of 64 Northeastern University semester hours.</p>
<p>Complete the <span>experiential learning </span><span>gra</span><span>dua</span><span>tion requirement</span>.</p>'''


def test_shared_minima_are_observed_and_do_not_create_a_complete_degree():
    result=parse('universitywide',UNIVERSITY);validate_requirements(result)
    assert len(result['requirements'])==5 and result['courses']==[]
    assert result['curriculum_status']=='partial' and 'curriculum_audit' not in result and 'last_verified' not in result
    credit=next(r for r in result['requirements'] if r['title']=='University minimum degree credits')
    assert credit['credits']==128 and credit['kind']=='note'
    changed=parse('universitywide',UNIVERSITY.replace('128','132').replace('2.000','2.250').replace('64','72'))
    assert next(r for r in changed['requirements'] if r['title']==credit['title'])['credits']==132
    assert any('2.250' in r['summary'] for r in changed['requirements'])
    assert next(r for r in changed['requirements'] if r['title']=='Northeastern-earned credit minimum')['credits']==72


@pytest.mark.parametrize('bad',[
    page('universitywide',UNIVERSITY).replace('Universitywide Requirements','Wrong Policy'),
    page('universitywide','')+'<aside>'+UNIVERSITY+'</aside>',
    page('universitywide',UNIVERSITY.replace('experiential learning ','different ')),
    page('universitywide',UNIVERSITY.replace('semester hours','quarter hours')),
])
def test_wrong_source_or_changed_policy_semantics_fails(bad):
    with pytest.raises(ValueError):parse_policy(bad,program_id='test-program',profile='universitywide')


NUPATH='''<p>NUpath is competency based rather than course based. NUpath courses may not be taken pass/fail. NUpath applies to freshmen who entered in fall 2016 and later.</p>
<h2>NUpath Requirements</h2><p>A set of 11 competencies.</p><ul>'''+''.join('<li>'+x+'</li>' for x in ['Natural and Designed World','Creative Expression','Interpreting Culture','Formal Reasoning','Societies','Data','Diversity','Ethics','Writing','Experience','Demonstrating Thought and Action in a Capstone'])+'''</ul>
<p>There are no level restrictions or semester-hour restrictions. No course completed on a satisfactory/unsatisfactory grading basis qualifies. A single course can count for up to two of the following requirements. Up to five of the following eight requirements can be met by transferred credit.</p>
<p>Transfer credits cannot be used to fulfill the capstone or experiential requirements; only the first-year writing requirement can be met by transferred or placement test credits.</p>
<h3>Demonstrating Thought and Action in a Capstone</h3><p>Each student must take at least one course designated as a capstone experience. Students must complete a capstone in their major. For combined or double majors, the units may specify in which major to take the capstone or may leave the choice to the student.</p>
<h3>First-Year Writing Requirement</h3><p>Earn a grade of C or better, or use qualifying advanced placement scores or appropriate transfer credit. The program uses guided self-placement and requires students bring an essay.</p>
<h3>Advanced Writing Requirement</h3><p>Students must satisfy the first-year requirement, have a minimum of 64 semester hours and at least junior or senior standing. Transfer credit cannot be used. Earn C or better.</p>
<h3>Writing-Intensive Courses in the Major</h3><p>Each major includes at least two additional writing-intensive courses.</p>'''


def test_nupath_criteria_do_not_inherit_ba_or_nyc_requirements():
    html=page('nupath',NUPATH)+'<div id="additionalrequirementsforbaprogramstextcontainer"><h3>Language</h3><p>BA students require language.</p></div><div id="nyliberalartsandsciencestextcontainer">NYC requires liberal arts credits.</div>'
    result=parse_policy(html,program_id='test-program',profile='nupath');validate_requirements(result)
    assert len(result['requirements'])==19 and not result['courses']
    assert not any('language' in r['summary'].lower() or 'NYC' in r['summary'] for r in result['requirements'])
    changed=parse('nupath',NUPATH.replace('up to two','up to three').replace('Up to five','Up to four').replace('minimum of 64','minimum of 72'))
    assert any('at most 3' in r['summary'] for r in changed['requirements'])
    assert any('at most 4' in r['summary'] for r in changed['requirements'])
    assert any('at least 72' in r['summary'] for r in changed['requirements'])
    with pytest.raises(ValueError,match='list/count'):parse('nupath',NUPATH.replace('set of 11','set of 12'))


def test_combined_home_college_is_not_inferred_from_catalog_location():
    content='''<h2>Double Major</h2><p>Different policy.</p><h2>Combined Majors</h2><p>A combined major is one major with at least nine courses from each discipline. No more than two courses may count for both disciplines and at least 16 courses in the combined major. It includes multiple points of curricular integration. Most combined majors allow the student to choose the home college. Students receive one major, one degree, and one diploma.</p><h2>Independent Majors</h2><p>Different approval process.</p>'''
    p=parse('combined',content);validate_requirements(p)
    assert any('individual student’s choice' in r['summary'] for r in p['requirements'])
    assert any('at least 9' in r['summary'] and 'at most 2' in r['summary'] for r in p['requirements'])
    with pytest.raises(ValueError,match='semantics'):parse('combined',content.replace('Most combined majors allow the student to choose the home college','The catalog college is mandatory'))


def test_capstone_is_in_major_without_requiring_one_per_combined_discipline():
    result=parse('nupath',NUPATH)
    node=next(r for r in result['requirements'] if r['id']=='test-program-req-policy-nupath-competency-11')
    assert 'in the major' in node['summary']
    assert 'may specify' in node['summary'] and 'extra capstone in every discipline' in node['summary']
    assert node['kind']=='note' and node['course_ids']==[]
    with pytest.raises(ValueError,match='semantics'):
        parse('nupath',NUPATH.replace('Students must complete a capstone in their major','Any outside elective satisfies capstone'))


def test_progression_appeal_limit_is_observed_and_stays_conditional():
    content='''<p>Students maintain an overall GPA of 1.800 at the end of each semester of their freshman year and a minimum cumulative GPA of 2.000 thereafter. Earn at least 12 semester hours in the semester just completed. Individual colleges may have additional requirements. Academic Standing Committee reviews appeals. Dismissal may occur after two full-term academic semesters or below a 1.000 GPA or fewer than 4 earned semester hours, at the discretion of their college. Generally, a student on probation may be granted no more than one additional full-term academic semester.</p>'''
    result=parse('progression',content)
    node=next(r for r in result['requirements'] if r['id']=='test-program-req-policy-progression-dismissal')
    assert 'generally allows no more than 1' in node['summary'] and node['kind']=='note'
    changed=parse('progression',content.replace('no more than one','no more than two'))
    assert 'generally allows no more than 2' in changed['requirements'][-1]['summary']
