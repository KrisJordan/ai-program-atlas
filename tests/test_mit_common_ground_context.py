import importlib,json
from pathlib import Path
import pytest
m=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.common_ground_context')


def fixture(units='12'):
    fields={'Offered under:':'6.C35, 6.C85, 11.C35, 11.C85','Units:':units,'Prerequisite:':'None','Term(s):':'Spring','Level:':'Undergraduate, Graduate'}
    return '<h1>'+m.TITLE+'</h1><ul>'+''.join(f'<li><strong>{k}</strong>{v}</li>'for k,v in fields.items())+'</ul>'


def test_source_units_are_observed_without_precedence_or_course_overwrite():
    a=m.parse(fixture());b=m.parse(fixture('15'))
    assert a['courses']==[]and b['courses']==[]
    assert a['requirements'][0]['kind']=='note'
    assert '12 MIT units'in a['requirements'][0]['summary']
    assert '15 MIT units'in b['requirements'][0]['summary']
    assert 'no offering year'in a['requirements'][0]['summary']


def test_mislinked_optimization_page_cannot_supply_c35_or_c57_metadata():
    path=Path('/tmp/mit-common-ground-detail-1.html')
    if not path.exists():pytest.skip('Optional public wrong-target source capture absent')
    with pytest.raises(ValueError):m.parse(path.read_text())


def test_actual_source_credit_claim_does_not_change_dated_record():
    path=Path('/tmp/mit-common-ground-detail-0.html')
    if not path.exists():pytest.skip('Optional public Common Ground detail capture absent')
    assert '12 MIT units'in m.parse(path.read_text())['requirements'][0]['summary']
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    v=next(c for c in p['courses']if c['id']=='mit-ai-v2025-6-c35')
    assert v['credits']==15 and any('Common Ground'in n for n in v['notes'])
    reference=next(c for c in p['courses']if c['id']=='mit-ai-6-c35-j')
    assert reference['credits']is None
