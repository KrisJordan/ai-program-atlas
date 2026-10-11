from pathlib import Path
import pytest
from atlas.adapters import stevens_transition_policy as m


def synthetic(kind):
    extra = ('artificial intelligence and cybersecurity; Existing faculty, students and curricula will continue without disruption'
             if kind == 'faq' else 'Dec. 16, 2025; existing faculty, students and curricula continuing without disruption')
    return '<main>School of Computing; Fall 2026; Current computer science majors; their degrees and academic progress remain unchanged; '+extra+'</main>'


@pytest.mark.parametrize('kind', m.SOURCES)
def test_transition_statement_does_not_grant_unstated_policy_or_launch_date(kind):
    result = m.parse(synthetic(kind), kind)
    assert result['courses'] == []
    assert result['requirements'][0]['kind'] == 'note'
    assert result['requirements'][0]['course_ids'] == []
    assert not {'first_offered','curriculum_audit','last_verified'} & result.keys()
    for altered in (synthetic(kind).replace('Fall 2026','Fall 2027'),
                    synthetic(kind).replace('Current computer science majors','All new AI majors'),
                    synthetic(kind).replace('</main>','Advanced Placement guidance has changed.</main>')):
        with pytest.raises(ValueError):
            m.parse(altered, kind)


@pytest.mark.parametrize('kind', m.SOURCES)
def test_optional_actual_public_transition_page(kind):
    path = Path('/tmp/atlas-stevens-transition')/(kind+'.html')
    if not path.exists():
        pytest.skip('Ignored public source cache is not redistributed')
    assert m.parse(path.read_text(),kind)['requirements'][0]['source_id'].endswith(kind)
