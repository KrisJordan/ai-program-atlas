import importlib
import json
from pathlib import Path

m=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.reference_subjects')


def test_exact_reference_identity_and_title_required():
    c=dict(id='mit-ai-6-1210',name='Introduction to Algorithms',category='other')
    m.observe([c]);assert c['category']=='foundations'and'category_review'not in c
    c['name']='Introduction to something else';m.observe([c]);assert c['category']=='other'
    other=dict(id='different-source-6-1210',name='Introduction to Algorithms',category='other')
    m.observe([other]);assert other['category']=='other'


def test_title_observation_remains_limited_when_dated_metadata_is_separate():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text());by={c['id']:c for c in p['courses']}
    assert m.REVIEWS['mit-ai-6-3260-j']['category']=='other'
    assert by['mit-ai-6-3260-j']['category']=='mathematics'
    assert by['mit-ai-v2025-6-3260']['category']=='mathematics'
    assert by['mit-ai-6-5931']['category']=='systems'
    assert 'Bounded dated annotation review.'in by['mit-ai-6-5931']['category_review']['rationale']
    assert by['mit-ai-6-5931']['description']
    assert by['mit-ai-6-5931']['source_id']!=by['mit-ai-v2025-6-5931']['source_id']
    assert set(by['mit-ai-6-5931']['category_review']['source_ids'])=={by['mit-ai-6-5931']['source_id'],'mit-ai-decision-making-bs-versioned'}
    assert len(m.REVIEWS)==63 and sum(r['category']!='other'for r in m.REVIEWS.values())==39
