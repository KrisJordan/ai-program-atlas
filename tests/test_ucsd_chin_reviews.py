import copy
import hashlib
import json
from pathlib import Path
from collections import Counter
import pytest
from atlas.adapters import ucsd_chin_reviews as m


def fixture(monkeypatch,code='CHIN 198'):
    e=copy.deepcopy(next(e for e in m.SPEC['entries']if e['code']==code))
    body='Selected study. Prerequisites: consent of instructor.'
    e['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[e]})
    return '<h1>Chinese Studies</h1><p class="course-disclaimer">2026–27</p>'+f'<p class="course-name">{e["heading"]}</p><p><span>{body}</span></p>'


def test_variable_units_nested_description_and_fail_closed_guard(monkeypatch):
    h=fixture(monkeypatch);r=m.parse_observations(h);c=r['courses'][0]
    assert c['credits']is None and c['category']=='other'
    assert c['prerequisites']=='consent of instructor.'
    assert not {'category_review','requirements','course_identity_groups'}&r.keys()
    assert 'category_review'not in c
    for altered in [h.replace('consent','automatic permission'),h.replace('2026–27','2027–28'),h.replace('(2 or 4)','(4)'),h+'<p>Additional condition.</p>',h+h]:
        with pytest.raises(ValueError):m.parse_observations(altered)


def test_language_context_does_not_become_medical_or_business_methods():
    es={e['code']:e for e in m.SPEC['entries']}
    assert len(es)==41
    assert Counter(e['category']for e in es.values())=={'human_context':38,'other':3}
    assert Counter(e['credits']for e in es.values())=={4:30,5:9,None:2}
    for code in ['165A','165B','165C','169A','169B','186A','186B','186C']:
        assert es['CHIN '+code]['category']=='human_context'
    assert 'CHIN 186CB' in es['CHIN 186C']['observed_prerequisites']
    assert 'previous course or department approval' in es['CHIN 20BM']['observed_prerequisites']
    assert all(es['CHIN '+c]['category_review']['status']=='unclassified'for c in ['196','198','199'])


def test_actual_chapter_all_records_and_registered_integration():
    import importlib
    from atlas.curriculum_profile import requirement_profile
    s=m.SPEC['sources']['CHIN'];p=Path(s['cache_path'])
    if not p.exists():pytest.skip('Optional Chinese chapter')
    a=importlib.import_module('atlas.adapters.'+m.SPEC['program_id']+'.adapter')
    out=a.SOURCE_PARSERS[s['url']](p.read_text());assert len(out['courses'])==42
    d=json.loads(Path('data/programs',m.SPEC['program_id']+'.json').read_text());cs={c['id']:c for c in d['courses']}
    assert all(cs[c['id']][k]==v for c in out['courses']for k,v in c.items()if k!='notes')
    assert [requirement_profile(d)[k]['count']for k in ['required','options','unresolved']]==[8,119,2240]
    # Preserve prior Warren language membership rules while enriching descriptions.
    assert a.SOURCES.count(s['url'])==1
    assert len(out['requirements'])==43
    assert any('160-260' in r['id']and not r['course_ids']for r in out['requirements'])
