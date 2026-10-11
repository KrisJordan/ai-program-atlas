"""Thirteen source-read records only; not a whole-degree second pass."""
import hashlib
import json
from pathlib import Path

from bs4 import BeautifulSoup, Comment, NavigableString
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPECS = {key: json.loads((ROOT / f'atlas/adapters/ucsd_{key}_remaining_reviews.json').read_text())
         for key in ['math', 'linguistics']}
ENTRIES = {e['code']: e for spec in SPECS.values() for e in spec['entries']}
# Independently read actual descriptions; these are not prefix-based expectations.
EXPECTED = {
    'LIGN 6': ('ai_ml', 4), 'LIGN 17': ('human_context', 4),
    'LIGN 165': ('ai_ml', 4), 'LIGN 167': ('ai_ml', 4),
    'LIGN 9GS': ('human_context', None), 'LISL 1E': ('human_context', 4),
    'MATH 173A': ('mathematics', 4), 'MATH 181D': ('ai_ml', 4),
    'MATH 155A': ('mathematics', 4), 'MATH 186': ('mathematics', 4),
    'MATH 11': ('mathematics', 5), 'MATH 180A': ('mathematics', 4),
    'MATH 184': ('mathematics', 4),
}


def test_independent_subject_and_nominal_unit_judgments():
    for code, (category, amount) in EXPECTED.items():
        entry = ENTRIES[code]
        assert entry['category'] == category
        assert entry['credits'] == amount
        assert entry['category_review']['status'] == 'reviewed'
    assert ENTRIES['LIGN 6']['observed_prerequisites'] is None
    assert ENTRIES['LIGN 165']['observed_prerequisites'] == 'none.'
    assert 'ability to program' in ENTRIES['LIGN 167']['observed_prerequisites']


def test_unknown_amount_and_scoped_language_entry_conditions():
    global_course = ENTRIES['LIGN 9GS']
    assert global_course['credits'] is None
    assert 'apply and be accepted' in global_course['observed_prerequisites']
    sign = ENTRIES['LISL 1E']
    assert sign['observed_prerequisites'] == 'LISL 1D and LISL 1DX with a grade of C– or better, or equivalent.'
    assert any('does not assign a 1EX corequisite' in n for n in sign['notes'])


def test_math_recommendations_and_conditional_credit_do_not_become_corequisites():
    note = ' '.join(ENTRIES['MATH 180A']['notes'])
    assert 'two after ECON 120A' in note and 'concurrent ECON 120A prevents credit' in note
    assert 'Prior or concurrent MATH 183 or 186' in note
    assert 'MATH 109 is strongly recommended' in note
    assert 'MATH 109' not in ENTRIES['MATH 180A']['observed_prerequisites']
    note = ' '.join(ENTRIES['MATH 186']['notes'])
    assert 'two with prior or concurrent MATH 180A' in note
    for code in ['ECON 120A', 'ECE 109', 'MAE 108', 'MATH 181A', 'MATH 183']:
        assert code in note
    assert 'prevents credit' in note
    note = ' '.join(ENTRIES['MATH 184']['notes'])
    assert 'renumbers MATH 184A' in note
    assert 'concurrent 184/188 yields credit only for 188' in note
    assert 'no identity group' in note
    assert any('Programming knowledge is recommended' in n for n in ENTRIES['MATH 155A']['notes'])
    assert any('restriction alone does not establish cross-list identity' in n for n in ENTRIES['MATH 173A']['notes'])


@pytest.mark.parametrize('key', ['math', 'linguistics'])
def test_independently_extracted_full_source_blocks_match_reviewed_evidence(key):
    spec = SPECS[key]
    source = next(iter(spec['sources'].values()))
    path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored source capture absent')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    soup = BeautifulSoup(raw.decode(), 'html.parser')
    headings = soup.select('p.course-name')
    for entry in spec['entries']:
        if entry['code'] not in EXPECTED:
            continue
        matches = [h for h in headings if ' '.join(h.get_text(' ', strip=True).split()) == entry['heading']]
        assert len(matches) == 1
        parts = []
        for node in matches[0].next_siblings:
            if getattr(node, 'name', None) in ('h1', 'h2', 'h3', 'h4') or 'course-name' in getattr(node, 'attrs', {}).get('class', []):
                break
            if isinstance(node, Comment) or getattr(node, 'name', None) in ('script', 'style'):
                continue
            text = str(node) if isinstance(node, NavigableString) else node.get_text(' ', strip=True)
            if text.strip():
                parts.append(text)
        body = ' '.join(' '.join(parts).split())
        assert hashlib.sha256(body.encode()).hexdigest() == entry['description_hash']
