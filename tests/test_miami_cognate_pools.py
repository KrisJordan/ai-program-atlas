from pathlib import Path
import json
import pytest
from atlas.adapters import miami_cognate_pools as pool
from atlas.db import validate_program

ROOT=Path(__file__).resolve().parents[1]
PIDS=['miami-data-science-ai-bs','miami-ai-technologies-business-bsba',
 'university-of-miami-data-science-and-artificial-intelligence-ba-degree',
 'university-of-miami-artificial-intelligence-technologies-for-business-other-degree']


def pdf_page(rows):
    return ('Subject\nCourse No.\nCourse Title\nArea of Knowledge\nTypically Oﬀered\nCourse ID\n'+rows+
            '\nCourses Eligible to be Used in Individualized Cognates\n(Updated 10/2/2026)')

PDF=pdf_page('ZZZ\n101\nSynthetic first title\nArts & Humanities\nFall\n100001\nPeople & Society\nFall\n100001\n102\nTruncated sy..\nPeople & Society\nSpring\n100002')


def test_pdf_multi_area_identity_and_truncated_title_do_not_invent_metadata():
    rows=pool.parse_individualized_text(PDF+'\f'+PDF)
    assert len(rows)==2
    assert rows[0]['areas']==['Arts & Humanities','People & Society']
    assert rows[0]['pages']==[1,2]
    assert rows[1]['name'] is None and rows[1]['display_title']=='Truncated sy..'
    o=pool.individualized_observation(PDF+'\f'+PDF,pid='synthetic')
    assert len(o['courses'])==2
    assert all(c['credits'] is None and c['prerequisites'] is None for c in o['courses'])
    assert all(r['kind']=='note' for r in o['requirements'])
    assert 'None may satisfy another degree requirement' in o['requirements'][0]['summary']
    assert not {'curriculum_status','curriculum_audit','last_verified'} & o.keys()


@pytest.mark.parametrize('before,after',[
 ('Updated 10/2/2026','Updated 11/2/2026'),('Course ID','Credit Hours'),
 ('Arts & Humanities','New Area'),('100002','not-an-id'),
])
def test_changed_pdf_schema_or_identity_fails_closed(before,after):
    with pytest.raises(ValueError):pool.parse_individualized_text(PDF.replace(before,after))


def row(code,name='Synthetic course',credit='3/3',extra='',inactive=False):
    return f'<tr class="course"><td>{code}'+(' *' if inactive else '')+f'</td><td></td><td><a>{name}</a>{extra}</td><td>{credit}</td><td>Fall</td></tr>'


def thematic():
    title,area,unit=pool.PLANS['PS_0031']
    return f'''<h1>{title}</h1><select id="term_selector"><option selected>Fall 2026</option></select>
      <ul><li>Academic Plan PS_0031</li><li>Cognate {area}</li><li><span>Responsible Academic Unit</span><span>{unit}</span></li>
      <li>Recommended for All students.</li><li>Students must complete at least 3 courses for at least 9 credits.</li></ul>
      <p>Complete 2 of the following option groups:</p>
      <div><p>Complete at least 1 course from the following:</p><table class="group_table">{row('AAA 101')}{row('AAA 102',inactive=True)}</table></div>
      <div><p>Complete exactly 2 courses from the following:</p><table class="group_table">{row('BBB 201',credit='1/3')}{row('BBB 202',extra='<div>Prerequisite: AAA 101.</div>')}{row('BBB 203')}</table></div>
      <p>*Indicates an inactive course</p>'''


def test_thematic_counts_inactive_and_variable_credit_semantics():
    o=pool.parse_thematic(thematic(),pid='synthetic',plan='PS_0031')
    courses={c['code']:c for c in o['courses']}
    assert 'AAA 102' not in courses
    assert courses['BBB 201']['credits'] is None
    assert courses['BBB 202']['prerequisites']=='Prerequisite: AAA 101.'
    assert 'AAA 102 inactive' in o['requirements'][-1]['summary']
    assert o['requirements'][1]['count']==1 and 'at least 1' in o['requirements'][1]['summary']
    assert o['requirements'][2]['count']==2 and 'exactly 2' in o['requirements'][2]['summary']
    assert '1–3 credits' in o['requirements'][2]['summary']
    assert 'individualized' in o['requirements'][0]['summary'].lower()
    assert not {'curriculum_status','curriculum_audit','last_verified'} & o.keys()


def test_changed_selection_count_is_observed_not_replayed():
    changed=thematic().replace('Complete exactly 2 courses','Complete exactly 3 courses')
    o=pool.parse_thematic(changed,pid='synthetic',plan='PS_0031')
    assert o['requirements'][2]['count']==3


@pytest.mark.parametrize('before,after',[
 ('Fall 2026','Spring 2027'),('Recommended for All students.','Recommended for majors only.'),
 ('Gender and Sexuality Studies','Another Unit'),('Complete exactly 2 courses','Choose freely'),
 ('*Indicates an inactive course','*Another condition'),
])
def test_unreviewed_thematic_applicability_requires_review(before,after):
    with pytest.raises(ValueError):pool.parse_thematic(thematic().replace(before,after),pid='synthetic',plan='PS_0031')


@pytest.mark.parametrize('pid',PIDS)
def test_curated_optional_routes_and_known_conflicts_preserved(pid):
    d=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());validate_program(d)
    assert d['curriculum_status']=='partial'
    assert any('summer' in s for s in d['curriculum_audit']['unresolved_requirements'])
    assert any('2 of 50' in s and '2 of 215' in s for s in d['curriculum_audit']['unresolved_requirements'])
    if pid=='miami-data-science-ai-bs':assert any('nine-credit' in s and 'three-credit' in s for s in d['curriculum_audit']['unresolved_requirements'])
    rules={r['id']:r for r in d['requirements']}
    assert rules[pid+'-cognate-directory-sample']['parent_id']==pid+'-supplement-individualized-overlap'
    assert rules[pid+'-thematic-ps_0031']['parent_id']==pid+'-policy-cognate-rules'
    assert 'at least 2' in rules[pid+'-thematic-ps_0031-group-2']['summary']
    assert 'exactly 2' in rules[pid+'-thematic-at_0027-group-2']['summary']
    assert not any('st_0003' in r for r in rules)
    assert len([c for c in d['courses'] if c['code']=='APY 392'])==1
    assert next(c for c in d['courses'] if c['code']=='AMS 335')['name'] is None


def test_fact_manifest_counts_are_bounded_and_multi_area_not_double_counted():
    m=json.loads((ROOT/'research/miami-cognate-pool-sample.json').read_text())
    assert m['scope']['complete_pool'] is False
    assert len(m['rows'])==77
    assert len({r['code'] for r in m['rows']})==77
    assert sum(len(r['areas']) for r in m['rows'])==101
    assert sum(r['name'] is None for r in m['rows'])==3


@pytest.mark.parametrize('plan',list(pool.PLANS))
def test_optional_real_thematic_replay(plan):
    p=ROOT/'var/miami-cognates'/f'{plan}.html'
    if not p.exists():pytest.skip('Optional ignored public HTML capture')
    o=pool.parse_thematic(p.read_text(),pid='synthetic',plan=plan)
    assert len(o['courses'])=={'PS_0031':17,'AT_0027':27}[plan]
