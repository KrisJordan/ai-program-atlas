import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_cgs_reviews as m


def test_technology_and_science_themes_are_classified_from_actual_purpose():
    es={e['code']:e for e in m.SPEC['entries']}
    assert len(es)==24 and all(e['category']=='human_context'for e in es.values())
    assert 'no model-building' in es['CGS 108']['category_review']['rationale']
    assert 'not the scientific methods' in es['CGS 135']['category_review']['rationale']
    assert 'natural-science' in es['CGS 100B']['category_review']['rationale']


def test_source_block_and_edition_guard_without_review_replay(monkeypatch):
    e=dict(next(e for e in m.SPEC['entries']if e['code']=='CGS 137'));body='Cultural analysis. May repeat for credit. Prerequisites: permission.'
    e['description_hash']=hashlib.sha256(body.encode()).hexdigest();monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[e]})
    html='<h1>Critical Gender Studies</h1><p class="course-disclaimer">2026–27</p><p class="course-name">'+e['heading']+'</p><p>'+body+'</p>'
    r=m.parse_observations(html);assert r['courses'][0]['prerequisites']=='permission.'
    assert 'category_review'not in r['courses'][0]and'course_identity_groups'not in r
    for x in [html.replace('permission','no permission'),html.replace('2026–27','2027–28'),html+'<p>New credit restriction.</p>']:
        with pytest.raises(ValueError):m.parse_observations(x)


def test_actual24_blocks_preserve_credit_and_prerequisite_expressions():
    p=Path(m.SPEC['sources']['CGS']['cache_path'])
    if not p.exists():pytest.skip('Optional ignored current chapter')
    r=m.parse_observations(p.read_text());cs={c['code']:c for c in r['courses']}
    assert len(cs)==24 and not r['source_dispositions']
    assert all(c['credits']==4 for c in cs.values())
    assert cs['CGS 108']['prerequisites']is None
    assert cs['CGS 100A']['prerequisites']=='CGS 2A-B or at least one CGS upper-division course.'
    assert 'combined total of twelve units' in cs['CGS 137']['prerequisites']
    assert any('CGS 115' in n for n in cs['CGS 187']['notes'])
