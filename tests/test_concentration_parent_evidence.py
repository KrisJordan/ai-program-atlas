"""Source-reviewed parent relationships; no award is inferred from the host unit."""
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest

from atlas import db
from atlas.program_relationships import validate_program_relationships

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/programs'
PROGRAMS = {
    p.stem: json.loads(p.read_text()) for p in DATA.glob('*.json')
    if json.loads(p.read_text()).get('program_kind') == 'concentration'
}


def parents(pid):
    return PROGRAMS[pid]['parent_programs']


def test_all_fifty_records_have_individually_reviewed_parent_evidence():
    assert len(PROGRAMS) == 50
    assert Counter(p['parent_program_review']['status'] for p in PROGRAMS.values()) == {
        'verified': 47, 'partial': 2, 'unknown': 1,
    }
    assert sum(len(p['parent_programs']) for p in PROGRAMS.values()) == 50
    notes = (ROOT / 'research/concentration-parents.md').read_text()
    for pid, p in PROGRAMS.items():
        before = deepcopy(p)
        validate_program_relationships(p)
        assert p == before
        review = p['parent_program_review']
        assert review['reviewed_at'] == '2026-10-11'
        assert review['source_ids'] and review['notes']
        assert '### ' + pid in notes
        source_ids = {s['id'] for s in p['sources']}
        for parent in p['parent_programs']:
            assert set(parent['source_ids']) <= set(review['source_ids']) <= source_ids
            assert parent['locator']
            assert parent['reviewed_at'] == review['reviewed_at']


def test_two_explicit_ohio_state_parents_are_not_a_double_major():
    actual = parents('ohio-state-ai-specialization')
    assert {(p['title'], p['award_level']) for p in actual} == {
        ('Computer Science and Engineering', 'BS CSE'),
        ('Computer and Information Science', 'BS CIS'),
    }
    assert all(p['relationship'] == 'specialization' for p in actual)
    assert all(p['parent_program_id'] is None for p in actual)


@pytest.mark.parametrize('pid', [
    'boston-college-artificial-intelligence-concentration-concentration-concentration',
    'ut-austin-cs-ml-ai-concentration',
])
def test_parent_name_does_not_infer_which_computer_science_award_is_eligible(pid):
    p = PROGRAMS[pid]
    assert p['parent_program_review']['status'] == 'partial'
    assert len(p['parent_programs']) == 1
    parent = parents(pid)[0]
    assert parent['title'] == 'Computer Science'
    assert parent['award_level'] is None and parent['award_label'] is None
    assert parent['parent_program_id'] is None


def test_university_wide_immersion_does_not_acquire_an_ai_degree_parent():
    p = PROGRAMS['rit-ai-society-immersion']
    assert p['parent_programs'] == []
    assert p['parent_program_review']['status'] == 'unknown'
    assert 'university-wide' in p['parent_program_review']['notes'][0]
    assert 'not a standalone degree or minor' in p['parent_program_review']['notes'][0]


def test_all_eleven_wpi_paths_belong_to_ai_and_not_the_named_discipline_degree():
    wpi = [p for pid, p in PROGRAMS.items() if pid.startswith('wpi-')]
    assert len(wpi) == 11
    for p in wpi:
        assert len(p['parent_programs']) == 1
        parent = p['parent_programs'][0]
        assert parent['title'] == 'Artificial Intelligence'
        assert parent['award_level'] is None
        assert parent['award_label'] == 'Bachelor of Science'
        assert parent['parent_program_id'] == 'wpi-ai-bs'
        assert parent['relationship'] == 'concentration'
        assert p['parent_program_review']['status'] == 'verified'


@pytest.mark.parametrize('prefix,suffix', [
    ('san-diego-cs-', '-data-science-ai-concentration'),
    ('uva-', 'cs-ai-concentration'),
])
def test_separate_ba_and_bs_paths_retain_separate_parent_awards(prefix, suffix):
    for award in ('BA', 'BS'):
        parent = parents(prefix + award.lower() + suffix)
        assert len(parent) == 1
        assert parent[0]['title'] == 'Computer Science'
        assert parent[0]['award_level'] == award


def test_business_parent_uses_actual_award_not_department_abbreviations():
    cmu = parents('cmu-ai-business-concentration')[0]
    assert (cmu['title'], cmu['award_level'], cmu['award_label']) == (
        'Business Administration', 'B.S.', 'Bachelor of Science')
    wharton = parents('penn-concentration-ai-business')[0]
    assert (wharton['title'], wharton['award_level']) == ('Economics', 'BS')
    assert len(parents('penn-concentration-ai-business')) == 1


def test_penn_engineering_merced_and_uic_do_not_inherit_nearby_unrelated_parents():
    penn = parents('penn-concentration-ai-cs')[0]
    assert (penn['title'], penn['award_level']) == ('Computer Science', 'BSE')
    assert penn['award_label'] == 'Bachelor of Science in Engineering'
    merced = parents('uc-merced-cse-ai-emphasis')[0]
    assert (merced['title'], merced['award_level']) == ('Computer Science and Engineering', 'B.S.')
    uic = parents('uic-cs-ai-concentration')
    assert len(uic) == 1 and uic[0]['title'] == 'Computer Science'
    assert all(p['parent_program_id'] is None for p in [penn, merced, uic[0]])


def test_full_award_evidence_does_not_invent_an_abbreviation():
    msu = PROGRAMS['michigan-state-cs-ai-concentration']
    assert msu['parent_programs'][0]['award_level'] is None
    assert msu['parent_programs'][0]['award_label'] == 'Bachelor of Science'
    assert msu['parent_program_review']['status'] == 'verified'


def test_real_parent_evidence_round_trips_all_fifty_records_idempotently(tmp_path):
    conn = db.connect(tmp_path / "parents.sqlite")
    db.migrate(conn)
    # Only WPI has a parent award represented as a separate existing Atlas record.
    host = json.loads((DATA / 'wpi-ai-bs.json').read_text())
    db.ingest_program(conn, host)
    for p in PROGRAMS.values():
        assert db.ingest_program(conn, p)
        assert not db.ingest_program(conn, p)
    saved = {p['id']: p for p in db.export_data(conn)['programs']}
    for pid, p in PROGRAMS.items():
        assert saved[pid]['parent_programs'] == p['parent_programs']
        assert saved[pid]['parent_program_review'] == p['parent_program_review']
    assert conn.execute('SELECT count(*) FROM program_parents').fetchone()[0] == 50
    assert conn.execute('SELECT count(*) FROM program_parent_reviews').fetchone()[0] == 50
    assert not conn.execute('PRAGMA foreign_key_check').fetchall()
    assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    conn.close()
