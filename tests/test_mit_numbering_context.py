import importlib,json
from pathlib import Path
import pytest
m=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.numbering_context')


def fixture(rows=None):
    if rows is None:rows=[dict(newnum=code,oldnum='6.old',title='Observed title',level='G',reason='will use 6.Sxxx number in future')for code in m.CODES]
    return '<h1>Subject Numbering</h1><p>Starting fall 2022</p><script>generatePage('+json.dumps(rows)+');</script>'


def test_actual_render_data_observes_context_without_new_courses_or_roles():
    out=m.parse(fixture())
    assert out['courses']==[] and len(out['requirements'])==12
    assert all(r['kind']=='note'for r in out['requirements'])
    assert 'Observed title'in out['requirements'][0]['summary']
    changed=m.parse(fixture().replace('Observed title','Changed historical title'))
    assert all('Changed historical title'in r['summary']for r in changed['requirements'])
    assert not any('category_review'in r for r in out['requirements'])


@pytest.mark.parametrize('change',['scope','inventory','duplicate'])
def test_wrong_scope_or_incomplete_identity_inventory_rejected(change):
    rows=list(m.observe(fixture()).values())
    html=fixture().replace('Starting fall 2022','Different source')if change=='scope'else fixture(rows[:-1]if change=='inventory'else rows+[rows[0]])
    with pytest.raises(ValueError):m.parse(html)


def test_actual_visible_future_numbering_is_not_replacement_or_degree_exclusion():
    path=Path('/tmp/mit-numbering-0.html')
    if not path.exists():pytest.skip('Optional official public render-data cache absent')
    rows=m.observe(path.read_text())
    future={c for c,r in rows.items()if r.get('reason')=='will use 6.Sxxx number in future'}
    assert future=={'6.5370','6.5380','6.5390','6.5480','6.5490','6.5690','6.5890','6.6440'}
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    for c in p['courses']:
        if c['id'].startswith('mit-ai-v2025-')and c['code']in rows:
            assert c['name']is None and c['category']=='other'
            assert any('does not change'in n for n in c['notes'])
