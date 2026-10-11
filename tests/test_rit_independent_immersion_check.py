"""Independent 2026–2027 route-table transcriptions; see adjacent review note.

Expected menus below were read from the public RIT pages, not generated from
requirement_profile or the production route manifests. These are bounded route
checks, not a whole-degree audit or a student-specific completion solver.
"""
import json
from pathlib import Path

import pytest

from atlas.curriculum_profile import requirement_profile

PID = 'rochester-institute-of-technology-artificial-intelligence-bs-degree'
ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / 'data/programs' / f'{PID}.json').read_text())
COURSES = {c['id']: c for c in P['courses']}
BY_CODE = {c['code']: c for c in P['courses']}
RULES = {r['id']: r for r in P['requirements']}
PARENT = PID + '-immersion-observed-routes'


def codes(text):
    return set(text.split())


# Actual popup codes replace only independently clicked literal slash labels.
# AI-fixed MATH-241 and PSYC-223 are excluded under the explicit overlap rule.
MENUS = {
    'music': codes('PRFL-250 PRFL-251 PRFL-262 PRFL-263 PRFL-264 PRFL-265 PRFL-280 PRFL-281 PRFL-282 PRFL-283 PRFL-284 PRFL-285 PRFL-327 PRFL-352 PRFL-372 PRFL-376 PRFL-465 SOIS-240'),
    'theatre-arts': codes('PRFL-220 PRFL-221 PRFL-222 PRFL-227 PRFL-230 PRFL-235 PRFL-319 PRFL-320 PRFL-321 PRFL-323 PRFL-327 PRFL-330 PRFL-331 PRFN-200 PRFN-204 PRFN-240 PRFN-243 PRFN-244 PRFN-246 PRFN-247'),
    'psychology': codes('PSYC-221 PSYC-221H PSYC-222 PSYC-224 PSYC-224H PSYC-225 PSYC-226 PSYC-231 PSYC-234 PSYC-235 PSYC-236 PSYC-237 PSYC-238 PSYC-239 PSYC-240 PSYC-241 PSYC-242 PSYC-255 PSYC-300'),
    'diversity-inclusion-and-dialogue': codes('LEAD-203 LEAD-303 LEAD-304 LEAD-309 SOCI-220 LEAD-310 HIST-335 LEAD-311 HIST-330 LEAD-312 HIST-333 LEAD-313 SOCI-240'),
    'quantum-information-science-and-technology': codes('PHYS-251 CMPE-257 MATH-233 MATH-241H MATH-367 MATH-367H PUBL-201 PUBL-510 POLS-370 STSO-140 STSO-201 STSO-240'),
    'climate-change-interdisciplinary-problem': codes('CHEM-531 ENVS-531 PUBL-531 HIST-345 PHIL-308 PUBL-530 SOIS-333 STSO-326 STSO-421 STSO-422 ENVS-101 ENVS-111 ENVS-152H ENVS-250 ENVS-305 ENVS-310 ESHS-360'),
    'environmental-studies': codes('HIST-345 PUBL-530 STSO-120 STSO-220 STSO-225 STSO-230 STSO-326 STSO-330 STSO-335 STSO-342 STSO-360 STSO-421 STSO-422 STSO-425 STSO-488 STSO-510 STSO-521 STSO-550'),
    'science-technology-and-society': codes('STSO-140 STSO-201 STSO-225 STSO-230 STSO-240 STSO-246 STSO-320 STSO-335 STSO-340 STSO-341 STSO-342 STSO-350 STSO-360 STSO-425 STSO-441 STSO-489 STSO-510'),
}


def branch(name):
    selected = {PID + '-' + name + '-immersion'}
    while True:
        more = {r['id'] for r in RULES.values() if r['parent_id'] in selected}
        if more <= selected:
            return [RULES[rid] for rid in sorted(selected)]
        selected |= more


def observed_codes(rules):
    return {COURSES[cid]['code'] for r in rules for cid in r['course_ids']}


def scoped_profile(rules, expected_codes):
    return requirement_profile({
        'courses': [BY_CODE[c] for c in expected_codes],
        'requirements': [RULES[PARENT], *rules],
    })


@pytest.mark.parametrize('name', MENUS)
def test_independent_source_menu_and_conditional_profile(name):
    rules = branch(name)
    assert observed_codes(rules) == MENUS[name]
    root = RULES[PID + '-' + name + '-immersion']
    assert root['parent_id'] == PARENT
    assert root['credits'] == 9
    assert root['credit_unit'] == 'semester_hours'
    assert RULES[PARENT]['kind'] == 'alternative'
    profile = scoped_profile(rules, MENUS[name])
    assert profile['required']['count'] == 0
    assert profile['options']['count'] == len(MENUS[name])
    assert profile['unresolved']['count'] == 0
    assert all(c['context'] == 'conditional' for c in profile['choices'] if c['id'] != PARENT)


