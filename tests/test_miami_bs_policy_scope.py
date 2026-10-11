from copy import deepcopy
import importlib
from pathlib import Path
import pytest
from atlas.adapters.miami_bs_policy_scope import PROGRAM, apply


def test_full_published_rows_keep_higher_requirement_and_scoped_waivers():
    module=importlib.import_module('atlas.adapters.'+PROGRAM+'.adapter')
    html=Path('tests/fixtures/next_degrees/miami-ds-bs.html').read_text()
    result=module.parse(html)
    bytitle={r['title']:r for r in result['requirements']}
    assert bytitle['Language course 200-level or higher']['credits']==9
    assert bytitle['Total Credit Hours']['credits']==121
    note=next(r for r in result['requirements']if r['id']==PROGRAM+'-language-conflict')
    assert note['kind']=='note' and note['course_ids']==[]
    assert 'compatible' in note['summary'] and 'does not establish' in note['summary']
    assert 'curriculum_audit'not in result
    unannotated={**result,'requirements':[r for r in result['requirements']if r is not note]}
    for label in ['Language course 200-level or higher','Total Credit Hours']:
        changed=deepcopy(unannotated);next(r for r in changed['requirements']if r['title']==label)['credits']+=1
        with pytest.raises(ValueError):apply(changed)
    with pytest.raises(ValueError):apply({**unannotated,'id':'unrelated'})
