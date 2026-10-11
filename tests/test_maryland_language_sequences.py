from pathlib import Path
import json
import pytest
from atlas.adapters import maryland_language_sequences as language
from atlas.db import validate_program

ROOT=Path(__file__).resolve().parents[1]
PID='university-of-maryland-college-park-human-centered-ai-ba-degree'
FIXTURE=(ROOT/'tests/fixtures/maryland_language_synthetic.txt').read_text()


def test_dated_conditional_inventory_and_unknown_metadata():
    observed=language.parse(FIXTURE,pid=PID)
    courses={c['code']:c for c in observed['courses']}
    assert len(courses)==51 and len(observed['requirements'])==26
    assert {'ARAB104','ARAB105','FOLA138','FOLA138_'} .isdisjoint(courses)
    assert courses['CHIN101']['credits']==6 and courses['FREN203']['credits']==4
    assert all(c['name'] is None and c['prerequisites'] is None and c['description'] is None for c in courses.values())
    rules={r['id'].removeprefix(PID+'-language-sequences-2023-'):r for r in observed['requirements']}
    assert 'Terminal requirement: CHIN102 and CHIN103.' in rules['chin-2']['summary']
    assert 'heritage speakers only' in rules['kora-1']['summary']
    assert all(r['kind']=='note' and r['count'] is None for r in rules.values())
    assert rules['reference']['parent_id']==PID+'-policy-arhu-language'
    assert not rules['fola-1']['course_ids']
    assert not {'last_verified','curriculum_status','curriculum_audit'} & observed.keys()


def test_actual_credit_observation_changes_and_ax_text_works():
    changed=FIXTURE.replace('*French (FREN) 103 (4)', '*French (FREN) 103 (5)')
    ax='\n'.join(f'  {i} text {line}' for i,line in enumerate(changed.splitlines()))
    observed=language.parse(ax,pid=PID)
    assert next(c for c in observed['courses'] if c['code']=='FREN103')['credits']==5


@pytest.mark.parametrize('before,after',[
    ('September 2023','September 2026'),
    ('cannot be taken Pass/Fail','can be taken Pass/Fail'),
    ('minimum grade = D-','minimum grade = C-'),
    ('{heritage speakers only}',''),
    ('*Spanish','Spanish'),
    ('Non-Heritage Speakers:','Heritage Speakers:'),
    ('102 (3) and 103 (3)','102 (3) → 103 (3)'),
    ('203 (4)','204 (4)'),
    ('121 (4) → 122 (4)',''),
])
def test_material_rule_or_terminal_identity_change_requires_review(before,after):
    with pytest.raises(ValueError):language.parse(FIXTURE.replace(before,after),pid=PID)


def test_drive_shell_is_not_pdf_evidence():
    with pytest.raises(ValueError):language.parse('<html>Global Engagement Language Sequences.pdf Download</html>',pid=PID)


def test_curated_reference_preserves_source_conflict_and_conditional_parentage():
    d=json.loads((ROOT/'data/programs'/f'{PID}.json').read_text())
    validate_program(d)
    assert d['curriculum_status']=='partial'
    assert any('whereas current ARHU' in x and 'two-language' in x for x in d['curriculum_audit']['unresolved_requirements'])
    source=next(s for s in d['sources'] if s['id'].endswith('-language-sequences-2023'))
    assert source['source_date'] is None and 'September 2023' in source['locator']
    observed=language.parse(FIXTURE,pid=PID)
    expected={r['id']:r for r in observed['requirements']}
    actual={r['id']:r for r in d['requirements'] if r['id'] in expected}
    assert actual==expected
    assert len(d['courses'])==121
