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


def test_corrected_degree_subjects_do_not_follow_required_or_option_role():
    u = program('university-of-california-san-diego-artificial-intelligence-bs-degree')
    courses = {c['code']: c for c in u['courses']}
    assert courses['CSE 101']['category'] == 'foundations'
    assert courses['CSE 30']['category'] == 'systems'
    assert courses['CSE 12']['credits'] == courses['CSE 30']['credits'] == 4
    assert courses['MATH 20A']['category'] == courses['MATH 20B']['category'] == 'mathematics'
    assert all(c['category'] == 'other' for c in u['courses'] if c['name'] is None and c['description'] is None)
    b = {c['code']: c for c in program('ucsb-ai-bs')['courses']}
    assert b['CMPSC 130A']['category'] == b['CMPSC 130B']['category'] == 'foundations'
    assert b['CMPSC 183']['category'] == 'human_context'
    assert b['ECE 139']['category'] == 'mathematics'
    assert b['CMPSC 41']['credits'] is None  # source conflict remains
    p = program('purdue-ai-bs')
    assert all(c['category'] == 'other' for c in p['courses'] if '-pool-' in c['id'])
    ba = {c['code']: c for c in program('purdue-ai-ba')['courses']}
    assert ba['CS 10100']['category_review']['status'] == 'mixed'
    assert ba['CS 18200']['category_review']['status'] == 'mixed'
    assert all(c['credits'] is None for c in ba.values())


def test_source_observations_drop_stale_reviews_and_changed_titles():
    from atlas.adapters.west_degree_subjects import observe
    result = observe(lambda: {'courses': [{'code': 'CSE 101', 'name': 'Different subject',
                      'category': 'ai_ml', 'category_review': {'stale': True}}]},
                      'university-of-california-san-diego-artificial-intelligence-bs-degree')()
    assert result['courses'][0]['category'] == 'other'
    assert 'category_review' not in result['courses'][0]


def test_purdue_source_grade_and_transfer_rules_do_not_add_prerequisite_courses():
    import pytest
    m = importlib.import_module('atlas.adapters.purdue-ai-bs.adapter')
    html = '''<p>all major required courses; all major electives (selectives); their pre-requisites, regardless of department; grade of C or better.
    100 and 200 level core courses before the student enters; 300 or 400 level CS coursework; pre-approved Study Abroad coursework.
    Graduate courses: additional prerequisites that must be met to be eligible.</p>'''
    result = m.parse_major_policies(html)
    assert len(result['requirements']) == 3
    assert all(r['kind'] == 'note' and not r['course_ids'] for r in result['requirements'])
    with pytest.raises(ValueError):
        m.parse_major_policies(html.replace('C or better', 'D or better'))


def test_ucsd_noncourse_ahi_routes_and_transfer_climate_exemption_remain_contextual():
    d = program('university-of-california-san-diego-artificial-intelligence-bs-degree')
    nodes = {r['id']: r for r in d['requirements']}
    assert nodes[d['id']+'-shared-ahi-pool']['parent_id'] == d['id']+'-policy-ahi'
    assert nodes[d['id']+'-shared-climate-pool']['parent_id'] == d['id']+'-shared-climate-scope'
    profile = requirement_profile(d)
    assert profile['required']['count'] == 8
    assert profile['options']['count'] == 119
    assert profile['unresolved']['count'] == 2241
    assert all(c['context'] == 'unresolved' for c in profile['choices']
               if c['id'] in [d['id']+'-shared-ahi-pool', d['id']+'-shared-climate-pool'])


def test_fixed_ucsd_calculus_parser_reads_actual_values_and_prerequisite_logic():
    import pytest
    m = importlib.import_module('atlas.adapters.university-of-california-san-diego-artificial-intelligence-bs-degree.course_metadata')
    html = '<h1>Mathematics</h1>' + ''.join(
        f'<p class="course-name">MATH 20{suffix}. Synthetic calculus (5)</p><p>Synthetic content.</p><p>Prerequisites: A or B with C–.</p>'
        for suffix in ['A', 'B'])
    result = m.parse_math(html)
    assert {c['credits'] for c in result['courses']} == {5}
    assert all(c['prerequisites'] == 'A or B with C–.' for c in result['courses'])
    assert 'requirements' not in result
    with pytest.raises(ValueError):
        m.parse_math(html.replace('MATH 20B.', 'MATH 20C.'))


def test_eight_degree_ledger_has_independent_partitions_and_honest_blockers():
    ledger = json.loads(Path('research/degree-audit/west-purdue-wpi.json').read_text())
    assert len(ledger['programs']) == 8
    for audit in ledger['programs']:
        assert audit['blockers']
        expected_status = 'blocked' if audit['program_id'] in ['uc-merced-ai-bs', 'furman-ai-bs', 'wpi-business-analytics-applied-ai-bs', 'wpi-ai-bs'] else 'in_progress'
        assert audit['status'] == expected_status
        if expected_status == 'in_progress':
            assert 'accessible' in audit['accessible_work_remaining']
        assert audit['second_pass_status'] == 'pending'
        assert set(audit['checks']) == {'degree_identity', 'required_and_choices', 'elective_pools',
            'prerequisites', 'credits_and_units', 'classification', 'family_composition', 'degree_wide_requirements'}
        if audit['expected_profile'] is None:
            assert audit['program_id'] in ['uc-merced-ai-bs', 'furman-ai-bs']
            continue
        d = program(audit['program_id'])
        ids = audit['expected_course_ids']
        assert_partition(d, set(ids['required']), set(ids['options']), set(ids['unresolved']))
        for role, course_ids in ids.items():
            assert audit['expected_profile'][role]['count'] == len(course_ids)
            expected = Counter(c['category'] for c in d['courses'] if c['id'] in course_ids)
            assert audit['expected_profile'][role]['categories'] == dict(expected)
