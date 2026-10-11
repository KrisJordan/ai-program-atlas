import importlib.util,json
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];PID='rochester-institute-of-technology-artificial-intelligence-bs-degree'
def adapter():
 s=importlib.util.spec_from_file_location('rit_degree',ROOT/'atlas/adapters'/PID/'adapter.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def test_study_observation_reads_changed_blocks_without_replaying_catalog():
 html=(ROOT/'tests/fixtures/next_degrees/rit-study.html').read_text()
 d=adapter().parse(html.replace('two blocks','three blocks'))
 assert '3 cooperative' in d['requirements'][0]['summary']
 assert 'courses' not in d and 'curriculum_audit' not in d and 'last_verified' not in d
 with pytest.raises(ValueError):adapter().parse(html.replace('two blocks','unpublished blocks'))
def test_reviewed_catalog_preserves_choices_repeated_coop_and_scope():
 from atlas.db import validate_program
 d=json.loads((ROOT/'data/programs'/f'{PID}.json').read_text());validate_program(d)
 assert len([c for c in d['courses'] if c['source_id']=='rit-ai-bs-rendered-2026-2027'])==40
 assert len([c for c in d['courses'] if c['source_id']=='rit-ai-bs-advising-2026-2027'])==3
 assert sum(c['code']=='IDAI-499' for c in d['courses'])==1
 assert len([r for r in d['requirements'] if r['source_id']=='rit-ai-bs-catalog' and r['kind']=='choose_courses' and r['count']==1])==6
 electives=next(r for r in d['requirements'] if r['id'].endswith('-ai-electives'))
 assert electives['count']==2 and len(electives['course_ids'])==3
 assert any(r['parent_id']==electives['id'] and r['kind']=='alternative' for r in d['requirements'])
 assert d['curriculum_status']=='partial' and d['curriculum_audit']['unresolved_requirements']
 assert next(r for r in d['requirements'] if r['id'].endswith('-total'))['credits']==122
