import json
from pathlib import Path
import pytest
from atlas.adapters import ucsb_progression as p
from atlas.db import validate_program


def test_mcp_parser_reads_actual_thresholds_not_seed_values():
    html='<h1>Minimum Cumulative Progress</h1><p>90-105 units; less than 90 units or more than 105 units; previous two consecutive MCP quarters; 12 regular quarters; 9 regular quarters; 215 units</p><table><tr><th>Number of MCP Quarters</th><th>Units Completed</th></tr>'
    html+=''.join(f'<tr><td>{i}</td><td>{i*13}</td></tr>'for i in range(1,13))+'</table>'
    r=p.parse_progress(html);assert '12: 156'in r['requirements'][0]['summary']
    assert '12: 180'not in r['requirements'][0]['summary']
    assert 'curriculum_audit'not in r
    with pytest.raises(ValueError):p.parse_progress(html.replace('<td>12</td>','<td>13</td>'))


def test_writing_parser_uses_course_blocks_credits_and_prereqs():
    html='<h1>Writing 1</h1><h3>Writing 1. Synthetic title</h3><p><strong>5 units</strong><em>Prerequisite: Synthetic restriction</em></p><h3>Writing 1E. Synthetic engineering title</h3><p><strong>4 units</strong><em>Prerequisite: Engineering only</em></p>'
    r=p.parse_writing(html);assert r['courses'][0]['credits']==5
    assert r['courses'][0]['name']=='Synthetic title'
    assert r['courses'][0]['prerequisites']=='Synthetic restriction'
    with pytest.raises(ValueError):p.parse_writing(html.replace('Writing 1E.','Writing 2.'))


def test_reviewed_pdf_observations_never_expand_compressed_ranges():
    r=p.parse_gear_ahi_observation([('Test department','142AL-S, 133AA-ZZ')])
    assert not r.get('courses')
    assert '142AL-S'in r['requirements'][1]['summary']
    assert 'curriculum_audit'not in r
    with pytest.raises(ValueError):p.parse_guidance_observation('Google Docs shell')


def test_ucsb_curated_progress_rules_validate_and_keep_exact_blockers():
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text());validate_program(d)
    rows=[n for n in d['requirements']if n['id'].startswith('ucsb-ai-bs-progress-')]
    assert len(rows)==41
    assert sum('-ahi-row-'in n['id']for n in rows)==15
    assert any('up to two UCEAP'in n['summary']for n in rows)
    assert any('at least25%'in n['summary']for n in rows)
    assert any(o.get('statement_type')=='career_pathway'and o['source_id']=='ucsb-ai-bs-faq'for o in d['outcomes'])
    assert next(c for c in d['courses']if c['code']=='CMPSC 41')['credits']is None
    assert d['curriculum_status']=='partial'
