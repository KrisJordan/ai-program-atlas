import hashlib
import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import purdue_science_policy_reviews as m
from atlas.curriculum_profile import requirement_profile


def test_purdue_policy_context_preserves_roles_and_conditional_limits():
    d=json.loads(Path('data/programs/purdue-ai-bs.json').read_text())
    r={x['id']:x for x in d['requirements']}
    notes=[r['purdue-ai-bs-policy-'+n['suffix']]for s in m.SPEC['sources'].values()for n in s['notes']]
    assert len(notes)==15
    assert all(n['kind']=='note' and not n['course_ids'] and n['credits'] is None for n in notes)
    assert [requirement_profile(d)[k]['count']for k in ('required','options','unresolved')]==[9,140,1684]
    assert 'Only for Spring 2020' in r['purdue-ai-bs-policy-pass-not-pass-spring-2020']['summary']
    assert '5000-level' in r['purdue-ai-bs-policy-pass-not-pass-scope']['summary']
    assert 'year-round' in r['purdue-ai-bs-policy-math-exam-delivery']['summary']
    ledger=json.loads(Path('research/degree-audit/west-purdue-wpi.json').read_text())
    audit=next(x for x in ledger['programs']if x['program_id']==d['id'])
    assert audit['status']=='blocked'
    assert audit['accessible_work_remaining'].startswith('No identified unread source')
    assert d['curriculum_status']=='partial'


@pytest.mark.parametrize('key',tuple(m.SPEC['sources']))
def test_registered_policy_observation_matches_saved_note(key):
    s=m.SPEC['sources'][key]
    p=Path('.cache/research/purdue-science-policy')/(hashlib.sha256(s['url'].encode()).hexdigest()+'.body')
    if not p.exists():pytest.skip('Optional public policy cache')
    a=importlib.import_module('atlas.adapters.purdue-ai-bs.adapter')
    assert s['url'] in a.SOURCES
    out=a.SOURCE_PARSERS[s['url']](p.read_text())
    saved={x['id']:x for x in json.loads(Path('data/programs/purdue-ai-bs.json').read_text())['requirements']}
    assert all(saved[x['id']]==x for x in out['requirements'])
    assert set(out)=={'id','requirements'}
