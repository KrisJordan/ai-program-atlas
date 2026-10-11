import hashlib
import json
from pathlib import Path
from collections import Counter
import pytest
from atlas.adapters import ucsd_usp_reviews as m


def fixture(monkeypatch,code='USP 185A',body='A project studio. Prerequisites: prior course and senior standing; department approval.'):
    e=dict(next(x for x in m.SPEC['entries']if x['code']==code));e['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[e]})
    return '<h1>Urban Studies and Planning</h1><p class="course-disclaimer">General Catalog 2026–27</p>'+f'<p class="course-name">{e["heading"]}</p><p class="course-descriptions">{body}</p>'


def test_guarded_observer_does_not_certify_manual_review_or_degree_obligation(monkeypatch):
    h=fixture(monkeypatch);r=m.parse_observations(h);c=r['courses'][0]
    assert c['credits']==4 and c['category']=='applications'
    assert c['prerequisites']=='prior course and senior standing; department approval.'
    assert not {'requirements','category_review','curriculum_audit','course_identity_groups'} & r.keys()
    assert 'category_review'not in c
    for changed in [h.replace('department approval','automatic admission'),h.replace('2026–27','2027–28'),h.replace('USP 185A.','USP 185B.'),h+'<p>New admission rule.</p>',h+'<input type="password">',h+h]:
        with pytest.raises(ValueError):m.parse_observations(changed)


def test_missing_unsuffixed_code_is_not_replaced_by_topics_subcourse(monkeypatch):
    absent=next(e for e in m.SPEC['entries']if e['code']=='USP 165');h=fixture(monkeypatch,'USP 165A')
    monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[absent]})
    assert m.parse_observations(h)['source_dispositions']==[{'code':'USP 165','status':'no_current_heading'}]
    with pytest.raises(ValueError):m.parse_observations(h+'<p class="course-name">USP 165. New course (4)</p>')


def test_manual_content_distinguishes_policy_practice_and_unknown_topics():
    es={e['code']:e for e in m.SPEC['entries']};present=[e for e in es.values()if e['approved_for_integration']]
    assert len(es)==57 and len(present)==53
    assert Counter(e['category']for e in present)=={'human_context':33,'applications':11,'other':9}
    assert Counter(e['credits']for e in present)=={4:47,6:5,8:1}
    assert es['USP 60']['category']=='applications'
    assert es['USP 150']['category']=='human_context'
    assert es['USP 128A']['category_review']['status']=='mixed'
    assert es['USP 194']['category_review']['status']=='unclassified'
    assert all(es['USP '+n]['category_review']['status']=='unclassified'for n in ['165A','165B','165C','165D'])


def test_actual_full_chapter_preserves_all_conditions_and_separate_internship():
    p=Path(m.SPEC['sources']['USP']['cache_path'])
    if not p.exists():pytest.skip('Optional official USP chapter')
    out=m.parse_observations(p.read_text());cs={c['code']:c for c in out['courses']}
    assert len(cs)==53 and len(out['source_dispositions'])==4
    assert 'Restricted to seniors within the Real Estate and Development major' in cs['USP 185A']['prerequisites']
    assert 'major GPA 3.5' in cs['USP 190']['prerequisites']
    assert 'USP 177, USP 177A, or USP 179' in cs['USP 177B']['prerequisites']
    assert cs['USP 194']['credits']==4 and any('separate six-unit' in n for n in cs['USP 194']['notes'])
    assert any('recommended' in n for n in cs['USP 188']['notes'])
    assert cs['USP 144']['prerequisites']is None


def test_integrated_observations_keep_contextual_roles_and_unknown_missing_codes():
    import importlib
    from atlas.curriculum_profile import requirement_profile
    d=json.loads(Path('data/programs',m.SPEC['program_id']+'.json').read_text())
    cs={c['code']:c for c in d['courses']}
    assert [requirement_profile(d)[k]['count']for k in ['required','options','unresolved']]==[8,119,2240]
    assert cs['USP 129']['category_review']['status']=='unclassified'
    assert cs['USP 185A']['category']=='applications'
    assert 'Restricted to seniors' in cs['USP 185A']['prerequisites']
    p=Path(m.SPEC['sources']['USP']['cache_path'])
    if not p.exists():pytest.skip('Optional official USP chapter')
    a=importlib.import_module('atlas.adapters.'+m.SPEC['program_id']+'.adapter')
    observed=a.SOURCE_PARSERS[m.SPEC['sources']['USP']['url']](p.read_text())
    assert len(observed['courses'])==61
    assert all(cs[c['code']][key]==value for c in observed['courses']for key,value in c.items()if key!='notes')
