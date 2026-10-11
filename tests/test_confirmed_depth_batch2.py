"""Small structural fixtures exercise new observations, not copied catalog pages."""
import importlib.util
import json
from pathlib import Path
import pytest
from atlas.adapters.confirmed_depth_batch2 import parse_ncsu,parse_msu,parse_tamu_catalog,parse_tamu_department
from atlas.db import validate_program

ROOT=Path(__file__).resolve().parents[1]
IDS=('ncsu-computer-engineering-ai-ml-concentration','ncsu-electrical-engineering-ai-ml-concentration','michigan-state-cs-ai-concentration','texas-am-ai-arts-minor')


def row(code,name,credit='',alternative=False):
    return f'<tr class="{"orclass" if alternative else ""}"><td class="codecol">{"or " if alternative else ""}<a class="code" href="/course">{code}</a></td><td>{name}</td>'+(f'<td class="hourscol">{credit}</td>' if credit else '')+'</tr>'


def table(rows):return '<table class="sc_courselist">'+rows+'</table>'


def ncsu(discipline='Computer',hours=10,ai_extra=''):
    core='<tr class="areaheader"><td>AI/ML Concentration</td></tr>'+row('MA 305','Linear Algebra','3')+row('MA 405','Advanced Linear Algebra',alternative=True)+row('ECE 411','Introduction to Machine Learning','3')+f'<tr><td>AI/ML Electives</td><td class="hourscol">6</td></tr><tr><td>Open Electives</td><td class="hourscol">{hours}</td></tr><tr class="areaheader"><td>Other Major</td></tr>'+row('UNRELATED 101','Not concentration scope','4')
    return f'<main><h1>{discipline} Engineering (BS): Artificial Intelligence and Machine Learning Concentration</h1><div id="planrequirementstextcontainer">'+table(core)+table('')+table(row('ECE 410','Signal Processing','3')+ai_extra)+table(row('ECE 531','','3')+row('ECE 592','Special Topics','1-6'))+table(row('ECE 411','Introduction to Machine Learning','3'))+'<p>Minimum 3.5 GPA for graduate courses. A maximum of 3 credit hours of DSA courses. MA 405 is recommended. College electives with permission of advisor.</p></div></main>'


def msu(extra=''):
    def r(code,name,credits):
        department,number=code.split();return f'<tr><td>{department}</td><td>{number}</td><td>{name}</td><td></td><td>{credits}</td></tr>'
    return '<main><h2>Concentrations in Computer Science</h2><p>certification will appear on the student’s official transcript; no more than one concentration; 3 credits of CSE 499 Undergraduate Research with approval of the Department of Computer Science and Engineering.</p><table><tr><td><strong>Artificial Intelligence</strong></td></tr><tr><td>Two of the following courses (6 credits):</td></tr>'+r('CSE 404','Introduction to Machine Learning',3)+r('CSE 440','Artificial Intelligence',3)+r('CSE 482','Big Data Analysis',3)+'<tr><td>Three of the following courses not taken above (9 to 12 credits):</td></tr>'+r('CSE 440','Introduction to Artificial Intelligence',3)+r('LIN 401','Introduction to Linguistics',4)+r('CSE 803','Computer Vision',3)+extra+'<tr><td><strong>Computer Systems</strong></td></tr>'+r('CSE 410','Outside AI inventory',3)+'</table></main>'


def tamu():
    return '<main><h1>Artificial Intelligence in the Arts - Minor</h1><p>Students seeking to declare the minor must email pvfaadvising@tamu.edu</p><div id="programrequirementstextcontainer">'+table('<tr><th>Semester Credit Hours</th></tr>'+row('PVFA 201','Introduction to Artificial Intelligence in the Arts',3)+row('PVFA 301','AI Ethics',3)+row('PVFA 409','AI Capstone',3)+'<tr><td>Prescribed elective</td><td>6</td></tr><tr><td>Total Semester Credit Hours</td><td>15</td></tr>')+'<dl class="sc_footnotes"><dt>1</dt><dd>Select from '+', '.join(f'<a class="code">{c}</a>' for c in ['ARTS 301','DCED 307','MSTC 245','VIST 371'])+'</dd></dl></div></main>'


def tamu_dept():
    def t(codes):return '<table>'+''.join(f'<tr><td>{c}</td><td>Official title {c}</td><td>3</td></tr>' for c in codes)+'</table>'
    return '<main><h1>AI In The Arts</h1><p>Undergraduate Minor</p><h2>Three Required Courses, 9 Credit Hours</h2>'+t(['PVFA 201','PVFA 301','PVFA 409'])+'<h2>Select two from the following (6 hours)</h2>'+t(['ARTS 301','DCED 307','MSTC 245','VIST 371'])+'</main>'


def test_ncsu_scopes_local_rows_keeps_unknowns_and_source_changes():
    p=parse_ncsu(ncsu(),IDS[0],'source','https://example.edu/catalog','Computer')
    courses={c['code']:c for c in p['courses']}
    assert 'UNRELATED 101' not in courses
    assert courses['ECE 531']['name'] is None
    assert courses['ECE 592']['credits'] is None
    assert courses['MA 405']['credits'] is None
    assert len([c for c in p['courses'] if c['code']=='ECE 411'])==1
    assert all(c['credit_unit']=='unknown' for c in courses.values())
    assert next(r for r in p['requirements'] if r['id'].endswith('-linear'))['count']==1
    assert 'Select 10 published hours' in next(r for r in p['requirements'] if r['id'].endswith('-open-pool'))['summary']
    changed=parse_ncsu(ncsu(hours=12,ai_extra=row('ECE 525','Neural Networks',alternative=True)),IDS[0],'source','https://example.edu/catalog','Computer')
    assert changed['observed_hours']['open']=='12'
    assert any(c['code']=='ECE 525' for c in changed['courses'])
    with pytest.raises(ValueError):parse_ncsu(ncsu().replace('3.5','3.0'),IDS[0],'source','https://example.edu','Computer')


