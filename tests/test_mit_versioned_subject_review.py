import hashlib
import importlib
import json
from pathlib import Path

m=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.reviewed_subjects')


def test_changed_annotation_or_identity_does_not_reuse_review(monkeypatch):
    annotation='6.1800 Computer Systems Engineering Prereqs: 6.1910 Units: 5-1-6 Systems design.'
    monkeypatch.setattr(m,'SUBJECTS',{'6.1800':dict(name='Computer Systems Engineering',category='systems',annotation_digest=hashlib.sha256(annotation.encode()).hexdigest())})
    c=dict(code='6.1800',name='Computer Systems Engineering',category='other')
    m.classify(c,annotation);assert c['category']=='systems'and'category_review'not in c
    m.classify(c,annotation+' Changed.');assert c['category']=='other'
    c['name']='Different subject';m.classify(c,annotation);assert c['category']=='other'


def test_versioned_subjects_distinguish_computation_physical_engineering_and_social_analysis():
    from atlas.db import validate_program
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text());validate_program(p)
    by={c['code']:c for c in p['courses']if c['id'].startswith('mit-ai-v2025-')}
    assert by['18.404']['category']=='foundations'
    assert by['6.1200']['category']=='mathematics'
    assert by['6.1800']['category']=='systems'
    assert by['6.1850']['category']=='human_context'
    assert by['6.2000']['category']=='applications'
    assert by['6.1060']['category_review']['status']=='mixed'
    assert by['21M.589']['name']is None and by['21M.589']['category_review']['status']=='unclassified'
    assert by['6.1800']['credits']is None  # source unit triplet remains unconverted
    assert all('category_review'not in c for c in p['courses']if c['id']=='mit-ai-6-1800')
