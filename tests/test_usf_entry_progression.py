from importlib import import_module
from pathlib import Path
import hashlib
import json
import pytest
PID='university-of-south-florida-artificial-intelligence-bs-degree'
m=import_module('atlas.adapters.'+PID+'.entry_progression_policies')

def test_changed_entry_or_neighboring_scope_needs_fresh_review():
    review=dict(source_id='test',normalized_sha256=hashlib.sha256(b'AI entry C within two attempts').hexdigest(),rules=[dict(key='entry',title='Entry',summary='Conditional admission only.')])
    html='<main>AI entry C within two attempts</main>'
    out=m.observe(html,review)
    assert out['requirements'][0]['kind']=='note' and not out['requirements'][0]['course_ids']
    assert not {'curriculum_audit','last_verified','courses'} & out.keys()
    for changed in [html.replace('two','three'),html.replace('AI entry','Computer Engineering entry'),'<h1>Access denied</h1>'+html]:
        with pytest.raises(ValueError):m.observe(changed,review)

@pytest.mark.parametrize('review',m.REVIEWS,ids=lambda r:r['name'])
def test_optional_full_public_source_replay(review):
    path=Path('/tmp/usf-policy-'+review['name']+'.html')
    if not path.exists():pytest.skip('Optional private public-page capture absent')
    out=m.observe(path.read_text(),review)
    assert len(out['requirements'])==len(review['rules'])
    assert all(r['kind']=='note' and r['credits'] is None and not r['course_ids'] for r in out['requirements'])

def test_ai_admission_conditions_and_progression_keep_exact_scope():
    p=json.loads((Path('data/programs')/(PID+'.json')).read_text());r={r['id']:r for r in p['requirements']}
    assert '(SAT mathematics at least 570 OR ACT mathematics at least 24) AND' in r['usf-ai-bellini-entry-lower-transfer']['summary']
    assert 'not asserted to be six current USF offerings' in r['usf-ai-bellini-entry-programming-transfer']['summary']
    assert 'do not apply through this AI section' in r['usf-ai-bellini-entry-math-physics-transfer']['summary']
    assert 'includes prior postsecondary enrollment' in r['usf-ai-policy-10-505-additional-work']['summary']
    assert 'After six active postsecondary terms' in r['usf-ai-policy-10-505-six-terms']['summary']
    assert 'before applying to graduate' in r['usf-ai-policy-10-505-exceptions']['summary']
    source=next(s for s in p['sources'] if s['id']=='usf-ai-policy-10-505')
    assert source['source_date']=='2025-05-21' and 'No automated PDF refresh' in source['locator']
    assert p['curriculum_status']=='partial' and len(p['courses'])==29
