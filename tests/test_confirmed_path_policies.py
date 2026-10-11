"""Local policies preserve route/credential scope rather than universal permission."""
import json
from pathlib import Path
import pytest
from atlas.adapters import northwestern_second_majors as nw, stanford_symsys_concentrations as sy
ROOT=Path(__file__).resolve().parents[1]

def core_html():
 return '''<main><h1>Core Requirements</h1><p>Updated April 2, 2026. End: end of first week of Winter Quarter, Junior Year. Components: 3 or more units each; final approval by the Symbolic Systems Program office. Units must be applied to a student's Concentration.</p><h4>Practicum</h4><ul><li><a href="/not-integrative">CS 999</a>: Practicum-only synthetic option</li></ul><h4>Integrative Requirement*</h4><p>It must be completed no earlier than the Junior Year.</p><ul><li><a href="/honors">SYMSYS 190</a>: Honors continuation (continuation of the course taken for the Practicum)</li><li>A course in the 195-series or <a href="/project">CS 177</a>: Synthetic Project</li><li>Supervised research with a faculty member through <a href="/independent">SYMSYS 196</a>: Synthetic Study, or <ul><li><a href="/department">CS 197</a>: Synthetic Research</li></ul></li><li>A Concentration-Specific Integrative Course</li></ul></main>'''
@pytest.mark.parametrize('route',['ai','hai'])
def test_integrative_pool_excludes_host_practicum_and_preserves_open_series(route):
 r=sy.parse_core(core_html(),route);codes={c['code'] for c in r['courses']}
 assert codes=={'SYMSYS 190','CS 177','SYMSYS 196','CS 197'}
 assert 'SYMSYS 195' not in codes and 'CS 999' not in codes
 assert all(x['kind']=='note' for x in r['requirements'])
 assert 'alternatives' in r['requirements'][-1]['summary']
 assert not {'curriculum_status','curriculum_audit','last_verified'} & r.keys()
 changed=sy.parse_core(core_html().replace('CS 197','CS 198').replace('Synthetic Research','Revised Research'),route)
 assert any(c['code']=='CS 198' and c['name']=='Revised Research' for c in changed['courses'])
@pytest.mark.parametrize('old,new',[('continuation of the course taken for the Practicum','first tutorial'),('Supervised research with a faculty member','unsupervised project'),('must be completed no earlier than the Junior Year','may be completed at any time')])
def test_integrative_eligibility_change_requires_review(old,new):
 with pytest.raises(ValueError):sy.parse_core(core_html().replace(old,new),'ai')

def test_old_pn_table_never_grants_ai_permission_and_new_row_requires_review():
 old='1/22/2018 Departmental Programs Computer Science Integrated Engineering Studies'
 r=nw.parse_pdf_text(old,'mccormick','pn-table')
 assert 'not silently applied' in r['requirements'][0]['summary']
 with pytest.raises(ValueError):nw.parse_pdf_text(old+' Artificial Intelligence - all courses allowed','mccormick','pn-table')

def test_wcas_pdf_scope_is_not_reassigned_to_ai():
 text='2025-2026 non-WCAS students second major and/or minor in WCAS Other rules may apply for other years'
 r=nw.parse_pdf_text(text,'non-mccormick','overlap-table')
 assert 'not direct authority' in r['requirements'][0]['summary']
 with pytest.raises(ValueError):nw.parse_pdf_text(text.replace('in WCAS','in McCormick'),'non-mccormick','overlap-table')

def test_home_school_policy_sources_do_not_leak_between_concrete_routes():
 mc=json.loads((ROOT/'data/programs/northwestern-ai-second-major-mccormick.json').read_text())
 other=json.loads((ROOT/'data/programs/northwestern-ai-second-major-non-mccormick.json').read_text())
 assert not any(s['id'].endswith('-communication') for s in mc['sources'])
 assert any(s['id'].endswith('-communication') for s in other['sources'])
 assert any('Communication and Bienen' in gap for gap in other['curriculum_audit']['unresolved_requirements'])
 assert all(p['award_level']=='other' and p['curriculum_status']=='partial' for p in [mc,other])

def test_rice_completion_is_local_not_a_host_degree_claim():
 p=json.loads((ROOT/'data/programs/rice-ece-ai-systems-specialization.json').read_text())
 assert p['curriculum_status']=='complete' and p['curriculum_audit']['scope']=='concentration'
 assert 'not an official academic credential' in p['overview']
 assert any('host-degree source discrepancy' in r['summary'] for r in p['requirements'])
 assert any('not a separately invented AI-specialization GPA' in r['summary'] for r in p['requirements'])
 assert all(c['credit_unit']=='semester_hours' for c in p['courses'])
