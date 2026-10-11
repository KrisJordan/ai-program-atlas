import json
from pathlib import Path
import pytest
from atlas.adapters.tufts_development_policy_review import parse_policy
ROOT=Path(__file__).resolve().parents[1]
PID='tufts-ai-development-minor'

def test_only_ai_development_section_is_observed():
 html='<h1>Policies and Documentation</h1><h2>Minor in AI Development</h2><p>'+'CS135 or EE140/CS128 is the required choice in this synthetic policy fixture. '*3+'</p><h2>Graduate program</h2><p>Other program</p>'
 a=parse_policy(html,PID)
 assert a==parse_policy(html.replace('Other program','Changed unrelated policy'),PID)
 assert a['observed_policy_sha256']!=parse_policy(html.replace('CS135 or','CS135 and'),PID)['observed_policy_sha256']
 assert a['requirements']==[] and 'curriculum_audit' not in a
 with pytest.raises(ValueError):parse_policy(html.replace('Minor in AI Development','Other minor'),PID)

def test_third_source_does_not_silently_overrule_checklist():
 from atlas.db import validate_program
 d=json.loads((ROOT/'data/programs'/f'{PID}.json').read_text());validate_program(d)
 assert d['curriculum_status']=='partial'
 assert any('precedence' in x for x in d['curriculum_audit']['unresolved_requirements'])
 assert any('not conclusively accepted' in r['summary'] for r in d['requirements'])
 assert next(s for s in d['sources'] if s['id']=='tufts-ai-minors-launch')['source_date']=='2026-03-25'
