from importlib import import_module
from pathlib import Path
import hashlib
import json
import pytest

PID='university-of-south-florida-artificial-intelligence-bs-degree'
policies=import_module('atlas.adapters.'+PID+'.university_policies')
metadata=import_module('atlas.adapters.'+PID+'.course_metadata')

def ge_page():
    rows=''.join('<tr><td>'+n+'</td><td>3</td><td>3</td><td>6</td></tr>' for n in ['Communication','Humanities','Mathematics','Natural Science','Social Science'])
    return '''<main><h1>USF's General Education</h1><p>36 hours divided into 15 hours and 21 hours of USF-chosen courses.
    There are no requirements around how many of these enhancements students need to take.
    In some cases a student can take a State Core course as a gen ed elective; please check with an academic advisor.</p>
    <table><tr><th>Discipline</th><th>State Core Credits</th><th>USF Gen Ed Credits</th><th>Total</th></tr>'''+rows+'''<tr><td>Choose 2 courses from any gen ed discipline above</td><td>0</td><td>6</td><td>6</td></tr></table></main>'''

def test_ge_distribution_is_open_eligibility_not_invented_pool():
    p=policies.parse_ge(ge_page())
    assert len(p['requirements'])==8
    assert p['requirements'][0]['credits']==36
    assert len([r for r in p['requirements'] if r['parent_id']])==6
    assert all(r['kind']=='note' and not r['course_ids'] and r['credit_unit']=='unknown' for r in p['requirements'])
    assert 'no separate student quota' in p['requirements'][-1]['summary']

@pytest.mark.parametrize('old,new',[('>3</td><td>3</td>','>3</td><td>6</td>'),('Natural Science','Science'),('Choose 2 courses','Choose 3 courses'),('no requirements around','new requirements around')])
def test_ge_material_changes_rejected(old,new):
    with pytest.raises(ValueError):policies.parse_ge(ge_page().replace(old,new))

def course_page(number='1000',desc='Synthetic AI description.',prereq='',coprereq='',restrictions=''):
    labels={'lblDescription':desc,'lblcredithours':'3','lblprereq':prereq,'lblCorequisites':'','lblcoprereq':coprereq,'lblcreq':restrictions,'lblOtherInfo':''}
    return '<main><h1>Course Details</h1><h2>CAI '+number+': Example AI Course</h2>'+''.join('<label id="MainContent_'+key+'">'+value+'</label>' for key,value in labels.items())+'</main>'

def test_course_metadata_keeps_boolean_prereqs_and_unknown_blanks(monkeypatch):
    monkeypatch.setitem(metadata.REVIEWED,'1000',(hashlib.sha256(b'Synthetic AI description.').hexdigest(),'Reviewed synthetic summary.'))
    c=metadata.parse_course(course_page(prereq='[COP 2510 (min grade B) OR CGS 2060 (min grade B)] AND CAI 1000 (min grade B)',coprereq='COP 4530',restrictions='Majors Only'),'1000')['courses'][0]
    assert c['credits']==3 and c['credit_unit']=='unknown'
    assert ' OR ' in c['prerequisites'] and ' AND ' in c['prerequisites']
    assert 'Co-prerequisites: COP 4530' in c['prerequisites'] and 'Majors Only' in c['prerequisites']
    assert metadata.parse_course(course_page(),'1000')['courses'][0]['prerequisites'] is None
    assert c['public_site'] is None and c['syllabus'] is None

def test_changed_description_cannot_replay_old_paraphrase(monkeypatch):
    monkeypatch.setitem(metadata.REVIEWED,'1000',(hashlib.sha256(b'Synthetic AI description.').hexdigest(),'Reviewed synthetic summary.'))
    with pytest.raises(ValueError,match='description changed'):
        metadata.parse_course(course_page(desc='A different description.'),'1000')
    with pytest.raises(ValueError,match='identity missing'):
        metadata.parse_course(course_page(number='5005'),'1000')
    with pytest.raises(ValueError,match='field missing'):
        metadata.parse_course(course_page().replace('MainContent_lblprereq','wrong'),'1000')

