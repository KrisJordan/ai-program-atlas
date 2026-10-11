import copy
import json
from pathlib import Path

import pytest
from atlas.adapters.miami_limited_identity_reviews import SPEC, apply_observed_categories
from atlas.adapters.miami_cognate_export import full_individualized_observation
from atlas.adapters.miami_thematic_directory import parse_thematic

ROOT = Path(__file__).resolve().parents[1]


def test_exact_missing_content_dispositions_and_source_facts():
    assert len(SPEC['courses']) == 36
    assert sum(e['category'] == 'other' for e in SPEC['courses'].values()) == 34
    assert {code for code, e in SPEC['courses'].items() if e['category'] == 'human_context'} == {'GER 400', 'THA 300'}
    for pid in next(iter(SPEC['courses'].values()))['program_ids']:
        p = json.loads((ROOT / 'data/programs' / (pid + '.json')).read_text())
        bycode = {c['code']: c for c in p['courses']}
        for code, e in SPEC['courses'].items():
            c = bycode[code]
            assert c['name'] == e['name'] and c['category'] == e['category']
            assert c['description'] is None and c['prerequisites'] is None
            assert c['category_review']['rationale'] == e['review']['rationale']
            assert c['category_review']['source_ids'] == [e['source_id']]
            assert c['credits'] == (3 if code in {'GER 400', 'HCS 317', 'THA 300'} else None)
        assert all(c.get('category_review') for c in p['courses'])


def test_observation_never_certifies_review_or_invents_content():
    e = SPEC['courses']['PHI 301']
    c = dict(code='PHI 301', name=e['name'], source_id=e['source_id'], category='human_context', description=None, prerequisites=None)
    out = apply_observed_categories({'courses': [copy.deepcopy(c)]})['courses'][0]
    assert out['category'] == 'other' and 'category_review' not in out
    for key, value in [('name', 'New course'), ('description', 'New actual description'), ('prerequisites', 'New restriction')]:
        changed = {**c, key: value}
        with pytest.raises(ValueError): apply_observed_categories({'courses': [changed]})
    other = {**c, 'source_id': 'unrelated-source'}
    assert apply_observed_categories({'courses': [other]})['courses'][0] == other


def test_dated_pdf_observation_keeps_unknown_fields_and_context():
    data = json.loads((ROOT / 'research/miami-individualized-cognate-pool.json').read_text())
    result = full_individualized_observation(data, pid='synthetic')
    selected = [c for c in result['courses'] if c['code'] in SPEC['courses']]
    assert len(selected) == 33
    assert all(c['category'] == 'other' and c['credits'] is None and c['description'] is None for c in selected)
    assert all(r['kind'] == 'note' for r in result['requirements'])


@pytest.mark.parametrize('plan,code', [('AT_0050','GER 400'),('PS_0080','HCS 317'),('PS_0072','THA 300')])
def test_optional_actual_thematic_replay(plan,code):
    path = ROOT / 'var/miami-cognates' / (plan + '.html')
    if not path.exists(): pytest.skip('Ignored ordinary public source capture')
    result = parse_thematic(path.read_text(), pid='synthetic', plan=plan)
    c = next(c for c in result['courses'] if c['code'] == code)
    assert c['category'] == SPEC['courses'][code]['category']
    assert c['description'] is None and c['credits'] == 3 and 'category_review' not in c
