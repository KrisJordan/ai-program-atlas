import copy
import hashlib
import json
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from atlas.adapters import northeastern_international_social_reviews as m
from atlas.adapters import northeastern_international_affairs_reviews as prior
from atlas.adapters.northeastern_courseleaf import clean

PID='northeastern-university-artificial-intelligence-and-international-affairs-bs-boston-bs-degree'


def test_exact_review_scope_and_manual_identity_evidence():
    assert len(m.SPEC['courses'])==31
    assert sum(len(c['targets']) for c in m.SPEC['courses'].values())==31
    assert all(c['category']=='human_context' for c in m.SPEC['courses'].values())
    seed=json.loads(Path('data/programs',PID+'.json').read_text())
    source_ids={s['id'] for s in seed['sources']};course_ids={c['id'] for c in seed['courses']}
    assert len(m.SPEC['manual_identity_groups'])==3
    seen=set()
    for group,evidence in zip(m.SPEC['manual_identity_groups'],m.SPEC['identity_evidence']):
        assert set(group['source_ids'])<=source_ids
        assert set(group['course_ids'])<=course_ids
        assert not seen.intersection(group['course_ids'])
        seen.update(group['course_ids'])
        a,b=evidence['codes']
        assert evidence['block_digests']==[prior.SPEC['courses'][a]['block_digest'],m.SPEC['courses'][b]['block_digest']]
    assert not any('pols-3100' in cid for g in m.SPEC['manual_identity_groups'] for cid in g['course_ids'])
    assert not any('pols-3406' in cid for g in m.SPEC['manual_identity_groups'] for cid in g['course_ids'])


def test_guarded_additional_eligibility_and_no_runtime_identity_audit(monkeypatch):
    block='<div class="courseblock"><p class="courseblocktitle">POLS 3423. Synthetic politics. (4 Hours)</p><p class="cb_desc">Synthetic political inquiry. Permission required for unmet preparation.</p><p class="courseblockextra">Prerequisite(s): A or B with D-</p></div>'
    spec=copy.deepcopy(m.SPEC['courses']['POLS 3423'])
    spec['block_digest']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser')).encode()).hexdigest()
    spec['description_guard']='Synthetic political inquiry.'
    spec['conditions']=[{'kind':'additional_prerequisite','summary':'Permission required for unmet preparation.'}]
    monkeypatch.setitem(m.SPEC['courses'],'POLS 3423',spec)
    def page(b):return '<p>2026-2027 Edition</p><div id="site-title"><h1>'+m.SPEC['sources']['POLS']['heading']+'</h1></div><div id="textcontainer">'+b+'</div>'
    out=m.parse_subject(page(block),program_id=PID,subject='POLS',codes=['POLS 3423'])
    assert out['courses'][0]['prerequisites']=='A or B with D- Permission required for unmet preparation.'
    assert 'category_review' not in out['courses'][0]
    assert 'course_identity_groups' not in out and 'manual_identity_groups' not in out
    for bad in [block.replace('D-','C-'),block.replace('4 Hours','3 Hours'),block.replace('inquiry.','unrelated.'),block+block,'']:
        with pytest.raises(ValueError):m.parse_subject(page(bad),program_id=PID,subject='POLS',codes=['POLS 3423'])


def actual(subject, module=m):
    path=Path('.cache/http')/(hashlib.sha256(module.SOURCES[subject].encode()).hexdigest()+'.body')
    if not path.exists():pytest.skip('Ignored actual source cache unavailable')
    return path.read_text()


def test_actual_blocks_and_reciprocal_aliases_keep_eligibility():
    courses={};notes=[]
    for subject in m.SOURCES:
        out=m.parse_subject(actual(subject),program_id=PID,subject=subject)
        courses.update({c['code']:c for c in out['courses']});notes+=out['notes']
    assert len(courses)==31 and all(c['credits']==4 for c in courses.values())
    assert 'International Student and Scholar Institute' in courses['JRNL 5360']['prerequisites']
    assert 'Permission of instructor' in courses['POLS 3423']['prerequisites']
    assert any('Graduate awards do not apply' in n for n in notes)
    assert any('No prior knowledge of law' in n for n in notes)
    assert courses['ANTH 3442']['prerequisites'] is not None
    earlier=prior.parse_subject(actual('INTL',prior),program_id=PID,subject='INTL')
    old={c['code']:c for c in earlier['courses']}
    for e in m.SPEC['identity_evidence']:
        a,b=e['codes']
        left=next(n for n in earlier['notes'] if n.startswith(a))
        right=next(n for n in notes if n.startswith(b))
        assert a in left and b in left and a in right and b in right
    assert old['INTL 4500']['prerequisites']!=courses['ANTH 4500']['prerequisites']