@pytest.mark.parametrize('url,parser',list(policies.PARSERS.items())+list(metadata.PARSERS.items()))
def test_optional_source_cache_has_no_review_state(url,parser):
    path=Path('.cache/http')/(hashlib.sha256(url.encode()).hexdigest()+'.body')
    if not path.exists():pytest.skip('Optional local permitted source cache unavailable')
    p=parser(path.read_text())
    assert p['id']==PID
    assert not {'curriculum_status','curriculum_audit','last_verified'} & p.keys()
    with pytest.raises(ValueError):parser('<h1>Access denied</h1>'+path.read_text())

def test_civic_cohort_and_metadata_findings_in_reviewed_seed():
    p=json.loads((Path('data/programs')/(PID+'.json')).read_text())
    from atlas.db import validate_program
    validate_program(p)
    rules={r['id']:r for r in p['requirements']}
    assert 'Summer B 2021 onward requires both' in rules['usf-ai-civic-cohorts']['summary']
    assert 'additional-degree students are not categorically exempt' in rules['usf-ai-civic-cohorts']['summary']
    assert 'Course only' in rules['usf-ai-civic-acceleration']['summary']
    assert 'Fall 2024 onward' in rules['usf-ai-civic-routes']['summary']
    assert len([c for c in p['courses'] if c['description']])==29
    assert len([c for c in p['courses'] if c['prerequisites']])==21
    assert p['curriculum_status']=='partial' and p['curriculum_audit']['unresolved_requirements']


def civic_page():
    # Small source-shaped fixture with policy anchors, not a copied source document.
    return '''<main><h1>Civic Literacy Requirement</h1>
    Must be completed before graduation.
    Cohort 1 - Started Before The 2018 Summer B session.
    Cohort 2 - Started During 2018 Summer B through 2021 Summer A.
    Cohort 3 - Started Summer B 2021 or later: assessment AND approved course.
    Out-of-state students and students pursuing an additional bachelor’s degree are NOT exempt.
    Students entering in Fall 2024 or later can no longer use the internal test.
    POS 2041 Introduction to American Government, AMH 2010 American History I (timing applies), AMH 2020 US History since 1877.
    AMS X010: not offered at USF.
    High-school exam: 60% or better; official high school transcript.
    Internal test: 60% or higher; unlimited attempts.
    Both the exam and course requirement must be documented.
    External course syllabus: Office of Undergraduate Studies review.
    GE overlap: "C-" or higher. Returning graduates who did not meet the requirements as part of their initial degree must complete them.
    Naturalization/Citizenship Test: students will not have met the Civic Literacy requirement.
    Advanced Placement (AP) Government and Politics: United States Score required: 3 or higher Requirement Met: Course &amp; Assessment
    Advanced Placement (AP) United States History Score required: 4 or higher Requirement Met: Course &amp; Assessment
    Cambridge AICE History: U.S. History, c. 1840-1992 (A-level) Score required: A-E Requirement Met: Course only
    CLEP American Government Score required: 50 or higher Requirement Met: Course &amp; Assessment
    CLEP History of the United States I Score required: 50 or higher Requirement Met: Course &amp; Assessment
    CLEP History of the United States II: 1865 to present Score required: 50 or higher Requirement Met: Course only
    Dual Enrollment POSX041, AMH X020, AMH X010 (taken Fall 2024 or later), or AMS X010 (taken Fall 2024 or later) Score required: Passing Grade Requirement Met: Course only
    International Baccalaureate (IB) History of the Americas Score required: 5-7 Requirement Met: Course only
    </main>'''


def test_civic_parser_preserves_cohort_conditions_and_transfer_only_option():
    result=policies.parse_civic(civic_page())
    assert len(result['requirements'])==5
    assert {c['code'] for c in result['courses']}=={'POS 2041','AMH 2010','AMH 2020'}
    assert all(c['credits'] is None and c['prerequisites'] is None for c in result['courses'])
    assert 'transfer-only AMS X010' in result['requirements'][1]['summary']
    assert 'before graduation' in result['requirements'][0]['summary']
    assert 'unlimited attempts' in result['requirements'][1]['summary']

@pytest.mark.parametrize('old,new',[
 ('Score required: 3 or higher','Score required: 4 or higher'),
 ('Requirement Met: Course only','Requirement Met: Course &amp; Assessment'),
 ('"C-" or higher','"C" or higher'),
 ('did not meet the requirements as part of their initial degree','are exempt'),
])
def test_civic_changed_eligibility_needs_review(old,new):
    with pytest.raises(ValueError):policies.parse_civic(civic_page().replace(old,new))
