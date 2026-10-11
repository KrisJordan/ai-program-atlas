import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_biology_reviews as m


def test_block_and_chapter_policies_are_guarded(monkeypatch):
    e=dict(next(e for e in m.SPEC['entries']if e['code']=='BICD 136'));body='HIV science and society. Prerequisites: BILD 1, BILD 2 recommended.'
    e['description_hash']=hashlib.sha256(body.encode()).hexdigest();monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[e]})
    html='<h1>'+m.SPEC['sources']['BIOL']['heading']+'</h1><p class="course-disclaimer">2026–27</p>'+''.join('<p>'+p+'</p>'for p in m.SPEC['chapter_policies'])+'<p class="course-name">'+e['heading']+'</p><p>'+body+'</p>'
    out=m.parse_observations(html);assert out['courses'][0]['prerequisites']=='BILD 1, BILD 2 recommended.'
    assert 'category_review'not in out['courses'][0]and'requirements'not in out
    for altered in [html.replace('strictly enforced','not enforced'),html.replace('BILD 2 recommended','BILD 2 required'),html+'<p>New requirement.</p>']:
        with pytest.raises(ValueError):m.parse_observations(altered)


def test_actual_biology_blocks_units_and_scope():
    p=Path(m.SPEC['sources']['BIOL']['cache_path'])
    if not p.exists():pytest.skip('Optional ignored Biology capture')
    out=m.parse_observations(p.read_text());cs={c['code']:c for c in out['courses']}
    assert len(cs)==34 and {d['code']for d in out['source_dispositions']}=={'BILD 51','BIEB 131','BIEB 165'}
    assert cs['BISP 182']['credits']is None and cs['BISP 193']['credits']is None
    assert sum(c['credits']==4 for c in cs.values())==32
    assert cs['BICD 136']['prerequisites']=='BILD 1, BILD 2 recommended.'
    assert any('P/PN' in n for n in cs['BISP 193']['notes'])
    assert any('Open to nonbiology majors only' in n for n in cs['BILD 10']['notes'])
    assert not any('lab-specific' in n for n in cs['BILD 10']['notes'])
    assert any('lab-specific' in n for n in cs['BIEB 121']['notes'])
    assert all(any('strictly enforces' in n for n in c['notes'])for c in cs.values())
    assert cs['BILD 60']['category']=='human_context'
    assert cs['BILD 5']['category']=='applications'
