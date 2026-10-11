import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from atlas.adapters import northeastern_communication_course_reviews as m
from atlas.adapters.northeastern_courseleaf import clean
from atlas.curriculum_profile import requirement_profile
from atlas.families import resolve_program

PID = m.SPEC['degree_review']['program_id']


def synthetic(monkeypatch):
    block = '<div class="courseblock"><p class="courseblocktitle">COMM 1101. Synthetic inquiry. (4 Hours)</p><p class="cb_desc">Synthetic communication inquiry.</p><p class="courseblockextra">Prerequisite(s): A or B with C-</p></div>'
    entry = copy.deepcopy(m.SPEC['courses']['COMM 1101'])
    entry['block_digest'] = hashlib.sha256(clean(BeautifulSoup(block, 'html.parser')).encode()).hexdigest()
    entry['description_guard'] = 'Synthetic communication inquiry.'
    monkeypatch.setitem(m.SPEC['courses'], 'COMM 1101', entry)
    def page(b):
        return '<p>2026-2027 Edition</p><div id="site-title"><h1>'+m.SPEC['sources']['COMM']['heading']+'</h1></div><div id="textcontainer">'+b+'</div>'
    return block, page


def test_guarded_observation_does_not_certify_review(monkeypatch):
    block, page = synthetic(monkeypatch)
    result = m.parse_subject(page(block), program_id=PID, subject='COMM', codes=['COMM 1101'])
    c = result['courses'][0]
    assert c['prerequisites'] == 'A or B with C-'
    assert c['credits'] == 4 and c['credit_unit'] == 'semester_hours'
    assert 'category_review' not in c and 'curriculum_audit' not in result
    assert result['requirements'] == []
    for bad in [block.replace('inquiry.', 'unrelated.'), block.replace('4 Hours', '3 Hours'), block.replace('C-', 'B-'), block+block, '']:
        with pytest.raises(ValueError):
            m.parse_subject(page(bad), program_id=PID, subject='COMM', codes=['COMM 1101'])
    for bad in [page(block).replace('2026-2027', '2025-2026'), '<h1>Login</h1>']:
        with pytest.raises(ValueError):
            m.parse_subject(bad, program_id=PID, subject='COMM', codes=['COMM 1101'])
    with pytest.raises(ValueError, match='outside reviewed'):
        m.parse_subject(page(block), program_id='unreviewed', subject='COMM', codes=['COMM 1101'])


def test_manual_scope_and_source_specific_choices():
    entries = m.SPEC['courses']
    assert len(entries) == 35 and sum(len(e['targets']) for e in entries.values()) == 40
    assert Counter(e['subject'] for e in entries.values()) == {'COMM':32,'MSCR':1,'PREL':2}
    assert Counter(e['category'] for e in entries.values()) == {'human_context':34,'other':1}
    assert entries['COMM 1000']['review']['status'] == 'unclassified'
    assert entries['COMM 2941']['conditions'][0]['summary'] == 'May be repeated once.'
    assert 'statistical theory' in entries['COMM 2301']['review']['rationale']
    assert 'JRNL 3425' in entries['PREL 3625']['prerequisites']
    assert entries['COMM 2304']['conditions'][0]['kind'] == 'crosslist_observation'


def test_independent_source_role_sets_against_resolved_graph():
    seed = json.loads(Path('data/programs',PID+'.json').read_text())
    family = json.loads(Path('data/families/northeastern-ai-combined-degrees.json').read_text())
    for c in seed['courses']:
        if c['code'] in m.SPEC['courses']:
            c['category'] = m.SPEC['courses'][c['code']]['category']
    resolved = resolve_program(seed,family)
    result = requirement_profile(resolved)
    lookup = {c['id']:c for c in resolved['courses']}
    spec = m.SPEC['degree_review']
    for role in ['required','options','unresolved']:
        for cid in spec['expected_course_ids'][role]:
            assert requirement_profile({**resolved, 'courses':[lookup[cid]]})[role]['count'] == 1
        assert result[role]['count'] == spec['expected_profile'][role]['count']
        assert {k:v for k,v in result[role]['categories'].items() if v} == spec['expected_profile'][role]['categories']
    assert len(spec['expected_codes']['required']) == 15
    assert len(spec['expected_codes']['options']) == 63
    assert 'CS 4120' in spec['expected_codes']['options']
    assert 'COMM 2625' in spec['expected_codes']['options']
    assert 'COMM 2941' in spec['expected_codes']['options']


def test_optional_actual_subjects_and_policies():
    total = 0
    for subject,url in m.SOURCES.items():
        path = Path('.cache/http')/(hashlib.sha256(url.encode()).hexdigest()+'.body')
        if not path.exists():
            pytest.skip('Ignored actual source cache not available')
        html = path.read_text()
        programs = {t['program_id'] for e in m.SPEC['courses'].values() if e['subject']==subject for t in e['targets']}
        for pid in programs:
            first = m.parse_subject(html,program_id=pid,subject=subject)
            assert first == m.parse_subject(html,program_id=pid,subject=subject)
            total += len(first['courses'])
    assert total == 40
    base = Path('.cache/research/degree-audit-northeastern')
    html = (base/(PID+'.html')).read_text()
    observed = m.observe_degree_rules(html)
    assert 'expected_profile' not in observed
    with pytest.raises(ValueError):
        m.observe_degree_rules(html.replace('128 total semester hours', '132 total semester hours'))
    html = (base/'home-16.html').read_text()
    policy = m.parse_camd_policy(html,program_id=PID)
    assert len(policy['requirements']) == 3
    assert all(r['kind']=='note' and not r['course_ids'] for r in policy['requirements'])
    assert 'junior year' in policy['requirements'][1]['summary']
    with pytest.raises(ValueError):
        m.parse_camd_policy(html.replace('junior year','senior year'),program_id=PID)


def test_integrated_observers_preserve_manual_seed_facts_and_one_additional_camd_rule():
    from importlib import import_module
    import json
    base=Path('.cache/research/degree-audit-northeastern')
    pids={t['program_id']for e in m.SPEC['courses'].values()for t in e['targets']}
    for pid in pids:
        seed=json.loads(Path('data/programs',pid+'.json').read_text());adapter=import_module('atlas.adapters.'+pid+'.adapter')
        for subject,url in m.SOURCES.items():
            targets=[c for c,e in m.SPEC['courses'].items()if e['subject']==subject and any(t['program_id']==pid for t in e['targets'])]
            if not targets:continue
            source=base/(subject.lower()+'.html')
            if not source.exists():pytest.skip('Optional ignored subject source')
            observed=adapter.SOURCE_PARSERS[url](source.read_text())
            for code in targets:
                course=next(c for c in observed['courses']if c['code']==code);reviewed=next(c for c in seed['courses']if c['code']==code)
                assert all(reviewed[k]==v for k,v in course.items())
                assert 'category_review'not in course and reviewed['category_review']['status']in {'reviewed','unclassified'}
    seed=json.loads(Path('data/programs',PID+'.json').read_text());adapter=import_module('atlas.adapters.'+PID+'.adapter');url=m.SPEC['camd_policy']['url']
    observed=adapter.SOURCE_PARSERS[url]((base/'home-16.html').read_text())
    assert len(observed['requirements'])==1
    assert observed['requirements'][0]in seed['requirements']
    assert observed['requirements'][0]['id']==PID+'-conditional-camd-clearance'
