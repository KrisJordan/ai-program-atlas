import copy,hashlib,json
from pathlib import Path
from collections import Counter
import pytest
from atlas.adapters import northeastern_business_remaining_reviews as m


def source(subject):
    path=Path('.cache/http')/(hashlib.sha256(m.SOURCES[subject].encode()).hexdigest()+'.body')
    if not path.exists():pytest.skip('Ignored actual source capture unavailable')
    return path.read_text()


def test_all_65_actual_target_observations_preserve_reviewed_identity_and_conditions():
    count=0
    for subject in m.SOURCES:
        pids={t['program_id'] for e in m.SPEC['courses'].values() if e['subject']==subject for t in e['targets']}
        for pid in pids:
            result=m.parse_subject(source(subject),program_id=pid,subject=subject)
            for c in result['courses']:
                entry=m.SPEC['courses'][c['code']]
                assert (c['name'],c['category'],c['credits'])==(entry['name'],entry['category'],entry['credits'])
                assert 'category_review' not in c
            assert result['requirements']==[]
            count+=len(result['courses'])
    assert count==65


def test_variable_zero_hours_and_explicit_preparation_are_not_guessed():
    pid=next(t['program_id'] for t in m.SPEC['courses']['BUSN 4945']['targets'])
    busn=m.parse_subject(source('BUSN'),program_id=pid,subject='BUSN')
    assert next(c for c in busn['courses'] if c['code']=='BUSN 4945')['credits'] is None
    coop=m.parse_subject(source('COOP'),program_id=pid,subject='COOP')
    assert all(c['credits']==0 and c['prerequisites']=='Requires sophomore standing or above.' for c in coop['courses'])
    mgmt=m.parse_subject(source('MGMT'),program_id=pid,subject='MGMT')
    assert next(c for c in mgmt['courses'] if c['code']=='MGMT 3305')['prerequisites'] is None
    assert any('explicitly not required' in n for n in mgmt['notes'])
    intb=m.parse_subject(source('INTB'),program_id=pid,subject='INTB')
    assert next(c for c in intb['courses'] if c['code']=='INTB 1209')['category']=='other'
    assert any('does not count' in n.lower() and 'source conflict' in n for n in intb['notes'])


def test_changed_complete_course_block_or_identity_requires_review():
    pid=m.SPEC['courses']['COOP 3945']['targets'][0]['program_id'];html=source('COOP')
    for changed in [html.replace('sophomore standing','junior standing'),html.replace('2026-2027','2027-2028'),html.replace('Cooperative Education (COOP)','Other (COOP)')]:
        with pytest.raises(ValueError):m.parse_subject(changed,program_id=pid,subject='COOP')
    with pytest.raises(ValueError):m.parse_subject(html,program_id='unreviewed-degree',subject='COOP')


def test_data_tools_and_ai_labels_are_classified_from_actual_subject():
    courses=m.SPEC['courses']
    for code,category in [('EECE 2560','foundations'),('ORGB 3203','human_context'),('SCHM 3308','applications'),('MGMT 4550','applications'),('MISM 3515','ai_ml'),('SCHM 4983','other')]:
        assert courses[code]['category']==category and courses[code]['review']['rationale']
