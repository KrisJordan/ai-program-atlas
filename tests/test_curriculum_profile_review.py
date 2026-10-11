"""Independent semantic regressions patterned on reviewed MIT/Iowa graphs."""
from copy import deepcopy
import random

from atlas.curriculum_profile import requirement_profile
from atlas.families import resolve_program


def node(key, kind='all', parent=None, courses=(), **extra):
    result = dict(id=key, parent_id=parent, title=key, kind=kind,
                  count=None, credits=None, credit_unit='unknown', category='other',
                  source_id='catalog', source_text=None, summary='', course_ids=list(courses))
    result.update(extra)
    return result


def program(codes, requirements):
    return dict(courses=[dict(id=c, code=c, category='other', credits=None,
                             credit_unit='unknown') for c in codes], requirements=requirements)


def counts(profile):
    return tuple(profile[k]['count'] for k in ['required', 'options', 'unresolved'])


def test_mit_style_alternative_bundles_are_not_all_mandatory():
    p = program(['core', 'single', 'intro', 'comp', 'engineering', 'context', 'unbound'], [
        node('degree'), node('core-rule', parent='degree', courses=['core']),
        node('programming', 'alternative', 'degree', credits=12, credit_unit='units'),
        node('single-route', parent='programming', courses=['single']),
        node('bundle-a', parent='programming', courses=['intro', 'comp']),
        node('bundle-b', parent='programming', courses=['intro', 'engineering']),
        node('supplement', 'note', courses=['context']),
        node('overlapping-elective', 'choose_courses', courses=['core'], count=1),
    ])
    r = requirement_profile(p)
    assert counts(r) == (1, 4, 2)
    choices = {c['id']: c for c in r['choices']}
    assert choices['programming']['context'] == 'required'
    assert choices['programming']['credits'] == 12
    assert choices['programming']['credit_unit'] == 'units'
    # Same observed course can be in several bundles but counts only once.
    assert sum(counts(r)) == len(p['courses'])


def test_iowa_style_credit_choice_with_note_pools_stays_unresolved():
    p = program(['core', 'theory', 'methods', 'application', 'direct'], [
        node('minor'), node('core-rule', parent='minor', courses=['core']),
        node('electives', 'choose_credits', 'minor', courses=['direct'],
             credits=12, credit_unit='semester_hours'),
        node('theory-pool', 'note', 'electives', courses=['theory']),
        node('methods-pool', 'note', 'electives', courses=['methods']),
        node('application-pool', 'note', 'electives'),
        node('application-entry', parent='application-pool', courses=['application']),
    ])
    r = requirement_profile(p)
    assert counts(r) == (1, 1, 3)
    assert r['choices'][0]['credits'] == 12
    assert r['choices'][0]['context'] == 'required'
    # Twelve is source-defined load, not twelve required courses or pool credits.
    assert r['required']['count'] != r['choices'][0]['credits']


def test_note_ancestor_dominates_nested_choice_and_unknown_load_remains_unknown():
    p = program(['a', 'b'], [node('context', 'note'),
        node('candidate-choice', 'choose_credits', 'context'),
        node('candidate-bundle', parent='candidate-choice', courses=['a', 'b'])])
    r = requirement_profile(p)
    assert counts(r) == (0, 0, 2)
    assert r['choices'][0]['context'] == 'unresolved'
    assert r['choices'][0]['credits'] is None
    assert r['choices'][0]['credit_unit'] == 'unknown'


def test_single_observed_choice_is_not_promoted_when_pool_might_be_partial():
    p = program(['only-observed'], [node('incomplete-pool', 'choose_courses',
                 courses=['only-observed'], count=1)])
    assert counts(requirement_profile(p)) == (0, 1, 0)


def test_family_replacement_and_exclusion_are_resolved_before_profiling():
    shared = node('shared', courses=['A', 'B'])
    shared['course_codes'] = shared.pop('course_ids')
    family = dict(id='family', institution_id='university', name='Synthetic family',
                  classification_kind='source_stated', sources=[dict(id='catalog', url='https://example.edu')],
                  shared_requirements=[shared])
    p = program(['A', 'B', 'local'], [node('local', courses=['local']),
        node('bound', 'choose_courses', courses=['A', 'B'], count=1)])
    p.update(institution={'id': 'university'}, sources=[dict(id='catalog')],
             family=dict(id='family', variant_label='Variant', disciplines=['AI', 'Domain'],
                         relationship='integrated', classification_kind='source_stated', source_ids=['catalog'],
                         requirement_bindings=[dict(shared_id='shared', id='bound', parent_id=None,
                             course_ids=['A', 'B'], source_id='catalog')],
                         requirement_overrides=[dict(shared_id='shared', operation='replace',
                             reason='Explicit local option replaces shared mandatory core.', source_id='catalog')]))
    resolved = resolve_program(p, family)
    assert counts(requirement_profile(resolved)) == (1, 2, 0)
    assert requirement_profile(resolved)['choices'][0]['origin'] == 'replacement'
    p['requirements'] = [node('local', courses=['local'])]
    p['family']['requirement_bindings'] = []
    p['family']['requirement_overrides'][0]['operation'] = 'exclude'
    assert counts(requirement_profile(resolve_program(p, family))) == (1, 0, 2)


def test_profile_does_not_mutate_input_and_partition_is_order_independent():
    p = program(['a', 'b', 'c', 'd'], [node('all', courses=['a', 'a']),
        node('choice', 'alternative', courses=['a', 'b']),
        node('context', 'note', courses=['a', 'b', 'c'])])
    for course, category in zip(p['courses'], ['ai_ml', 'mathematics', 'human_context', 'systems']):
        course['category'] = category
    before = deepcopy(p)
    baseline = requirement_profile(p)
    assert p == before
    assert counts(baseline) == (1, 1, 2)
    for seed in range(8):
        shuffled = deepcopy(p)
        random.Random(seed).shuffle(shuffled['requirements'])
        random.Random(seed + 10).shuffle(shuffled['courses'])
        r = requirement_profile(shuffled)
        assert counts(r) == counts(baseline)
        assert sum(counts(r)) == len({c['id'] for c in p['courses']})
        assert r['overlap_count'] == baseline['overlap_count']
        for bucket in ['required', 'options', 'unresolved']:
            assert r[bucket]['categories'] == baseline[bucket]['categories']
            assert sum(r[bucket]['categories'].values()) == r[bucket]['count']