def test_ncsu_rejects_wrong_concentration_and_missing_table():
    with pytest.raises(ValueError):parse_ncsu(ncsu('Electrical'),IDS[0],'source','https://example.edu','Computer')
    with pytest.raises(ValueError):parse_ncsu(ncsu().replace(table(''),''),IDS[0],'source','https://example.edu','Computer')


def test_msu_two_disjoint_choices_transcript_and_research_option():
    p=parse_msu(msu(),IDS[2],'source','https://example.edu')
    courses={c['code']:c for c in p['courses']}
    assert 'CSE 410' not in courses
    assert courses['CSE 440']['name']=='Artificial Intelligence'
    assert courses['CSE 499']['credits'] is None
    assert [r['count'] for r in p['requirements'][:2]]==[2,3]
    assert 'not taken above' in p['requirements'][1]['summary']
    assert any('official-transcript certification' in r['summary'] for r in p['requirements'])
    changed=parse_msu(msu('<tr><td>PSY</td><td>301</td><td>Cognitive Neuroscience</td><td>3</td></tr>'),IDS[2],'source','https://example.edu')
    assert len(changed['courses'])==len(p['courses'])+1
    with pytest.raises(ValueError):parse_msu(msu().replace('not taken above',''),IDS[2],'source','https://example.edu')
    with pytest.raises(ValueError):parse_msu(msu().replace('certification will appear on the student’s official transcript','informal focus'),IDS[2],'source','https://example.edu')


def test_tamu_sources_preserve_separate_credit_and_course_choice_evidence():
    p=parse_tamu_catalog(tamu(),IDS[3],'catalog','https://example.edu/catalog')
    assert len(p['courses'])==7
    assert len([c for c in p['courses'] if c['name'] is None])==4
    assert p['requirements'][1]['kind']=='choose_credits' and p['requirements'][1]['credits']==6
    assert all(c['credit_unit']=='semester_hours' for c in p['courses'])
    d=parse_tamu_department(tamu_dept(),IDS[3],'department','https://example.edu/dept')
    assert d['requirements'][0]['count']==2
    assert all(c['credits']==3 for c in d['courses'])
    changed=parse_tamu_catalog(tamu().replace('ARTS 301','ARTS 302'),IDS[3],'catalog','https://example.edu/catalog')
    assert any(c['code']=='ARTS 302' for c in changed['courses'])
    with pytest.raises(ValueError):parse_tamu_department(tamu_dept().replace('Select two','Select three'),IDS[3],'dept','https://example.edu')


@pytest.mark.parametrize('pid',IDS)
def test_curated_new_record_valid_partial_and_observer_present(pid):
    p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())
    validate_program(p)
    assert p['curriculum_status']=='partial' and not p.get('curriculum_audit')
    assert p['first_offered'] is None
    assert all(c['description'] is None and c['prerequisites'] is None for c in p['courses'])
    spec=importlib.util.spec_from_file_location('depth2_adapter',ROOT/'atlas/adapters'/pid/'adapter.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert module.PROGRAM_ID==pid and module.SOURCES


def test_live_curated_ncsu_pools_do_not_merge_variant_exceptions():
    rows=[json.loads((ROOT/'data/programs'/f'{pid}.json').read_text()) for pid in IDS[:2]]
    for p,expected in zip(rows,[True,False]):
        course_map={c['id']:c['code'] for c in p['courses']}
        pool=next(r for r in p['requirements'] if r['id'].endswith('-ai-pool'))
        assert ('ECE 525' in [course_map[cid] for cid in pool['course_ids']])==expected
    assert [len(p['courses']) for p in rows]==[111,111]


def test_six_institution_ledger_accounts_for_new_ids_and_search_boundaries():
    ledger=json.loads((ROOT/'data/surveys/national-confirmed-depth-batch2-2026-10-11.json').read_text())
    assert {r['institution_id'] for r in ledger}=={'north-carolina-state-university','university-of-florida','university-of-georgia','ohio-state-university','michigan-state-university','texas-am-university'}
    assert {pid for r in ledger for pid in r['new_program_ids']}==set(IDS)
    assert all(r['absence_claim'] is False and r['remaining_work'] for r in ledger)
    assert all(s['url'].startswith('https://') and s['locator'] and s['access_method'] for r in ledger for s in r['sources'])
    assert sum(len(r['sources']) for r in ledger)==31
    ohio=next(r for r in ledger if r['institution_id']=='ohio-state-university')
    assert ohio['access_issues'][0]['classification']=='stale_url'
    assert all(r['status']=='confirmed' for r in ledger)


def test_tamu_curated_electives_are_one_selection_with_both_constraints():
    p=json.loads((ROOT/'data/programs/texas-am-ai-arts-minor.json').read_text())
    choices=[r for r in p['requirements'] if r['kind'].startswith('choose_')]
    assert len(choices)==1
    assert choices[0]['count']==2 and choices[0]['credits']==6
    assert choices[0]['source_id'].endswith('-department')
