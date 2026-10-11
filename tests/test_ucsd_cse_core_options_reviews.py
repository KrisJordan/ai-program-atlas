import hashlib
import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_cse_core_options_reviews as m


def test_cse_observation_guard_retains_optional_preparation(monkeypatch):
    e=dict(m.SPEC['entries'][0]);body='Advanced structures. Recommended preparation: C++. Prerequisites: prior study; restricted enrollment.'
    e['description_hash']=hashlib.sha256(body.encode()).hexdigest();monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[e]})
    html='<h1>Computer Science and Engineering (CSE)</h1><p class="course-disclaimer">2026–27</p><p class="course-name">'+e['heading']+'</p><p>'+body+'</p>'
    c=m.parse_observations(html)['courses'][0]
    assert c['category']=='systems'
    assert c['prerequisites']=='prior study; restricted enrollment. Recommended preparation (not a prerequisite): C++.'
    assert 'category_review'not in c
    with pytest.raises(ValueError):m.parse_observations(html.replace('restricted enrollment','unrestricted enrollment'))


def test_actual_core_options_compose_with_remaining_cse_and_tags():
    s=m.SPEC['sources']['CSE'];p=Path(s['cache_path'])
    if not p.exists():pytest.skip('Optional ignored CSE chapter')
    a=importlib.import_module('atlas.adapters.'+m.SPEC['program_id']+'.adapter')
    r=a.SOURCE_PARSERS[s['url']](p.read_text());cs={c['code']:c for c in r['courses']}
    assert len(cs)==90
    assert cs['CSE 100']['category']=='systems' and cs['CSE 150A']['category']=='ai_ml'
    assert 'Recommended preparation (not a prerequisite)' in cs['CSE 100']['prerequisites']
    assert 'All other students will be allowed as space permits' in cs['CSE 150A']['prerequisites']
    assert 'requirements'in r and r['requirements']
    assert all('category_review'not in c for c in cs.values())
