import importlib.util
import json
from pathlib import Path
import pytest
from atlas.db import validate_program
ROOT=Path(__file__).resolve().parents[1]
IDS=['cmu-ai-business-concentration','georgia-tech-ai-thread','northeastern-chemical-engineering-ai-bsche']
def adapter(pid):
    spec=importlib.util.spec_from_file_location(pid,ROOT/'atlas/adapters'/pid/'adapter.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def cmu():
    groups=[]
    for instruction,codes in [('Required:',['70-445']),('Choose 1 course:',['70-317','70-441','70-389']),('Choose 1 course:',['70-334','73-367']),('Choose 1 course:',['70-374','70-467','70-498'])]:
        groups.append('<p>'+instruction+'<br>'+''.join('<span class="sc_courseinline"><a class="code" href="/search/?P='+c+'">'+c+'</a> Test course '+c+'</span><br>' for c in codes)+'</p>')
    return '<nav><h3>AI and Business</h3></nav><main><h1 class="page-title">Business Administration, B.S.</h1><div id="concentrationstextcontainer"><p>Business concentrations require at least 36 units beyond the Business Core. Courses are not allowed to double count including the minor requirement; prerequisites from courses outside the concentration apply. Students consult with their academic advisor.</p><h3>AI and Business</h3>'+''.join(groups)+'<h3>Other concentration</h3><p>99-999 excluded</p></div></main>'

def gt():
    pairs=''.join('<li><a href="/programs/pair-'+str(i)+'/">Artificial Intelligence &amp; Partner '+str(i)+'</a></li>' for i in range(8))
    return '<h1>Bachelor of Science in Computer Science</h1><div id="textcontainer">Each student selects two Threads<ul><li>All required CS courses require C or better.</li><li>All courses listed as required for a Thread require C or better.</li></ul></div><div id="threadstextcontainer"><h3>Artificial Intelligence</h3><ul>'+pairs+'</ul><h3>Other</h3><ul><li>Unrelated</li></ul></div>'

def gt_thread():
    return '<h1>Artificial Intelligence</h1><div><h4>Required Courses:</h4><ul><li>CS 2050 or CS 2051 Discrete Math, 3</li><li>CS 3600 Introduction to Artificial Intelligence, 3</li></ul><h6>Pick 1 of Embodied Intelligence</h6><ul><li>CS 3630 Robotics, 3</li><li>CS 3790 Cognitive Science, 3</li></ul><h6>Pick 1 of Approaches to Intelligence</h6><ul><li>CS 4641 Machine Learning, 3</li><li>CS 4644 Deep Learning, 3</li></ul><h4>Elective Courses:</h4><ul><li>CS 9999 Unreviewed suggestion, 99</li></ul></div>'

def ne():
    m=adapter(IDS[2]); headings=''.join('<h2>'+s+'</h2>' for s in m.SECTIONS)
    return '<div id="site-title"><h1>'+m.TITLE+'</h1></div><div>Academic Catalog 2026-2027</div><div id="programrequirementstextcontainer">'+headings+'<p>NUpath (IC), (SI), (DD), and (EX) are not explicitly satisfied by required engineering coursework. Successful co-op may fulfill the EX requirement.</p><p>134 total semester hours required</p><table class="sc_courselist"><tr><td class="codecol"><a class="code" href="/course/">CHME 4512</a></td><td>Process Control</td><td class="hourscol">4</td></tr></table></div>'

def test_cmu_four_independent_groups_and_real_changes():
    m=adapter(IDS[0]); r=m.parse(cmu())
    assert len(r['courses'])==9
    assert [x['count'] for x in r['requirements'] if x['kind']=='choose_courses']==[1,1,1]
    changed=cmu().replace('Choose 1 course:','Choose 2 courses:',1).replace('70-317','70-318')
    r=m.parse(changed)
    assert any(x['count']==2 for x in r['requirements'])
    assert '70-318' in {x['code'] for x in r['courses']}
    assert all(x['credits'] is None for x in r['courses'])

@pytest.mark.parametrize('before,after',[('Business Administration, B.S.','Business Administration, MBA'),('<h3>AI and Business</h3>','<h3>Accounting</h3>'),('Choose 1 course:','Choose several courses:'),('not allowed to double count','may double count')])
def test_cmu_scope_failures(before,after):
    with pytest.raises(ValueError):adapter(IDS[0]).parse(cmu().replace(before,after))

def test_gt_eight_pairings_and_no_fake_degrees():
    r=adapter(IDS[1]).parse(gt())
    assert r['program_kind']=='concentration' and len(r['requirements'])==11
    assert r['requirements'][0]['kind']=='alternative'
    assert 'courses' not in r
    with pytest.raises(ValueError):adapter(IDS[1]).parse(gt().replace('Each student selects two Threads','Choose any interest'))
    with pytest.raises(ValueError):adapter(IDS[1]).parse(gt().replace('<h3>Artificial Intelligence</h3>','<h3>Intelligence</h3>'))

def test_gt_required_courses_only_alternatives_and_changed_counts():
    m=adapter(IDS[1]);r=m.parse_thread(gt_thread())
    assert len(r['courses'])==7 and all(c['code']!='CS 9999' for c in r['courses'])
    assert any(x['kind']=='alternative' and len(x['course_ids'])==2 for x in r['requirements'])
    changed=m.parse_thread(gt_thread().replace('Pick 1 of Approaches','Pick 2 of Approaches'))
    assert next(x for x in changed['requirements'] if x['title']=='Approaches to Intelligence')['count']==2
    assert all(c['prerequisites'] is None and c['credit_unit']=='unknown' for c in changed['courses'])
    with pytest.raises(ValueError):m.parse_thread(gt_thread().replace('<h1>Artificial Intelligence</h1>','<h1>Graduate AI</h1>'))

def test_ne_exact_bsche_supported_and_unrelated_award_rejected():
    m=adapter(IDS[2]);r=m.parse(ne())
    assert r['award_level']=='other' and r['title'].endswith('BSChE (Boston)')
    assert r['courses'][0]['code']=='CHME 4512'
    assert m.parse(ne().replace('CHME 4512','CHME 4703'))['courses'][0]['code']=='CHME 4703'
    with pytest.raises(ValueError):m.parse(ne().replace('BSChE','MSChE'))
    from atlas.adapters.northeastern_courseleaf import parse_catalog
    with pytest.raises(ValueError):parse_catalog(ne(),program_id='bad',title='Chemical Engineering and Artificial Intelligence, BFA (Boston)',url=m.SOURCES[0],required_sections=[],award_level='other')

@pytest.mark.parametrize('pid',IDS)
def test_reviewed_seed_and_optional_live_replay(pid):
    seed=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());validate_program(seed)
    if pid == IDS[0]:
        assert seed['curriculum_status']=='complete' and seed['curriculum_audit']['scope']=='concentration'
    else:
        assert seed['curriculum_status']=='partial'
    assert seed['first_offered'] is None and 'family' not in seed
    m=adapter(pid);key={IDS[0]:'cmu-business',IDS[1]:'gt-bscs',IDS[2]:'ne-chemical'}[pid]
    path=ROOT/'.cache/research/confirmed4'/f'{key}.html'
    if not path.exists():return
    r=m.parse(path.read_text());requirements=r['requirements'];courses=r.get('courses',[])
    if pid==IDS[1]:
        extra=m.parse_thread((path.parent/'gt-thread.html').read_text());requirements+=extra['requirements'];courses+=extra['courses']
    if pid == IDS[0]:
        assert all(r in seed['requirements'] for r in requirements)
        assert {(c['id'],c['code'],c['name']) for c in courses}=={(c['id'],c['code'],c['name']) for c in seed['courses']}
    elif pid == IDS[2]:
        # The degree page supplies requirement rows; independently reviewed
        # subject pages now enrich credits/prerequisites and manual taxonomy.
        assert requirements == seed['requirements']
        actual = {c['id']:c for c in seed['courses']}
        assert {(c['id'],c['code'],c['name']) for c in courses} == {(c['id'],c['code'],c['name']) for c in seed['courses']}
        for observed in courses:
            assert 'category_review' not in observed
            if observed['credits'] is not None:
                assert observed['credits'] == actual[observed['id']]['credits']
                assert observed['credit_unit'] == actual[observed['id']]['credit_unit']
    else:
        assert requirements==seed['requirements'] and courses==seed['courses']