def test_overlapping_routes_are_a_union_not_additional_fixed_load():
    expected = set().union(*MENUS.values())
    rules = [r for name in MENUS for r in branch(name)]
    profile = scoped_profile(rules, expected)
    assert len(expected) < sum(map(len, MENUS.values()))
    assert profile['options']['count'] == len(expected)
    assert profile['required']['count'] == 0
    assert profile['overlap_count'] > 0


def test_psychology_preparation_and_regular_honors_entries_remain_separate():
    stem = PID + '-psychology-immersion'
    prep = RULES[stem + '-preparation']
    assert prep['kind'] == 'note' and prep['parent_id'] is None
    assert observed_codes([prep]) == {'PSYC-101', 'PSYC-101H'}
    for suffix, expected in [('1', {'PSYC-221', 'PSYC-221H'}), ('2', {'PSYC-224', 'PSYC-224H'})]:
        pair = RULES[stem + '-electives-or-' + suffix]
        assert pair['kind'] == 'alternative' and pair['count'] == 1
        assert observed_codes([pair]) == expected
    assert RULES[stem + '-electives']['count'] == 3
    assert 'PSYC-223' not in observed_codes(branch('psychology'))
    assert 'broader' in RULES[stem]['summary'] and 'open' in RULES[stem]['summary']
    profile = scoped_profile(branch('psychology') + [prep, RULES[stem + '-preparation-or']], MENUS['psychology'] | {'PSYC-101', 'PSYC-101H'})
    assert (profile['required']['count'], profile['options']['count'], profile['unresolved']['count']) == (0, 19, 2)


def test_diversity_fixed_within_route_is_not_fixed_across_degree():
    stem = PID + '-diversity-inclusion-and-dialogue-immersion'
    required = RULES[stem + '-group-1']
    assert required['kind'] == 'all'
    assert observed_codes([required]) == {'LEAD-203', 'LEAD-303'}
    assert RULES[stem + '-group-2']['count'] == 1
    pairs = [r for r in branch('diversity-inclusion-and-dialogue') if r['kind'] == 'alternative']
    assert len(pairs) == 5 and all(r['count'] == 1 and len(r['course_ids']) == 2 for r in pairs)
    assert 'Closed to community development and inclusive leadership majors' in RULES[stem]['summary']


def test_three_science_menus_retain_individual_counts_and_degree_exclusion():
    for name in ('quantum-information-science-and-technology', 'climate-change-interdisciplinary-problem'):
        groups = [r for r in branch(name) if r['kind'] == 'choose_courses']
        assert len(groups) == 3
        assert all(r['count'] == 1 and r['credits'] == 3 for r in groups)
    quantum = RULES[PID + '-quantum-information-science-and-technology-immersion-group-2']
    assert 'MATH-241' not in observed_codes([quantum]) and 'MATH-241' in quantum['summary']
    climate = RULES[PID + '-climate-change-interdisciplinary-problem-immersion']
    assert 'Closed to environmental science' in climate['summary']


def test_ensemble_accumulation_and_optional_dance_limit():
    for number in range(280, 286):
        rule = RULES[f'{PID}-music-immersion-prfl-{number}-bundle']
        assert rule['kind'] == 'choose_credits' and rule['credits'] == 3
        assert observed_codes([rule]) == {f'PRFL-{number}'}
        assert 'three one-credit' in rule['summary'] and 'zero-credit' in rule['summary']
        assert BY_CODE[f'PRFL-{number}']['credits'] is None
    theatre = RULES[PID + '-theatre-arts-immersion-prfl-220-bundle']
    assert theatre['kind'] == 'choose_credits' and theatre['credits'] == 3
    assert BY_CODE['PRFL-220']['credits'] == 1
    assert 'music cards' not in theatre['summary'] and '0–1' not in theatre['summary']
    dance = RULES[PID + '-theatre-arts-immersion-dance-entry']
    assert dance['kind'] == 'alternative' and dance['count'] == 1
    assert observed_codes([dance]) == codes('PRFN-240 PRFN-243 PRFN-244 PRFN-246 PRFN-247')
    assert 'optional' in dance['summary']


def test_combined_labels_identify_clicked_card_without_alias_inference():
    for name in ('environmental-studies', 'science-technology-and-society'):
        rule = RULES[PID + '-' + name + '-immersion']
        assert rule['kind'] == 'choose_courses' and rule['count'] == 3
        assert {'STSO-225', 'STSO-342'} <= observed_codes([rule])
        assert not any(code.startswith('WGST-') for code in observed_codes([rule]))
        assert '300 level or above' in rule['summary']
        assert 'no separate WGST record' in rule['summary']
