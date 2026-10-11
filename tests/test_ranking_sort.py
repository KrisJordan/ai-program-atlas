from copy import deepcopy

import pytest

from atlas.rankings import institution_rank_context, program_rank_key

NU = 'National Universities'
LAC = 'National Liberal Arts Colleges'


def rank(value, category=NU, status='primary_verified', edition='2027', **extra):
    return dict(publisher='U.S. News', category=category, edition=edition, rank=value,
                verification_status=status, source_url='https://example.edu/ranking', **extra)


def test_numeric_order_ties_and_missing_are_deterministic_without_changed_ranks():
    entries = []
    for name, value in [('Beta',10), ('Alpha',10), ('Zulu',2), ('Unknown',None)]:
        i = dict(name=name, rankings=[rank(value)])
        entries.append((dict(id=name.lower(),title='AI'),i))
    ordered = sorted(entries,key=lambda item:program_rank_key(*item,NU,'2027'))
    assert [i['name'] for _,i in ordered] == ['Zulu','Alpha','Beta','Unknown']
    assert [institution_rank_context(i,NU,'2027')['rank'] for _,i in ordered] == [2,10,10,None]


@pytest.mark.parametrize('category',[NU,LAC])
@pytest.mark.parametrize('status',['primary_verified','enumerated_secondary','secondary_reported'])
def test_cited_current_numeric_ranks_preserve_category_edition_and_provenance(category,status):
    i = dict(rankings=[rank(2,category,status)])
    result = institution_rank_context(i,category,'2027')
    assert result['rank'] == 2
    assert result['category'] == category
    assert result['edition'] == '2027'
    assert result['verification_status'] == status
    assert result['source_url'] == 'https://example.edu/ranking'


@pytest.mark.parametrize('row',[
    rank(1,status='unverified'),rank(1,status='primary_edition_inferred'),
    rank(1,status='unknown'),rank(None,status='primary_membership_verified',rank_upper_bound=100),
    rank(1,edition='2026'),rank(1,LAC),rank(True),rank(2.5),rank('2'),rank(0),
    {**rank(2),'source_url':None},{**rank(2),'publisher':'Different publisher'},
])
def test_unknown_unverified_wrong_edition_or_category_never_supply_order(row):
    i = dict(rankings=[row])
    original = deepcopy(i)
    assert institution_rank_context(i,NU,'2027')['rank'] is None
    assert i == original


def test_unknown_target_does_not_choose_latest_or_best_recorded_edition():
    i = dict(rankings=[rank(2,edition='2026'),rank(10,edition='2027')])
    assert institution_rank_context(i,NU)['rank'] is None
    assert institution_rank_context(i,NU,'2027')['rank'] == 10


def test_conflicting_current_values_stay_unverified_not_smallest():
    i = dict(rankings=[rank(2),rank(3,status='enumerated_secondary')])
    result = institution_rank_context(i,NU,'2027')
    assert result['rank'] is None
    assert result['reason'] == 'conflicting_ranks'


def test_multiple_sources_agree_and_program_ties_have_stable_display_order():
    i = dict(name='Institution',rankings=[rank(2,status='enumerated_secondary'),rank(2)])
    assert institution_rank_context(i,NU,'2027')['reason'] == 'verified_primary'
    programs = [dict(id='z',title='AI Beta'),dict(id='b',title='AI Alpha'),dict(id='a',title='AI Alpha')]
    assert [p['id'] for p in sorted(programs,key=lambda p:program_rank_key(p,i,NU,'2027'))] == ['a','b','z']
