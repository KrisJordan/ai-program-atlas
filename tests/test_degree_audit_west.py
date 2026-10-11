"""Independent source-specific role/category checks for the western degree audit."""
import importlib
import json
from collections import Counter
from pathlib import Path

from atlas.curriculum_profile import requirement_profile


def program(pid):
    return json.loads(Path('data/programs',pid+'.json').read_text())


def assert_partition(d, fixed, options, unresolved):
    assert fixed.isdisjoint(options) and fixed.isdisjoint(unresolved) and options.isdisjoint(unresolved)
    assert fixed|options|unresolved=={c['id']for c in d['courses']}
    observed=requirement_profile(d)
    for key,ids in [('required',fixed),('options',options),('unresolved',unresolved)]:
        counts=Counter(c['category']for c in d['courses']if c['id']in ids)
        assert observed[key]['count']==len(ids)
        assert {k:v for k,v in observed[key]['categories'].items()if v}==dict(counts)


def test_wpi_ai_source_named_foundation_sequence_is_fixed():
    d=program('wpi-ai-bs')
    # Independently named mandatory algorithm, statistics pair and DS triple.
    fixed={'wpi-cs-2223','wpi-ma-2611','wpi-ma-2612','wpi-ds-1010','wpi-ds-2010','wpi-ds-3010'}
    unresolved={'wpi-hu-3900','wpi-hu-3910'}
    options={c['id']for c in d['courses']}-fixed-unresolved
    assert_partition(d,fixed,options,unresolved)
    core=next(r for r in d['requirements']if r['id']=='wpi-ai-bs-core')
    assert core['kind']=='all' and core['course_ids']==[]
    total=next(r for r in d['requirements']if r['id']=='wpi-ai-bs-core-selection-total')
    assert 'not 8/3 additional' in total['summary']


def test_wpi_business_known_optional_pool_is_not_unresolved():
    d=program('wpi-business-analytics-applied-ai-bs')
    unresolved={'wpi-hu-3900','wpi-hu-3910'}
    assert_partition(d,set(),{c['id']for c in d['courses']}-unresolved,unresolved)
    pool=next(r for r in d['requirements']if r['id']==d['id']+'-electives')
    assert {'wpi-etr-1100','wpi-mis-3010'}<=set(pool['course_ids'])
    assert pool['count']==6


def test_wpi_subjects_are_independent_of_ai_degree_membership():
    for pid in ['wpi-ai-bs','wpi-business-analytics-applied-ai-bs']:
        d=program(pid);courses={c['code']:c for c in d['courses']}
        assert courses['MA 1021']['category']=='mathematics'
        assert courses['CS 2119']['category']=='foundations'
        assert courses['ACC 2060']['category']=='applications'
        assert courses['CS 4342']['category']=='ai_ml'
        assert courses['DS 1010']['category']=='other'
        assert courses['DS 1010']['category_review']['status']=='mixed'
        assert all(c['category_review']['source_ids'] for c in d['courses'])
        assert sum(c['category']=='ai_ml'for c in d['courses'])<30
    from atlas.adapters.wpi_degree_subjects import observe
    result=observe(lambda: {'courses':[{'code':'MA 1021','name':'Changed unidentified course','category':'ai_ml','category_review':{'stale':True}}]})()
    assert result['courses'][0]['category']=='other' and 'category_review'not in result['courses'][0]
