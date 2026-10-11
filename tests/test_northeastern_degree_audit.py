"""Source-backed category decisions must not become broad automatic heuristics."""
import json
from pathlib import Path
from importlib import import_module

import pytest

from atlas.adapters.northeastern_courseleaf import CATEGORY_DECISIONS, category
from atlas.adapters.northeastern_course_metadata import parse_subject

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('code,expected', [
    ('CS 1800','mathematics'), ('DS 3000','mathematics'), ('CS 4120','ai_ml'),
    ('CY 4170','human_context'), ('CY 5240','human_context'), ('DS 1300','human_context'),
    ('ECON 1115','human_context'), ('ECON 2350','mathematics'), ('ECON 2560','mathematics'),
    ('CS 1200','other'), ('CS 1210','other'), ('CS 4991','other'), ('DS 4200','other'),
])
def test_individual_decisions_follow_reviewed_content(code,expected):
    decision = CATEGORY_DECISIONS[code]
    assert category(code, decision['name'], decision['guard']) == expected
    assert category(code, 'Changed Course Identity', decision['guard']) == 'other'
    assert category(code, decision['name'], 'Entirely different description') == 'other'


@pytest.mark.parametrize('code,title', [('ECON 9999','Economics'),('MATH 9999','Orientation'),
    ('CS 9999','Artificial Intelligence'),('DS 9999','Machine Learning'),('PHIL 9999','Ethics')])
def test_unknown_identity_is_not_classified_by_prefix_or_title_keyword(code,title):
    assert category(code,title) == 'other'


def test_changed_description_has_no_review_and_no_stale_category():
    html = '''<header id="site-title"><h1>Data Science (DS)</h1></header>
    <div id="textcontainer"><div class="courseblock"><p class="courseblocktitle">
    DS 3000. Mathematical Foundations of Artificial Intelligence. (4 Hours)</p>
    <p class="cb_desc">New unrelated material.</p></div></div>'''
    d = parse_subject(html,program_id='synthetic',subject='DS',heading='Data Science (DS)',
                      codes=['DS 3000'],url='https://catalog.northeastern.edu/course-descriptions/ds/')
    assert d['courses'][0]['category'] == 'other'
    assert 'category_review' not in d['courses'][0]


def test_minimum_credit_wording_is_preserved_without_fixing_an_exact_course_count():
    from test_northeastern_curriculum import document, row, parse
    html = document('<tr><td>Complete a minimum of 16 semester hours of general electives.</td><td class="hourscol">16</td></tr>' + row('CS 9999','Synthetic Subject'))
    d = parse(html)
    choice = next(r for r in d['requirements'] if r['kind'] == 'choose_credits')
    assert choice['credits'] == 16 and choice['count'] is None
    assert 'minimum' in choice['summary']
    with pytest.raises(ValueError,match='Conflicting credit'):
        parse(html.replace('minimum of 16','minimum of 12'))


def test_each_degree_has_individual_audit_entry_and_registered_category_evidence():
    ledger = json.loads((ROOT/'research/degree-audit/northeastern.json').read_text())
    entries = {r['program_id']:r for r in ledger['programs']}
    degrees = [json.loads(p.read_text()) for p in (ROOT/'data/programs').glob('northeastern*.json')]
    degrees = [p for p in degrees if p['program_kind'] == 'degree']
    assert len(degrees) == len(entries) == 24
    for program in degrees:
        entry = entries[program['id']]
        assert entry['status'] in {'in_progress','blocked','audited'}
        assert entry['sources'] and len(entry['checks']) == 8
        source_ids = {s['id'] for s in program['sources']}
        for c in program['courses']:
            review = c.get('category_review')
            if not review:
                continue
            assert set(review['source_ids']) <= source_ids
            decision = CATEGORY_DECISIONS[c['code']]
            assert c['name'] == decision['name'] and c['category'] == decision['category']
            assert review['rationale'] == decision['rationale']
            assert review['status'] == decision['status']
            if review['status'] in {'mixed','unclassified'}:
                assert c['category'] == 'other'


def test_optional_communication_catalog_minimum_phrase_replays():
    pid='northeastern-university-artificial-intelligence-and-communication-studies-bs-boston-bs-degree'
    file=ROOT/'.cache/research/degree-audit-northeastern'/f'{pid}.html'
    if not file.exists():pytest.skip('Optional official catalog cache')
    parsed=import_module('atlas.adapters.'+pid+'.adapter').parse(file.read_text())
    node=next(r for r in parsed['requirements'] if r['id']==pid+'-req-required-general-electives-credit-choice')
    assert node['credits']==16 and node['kind']=='choose_credits'
