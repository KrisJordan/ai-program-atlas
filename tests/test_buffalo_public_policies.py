import json
from pathlib import Path
import pytest
from atlas.adapters.buffalo_public_policies import parse_policy,POLICIES,URLS
from atlas.requirements import validate_requirements
ROOT=Path(__file__).resolve().parents[1]


def base(key):
    title,guards,_=POLICIES[key]
    return '<main><h1>'+title+'</h1><p>'+'; '.join(guards)+'</p>'


def rows():
    return '<table id="ub-areas"><tr><th>Course</th><th>Term</th><th>Pathway</th><th>Open Seats</th></tr>'+''.join('<tr>'+''.join('<td>'+v+'</td>' for v in vals)+'</tr>' for vals in [
        ['PHI 199SEM: Synthetic topic','Spring 2027','Justice (List 1)','12'],
        ['PHI 199SEM: Synthetic topic','Spring 2027','Humanity (List 1)','12'],
        ['PHI 199SEM: Other synthetic topic','Winter 2027','Humanity (List 3)','8'],
    ])+'</table>'


def test_dated_offerings_preserve_topics_deduplicate_membership_and_omit_seats():
    html=base('pathways')+rows()+'</main>'
    d=parse_policy(html,program_id='example',key='pathways');validate_requirements(d)
    assert len(d['courses'])==2 and {c['code'] for c in d['courses']}=={'PHI 199'}
    assert len({c['id'] for c in d['courses']})==2
    assert all(c['credits'] is None and c['credit_unit']=='unknown' for c in d['courses'])
    groups=[r for r in d['requirements'] if r['course_ids']]
    assert len(groups)==3 and all(g['kind']=='note' for g in groups)
    assert all('dated subset' in r['summary'] for r in groups)
    changed_seats=parse_policy(html.replace('>12<','>99<'),program_id='example',key='pathways')
    assert changed_seats==d
    with pytest.raises(ValueError):parse_policy(html.replace('PHI 199SEM','Unknown'),program_id='example',key='pathways')
    with pytest.raises(ValueError):parse_policy(html.replace('Spring 2027','Unspecified'),program_id='example',key='pathways')
    with pytest.raises(ValueError):parse_policy(base('pathways')+'</main>',program_id='example',key='pathways')


@pytest.mark.parametrize('key',URLS)
def test_material_policy_changes_are_reviewed_not_certified(key):
    html=base(key)+(rows() if key=='pathways' else '')+'</main>'
    d=parse_policy(html,program_id='example',key=key);validate_requirements(d)
    assert not {'last_verified','curriculum_status','curriculum_audit'}&d.keys()
    with pytest.raises(ValueError):parse_policy(html.replace(POLICIES[key][1][0],'Changed policy'),program_id='example',key=key)
    with pytest.raises(ValueError):parse_policy('<h1>Sign in</h1>'+html,program_id='example',key=key)


def test_capstone_is_general_education_and_has_exact_registration_conditions():
    d=parse_policy(base('capstone')+'</main>',program_id='example',key='capstone')
    assert d['courses'][0]['code']=='UBC 399' and d['courses'][0]['credits']==1
    assert 'concurrently enrolled' in d['courses'][0]['prerequisites']
    assert 'not assumed equivalent' in d['requirements'][0]['summary']


def test_all_family_degrees_preserve_partial_major_scope():
    records=[]
    for p in (ROOT/'data/programs').glob('university-at-buffalo-*.json'):
        d=json.loads(p.read_text())
        if not d.get('family'):continue
        records.append(d)
        assert len(d['courses'])==310
        assert all(c['id'].startswith('buffalo-ubc-') for c in d['courses'])
        assert d['curriculum_status']=='partial'
        assert any('AI+X-specific major inventories' in x for x in d['curriculum_audit']['unresolved_requirements'])
        assert set(URLS.values())<={s['url'] for s in d['sources']}
    assert len(records)==8
