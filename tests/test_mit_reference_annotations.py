"""Separate dated metadata must not silently merge chart and versioned roles."""
import copy
import importlib
import json
from pathlib import Path

import pytest

m = importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.reference_annotations')
v = importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.versioned')
a = importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.adapter')


def fixture(cid='mit-ai-6-1210'):
    r=m.REVIEWS[cid]
    c=dict(id='observed',code=r['observed_code'],name=r['observed_name'],
           prerequisites='Prereqs: 6.1010 and 6.1200',credits=12,credit_unit='units',
           source_id='mit-ai-decision-making-bs-versioned',url=a.policies.EMBEDDED)
    return dict(courses=[c],observed_core_description_digests={'observed':r['annotation_digest']})


def test_exact_annotation_is_supplemental_observation_not_certification():
    result=m.observe(fixture())
    assert len(result)==1
    c=result[0]
    assert c['id']=='mit-ai-6-1210' and c['description']
    assert c['prerequisites']=='Prereqs: 6.1010 and 6.1200'
    assert c['source_id']=='mit-ai-decision-making-bs-versioned'
    assert 'category_review'not in c and 'curriculum_audit'not in c
    assert any('does not supersede'in n for n in c['notes'])


@pytest.mark.parametrize('change',['code','title','body','missing_digest'])
def test_changed_evidence_cannot_replay_old_description(change):
    p=fixture()
    if change=='code':p['courses'][0]['code']='6.1211'
    if change=='title':p['courses'][0]['name']='Different subject'
    if change=='body':p['observed_core_description_digests']['observed']='changed'
    if change=='missing_digest':p['observed_core_description_digests']={}
    assert m.observe(p)==[]


def test_conflicting_reference_credit_and_unmatched_titles_stay_withheld():
    cid=next(cid for cid,r in m.REVIEWS.items()if r['observed_code']=='6.4300')
    p=fixture(cid);p['courses'][0]['credits']=15
    assert m.observe(p)[0]['credits']is None
    assert not {'6.8301','6.9030'} & {r['observed_code']for r in m.REVIEWS.values()}
    assert len(m.REVIEWS)==61


def test_source_replay_preserves_requirements_and_versioned_identities():
    path=Path('/tmp/pilot-audit-mit-version.html')
    if not path.exists():pytest.skip('Optional ignored official source capture absent')
    html=path.read_text();base=v.parse(html);observed=a.SOURCE_PARSERS[a.policies.EMBEDDED](html)
    assert len(base['courses'])==261 and len(observed['courses'])==322
    assert observed['requirements']==base['requirements']
    assert all('category_review'not in c for c in observed['courses'])
    actual={c['id']:c for c in observed['courses']}
    seed=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    for c in seed['courses']:
        if c['id']not in m.REVIEWS:continue
        for field in ('code','name','description','prerequisites','credits','category'):
            assert c[field]==actual[c['id']][field],(c['id'],field)
        assert c['source_id']in c['category_review']['source_ids']
        assert 'mit-ai-decision-making-bs-versioned'in c['category_review']['source_ids']
    # Change an actual annotation, retaining title and all page/table structure.
    changed=html.replace('Introduces fundamental concepts of programming.', 'Changed course body.')
    assert changed!=html
    result=a.SOURCE_PARSERS[a.policies.EMBEDDED](changed)
    assert 'mit-ai-6-1010'not in {c['id']for c in result['courses']}
