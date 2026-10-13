"""Limited exact-title judgments cannot become fabricated descriptions or roles."""
from copy import deepcopy
import importlib
import json
from pathlib import Path

import pytest

from atlas.adapters.maryland_catalog_subjects import SPEC, observe
from atlas.curriculum_profile import requirement_profile
from atlas.degree_audit import core_review_fingerprint
from atlas.site import required_directory_counts

BA='university-of-maryland-college-park-human-centered-ai-ba-degree'
BS='university-of-maryland-college-park-artificial-intelligence-computational-structures-for-ai-systems-bsai-degree'


def program(pid):
    return json.loads(Path('data/programs',pid+'.json').read_text())


def test_named_ba_core_has_bounded_subjects_and_unchanged_roles():
    p=program(BA);c={c['code']:c for c in p['courses']}
    expected={'HCAI100':'human_context','HCAI120':'foundations','HCAI121':'foundations','HCAI200':'foundations','HCAI300':'ai_ml','HCAI301':'ai_ml'}
    for code,category in expected.items():
        assert c[code]['category']==category
        assert c[code]['description'] is None
        assert c[code]['category_review']['status']=='reviewed'
        assert 'Moderate-confidence' in c[code]['category_review']['rationale']
        assert 'Full current exact course description remains unavailable' in c[code]['category_review']['rationale']
    profile=requirement_profile(p,include_course_ids=True)
    assert profile['required']['count']==10 and profile['options']['count']==59 and profile['unresolved']['count']==52
    assert profile['required']['categories']==dict(foundations=3,mathematics=1,ai_ml=2,systems=0,human_context=4,applications=0,electives=0,other=0)
    assert 'umd-hcai490' in profile['course_ids']['options']
    assert c['HCAI410']['category_review']['status']=='unclassified'
    assert c['INST431']['category_review']['status']=='unclassified'
    assert required_directory_counts(p)==dict(mathematics=1,computing_systems=3,ai_ml=2,human_context=4,applications=0,other=0)


def test_bs_choices_and_programming_projects_do_not_become_fixed_ai_courses():
    p=program(BS);c={c['code']:c for c in p['courses']}
    profile=requirement_profile(p,include_course_ids=True)
    assert profile['required']['count']==6 and profile['options']['count']==79
    for code in ['CMSC141','CMSC142','CMSC425','CMSC427']:
        assert c[code]['category']=='foundations'
        assert 'umd-'+code.lower() in profile['course_ids']['options']
    for code in ['CSAI221','CSAI427']:assert c[code]['category']=='ai_ml'
    assert c['CSAI216']['category']=='systems'
    assert c['CMSC425']['description'] and c['CMSC427']['description']
    assert c['CMSC320']['category_review']['status']=='mixed'
    assert c['STAT426']['category_review']['status']=='mixed'
    assert c['CSAI432']['category_review']['status']=='unclassified'
    assert c['CSAI473']['category_review']['status']=='unclassified'
    assert required_directory_counts(p)==dict(mathematics=4,computing_systems=4,ai_ml=1,human_context=2,applications=0,other=1)
    assert profile['required_obligations']['count']==12  # six fixed and six safely counted mandatory choices


def test_exact_whitelist_is_not_an_ai_keyword_classifier_or_review_replay():
    rows=[dict(code='HCAI120',name=SPEC['HCAI120']['name'],category='other',category_review={'stale':True}),
          dict(code='HCAI120',name='Different AI course',category='other'),
          dict(code='UNKNOWN100',name='Artificial Intelligence',category='other')]
    before=deepcopy(rows)
    result=observe(lambda: {'courses':deepcopy(rows)})()['courses']
    assert result[0]['category']=='foundations'
    assert 'category_review' not in result[0] and 'description' not in result[0]
    assert result[1]['category']==result[2]['category']=='other'
    assert rows==before


@pytest.mark.parametrize('pid,name',[(BA,'ba'),(BS,'bsai')])
def test_optional_actual_catalog_replay_preserves_manual_review_boundary(pid,name):
    path=Path('.cache/research/umd-oct13',name+'.html')
    if not path.exists():pytest.skip('Optional ignored current official source capture unavailable')
    module=importlib.import_module('atlas.adapters.'+pid+'.adapter')
    first=module.parse(path.read_text());second=module.parse(path.read_text())
    assert first==second
    assert 'last_verified' not in first and 'curriculum_audit' not in first
    for c in first['courses']:
        assert 'category_review' not in c
        if c['code'] in SPEC and c['name']==SPEC[c['code']]['name']:
            assert c['category']==SPEC[c['code']]['category']


def test_required_profile_sources_pin_new_judgments_without_promoting_independent_scope():
    rows=json.loads(Path('research/degree-audit/independent-core-other.json').read_text())['programs']
    for pid in [BA,BS]:
        row=next(r for r in rows if r['program_id']==pid)
        assert row['reviewed_content_hash']==core_review_fingerprint(program(pid))
        assert row['dimensions']['fixed_requirements']['status']=='verified'
        assert row['dimensions']['classification']['status']=='partial'
        assert row['expected_profile']['options']['categories'] is None
        assert not row['full_degree_verified']
        assert 'independent acceptance' in row['classification_followup']['scope']
