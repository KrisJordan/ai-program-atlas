from pathlib import Path
import json
import pytest
from atlas.adapters import miami_cognate_pools as pool
from atlas.db import validate_program

ROOT=Path(__file__).resolve().parents[1]
PIDS=['miami-data-science-ai-bs','miami-ai-technologies-business-bsba',
 'university-of-miami-data-science-and-artificial-intelligence-ba-degree',
 'university-of-miami-artificial-intelligence-technologies-for-business-other-degree']


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
    assert not any('summer' in s for s in d['curriculum_audit']['unresolved_requirements'])
    summer=next(r for r in d['requirements'] if r['id']==pid+'-policy-summer-transfer-conflict')
    assert 'Session A' in summer['summary'] and 'Session B' in summer['summary']
    assert 'credit' in summer['summary'] and summer['kind']=='note'
    assert '2075 unique course identities' in next(r['summary'] for r in d['requirements'] if r['id']==pid+'-cognate-directory-sample')
    if pid=='miami-data-science-ai-bs':assert next(r for r in d['requirements'] if r['title']=='Language course 200-level or higher')['credits']==9
    rules={r['id']:r for r in d['requirements']}
    assert rules[pid+'-cognate-directory-sample']['parent_id']==pid+'-supplement-individualized-overlap'
    assert rules[pid+'-thematic-ps_0031']['parent_id']==pid+'-policy-cognate-rules'
    assert 'at least 2' in rules[pid+'-thematic-ps_0031-group-2']['summary']
    assert 'exactly 2' in rules[pid+'-thematic-at_0027-group-2']['summary']
    assert not any('st_0003' in r for r in rules)
    assert len([c for c in d['courses'] if c['code']=='APY 392'])==1
    # The dated PDF clips this title; the independently read current AMS block
    # supplies its full identity without changing the original PDF evidence.
    dated=json.loads((ROOT/'research/miami-individualized-cognate-pool.json').read_text())
    assert next(c for c in dated['rows'] if c['code']=='AMS 335')['name'] is None
    current=next(c for c in d['courses'] if c['code']=='AMS 335')
    assert current['name']=="Topics in American Studies: Women's and Gender Studies"
    assert current['source_id']=='miami-context-courses-ams'
    assert current['category_review']['source_ids']==['miami-context-courses-ams']


@pytest.mark.parametrize('plan',list(pool.PLANS))
def test_optional_real_thematic_replay(plan):
    p=ROOT/'var/miami-cognates'/f'{plan}.html'
    if not p.exists():pytest.skip('Optional ignored public HTML capture')
    o=pool.parse_thematic(p.read_text(),pid='synthetic',plan=plan)
    assert len(o['courses'])=={'PS_0031':17,'AT_0027':27}[plan]
