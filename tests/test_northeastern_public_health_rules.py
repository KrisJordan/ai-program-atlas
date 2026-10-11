from copy import deepcopy
import json
from pathlib import Path
import pytest
from atlas.adapters.northeastern_public_health_rules import PROGRAM_ID as PID, POOLS, apply_home_aligned_choices


def fixture():
    rows=[]; rules=[]
    for key,(title,codes) in POOLS.items():
        parent=PID+'-req-'+key
        rules.append(dict(id=parent+'-rule',parent_id=parent,kind='note',credits=None,summary='Seminar and professional-development choices depend on the home college.',course_ids=[]))
        rows.append('<tr><td>'+title+'</td></tr><tr><td><span class="courselistcomment">Complete the following in alignment with your home college:</span></td><td class="hourscol">1</td></tr>')
        for code in codes:
            rows.append('<tr><td><a class="code">'+code+'</a></td></tr>')
            rules.append(dict(id=PID+'-req-'+code.lower().replace(' ','-'),parent_id=parent,kind='all',course_ids=[PID+'-'+code.lower().replace(' ','-')]))
        rows.append('<tr><td>Next section</td></tr>')
    html='<div id="site-title"><h1>Artificial Intelligence and Public Health, BS (Boston)</h1></div>2026-2027<div id="programrequirementstextcontainer"><table>'+''.join(rows)+'</table></div>'
    return dict(id=PID,requirements=rules),html


def test_published_one_hour_pools_preserve_conditional_ancestry_and_course_ids():
    result,html=fixture();original=deepcopy(result)
    apply_home_aligned_choices(result,html)
    assert {r['id'] for r in result['requirements']}=={r['id'] for r in original['requirements']}
    for key,(_,codes) in POOLS.items():
        choice=PID+'-req-'+key+'-rule'
        node=next(r for r in result['requirements'] if r['id']==choice)
        assert node['kind']=='choose_credits' and node['credits']==1
        assert 'actual home college' in node['summary']
        members=[r for r in result['requirements'] if r['parent_id']==choice]
        assert {cid for r in members for cid in r['course_ids']}=={PID+'-'+c.lower().replace(' ','-') for c in codes}


@pytest.mark.parametrize('old,new', [('Public Health, BS','Health Science, BS'),('2026-2027','2027-2028'),('hourscol">1','hourscol">2'),('HSCI 1000','HSCI 9999'),('alignment with your home college:','all listed courses:')])
def test_changed_identity_hours_members_or_condition_requires_review(old,new):
    result,html=fixture()
    with pytest.raises(ValueError):apply_home_aligned_choices(result,html.replace(old,new))


def test_actual_current_source_replay_if_available():
    path=Path('.cache/research/degree-audit-northeastern')/(PID+'.html')
    if not path.exists():pytest.skip('Optional ignored source capture')
    import importlib.util
    spec=importlib.util.spec_from_file_location('public_health_adapter',Path('atlas/adapters')/PID/'adapter.py')
    adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    observed=adapter.parse(path.read_text())
    seed=json.loads((Path('data/programs')/(PID+'.json')).read_text())
    for key,(_,codes) in POOLS.items():
        ids={PID+'-req-'+key+'-rule'}|{PID+'-req-'+c.lower().replace(' ','-') for c in codes}
        for rid in ids:
            left=next(r for r in observed['requirements'] if r['id']==rid)
            right=next(r for r in seed['requirements'] if r['id']==rid)
            assert {k:left[k] for k in ('id','parent_id','kind','credits','summary','course_ids')}=={k:right[k] for k in ('id','parent_id','kind','credits','summary','course_ids')}
