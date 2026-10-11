import json
from pathlib import Path
import pytest
from atlas.adapters.rit_policy_political_immersion_integration import parse_panels,CLIMATE,QUANTUM,register
from atlas.adapters.rit_writing_closure import PID
from atlas.curriculum_profile import requirement_profile

def fixture():
    title='Climate Change: An Interdisciplinary Problem Immersion'
    codes=['CHEM-531','ENVS-111','PUBL-530']
    rows=''.join(f'<tr><td><a class="code_bubble">{code}</a></td><td>Example</td><td>3</td></tr>'for code in codes)
    cards=''.join(f'<div class="courseblock"><span class="detail-code">{code}</span><span class="detail-title">Synthetic {code}</span><span class="detail-hours_html">({4 if code=="ENVS-111" else 3} Credits)</span><div class="courseblockextra">Synthetic observed content for {code}.</div></div>'for code in codes)
    return f'<main><h1>{title}</h1><h2>Curriculum for 2026-2027 for {title}</h2><table class="sc_courselist"><tbody>{rows}</tbody></table></main>'+cards

def test_composite_source_keeps_three_observer_bindings_and_observed_amounts():
    o=parse_panels(fixture(),url=CLIMATE);c={x['code']:x for x in o['courses']}
    assert len(c)==3 and c['ENVS-111']['credits']==4
    assert c['CHEM-531']['source_id']=='rit-climate-chemistry-card-2026-2027'
    assert c['PUBL-530']['source_id']=='rit-policy-climate-cards-2026-2027'
    assert c['ENVS-111']['source_id']=='rit-applied-science-climate-cards-2026-2027'
    assert o['requirements']==[] and 'curriculum_audit' not in o
    assert all('category_review' not in x for x in c.values())
    for bad in [fixture().replace('2026-2027','2025-2026'),fixture().replace('class="detail-code">PUBL-530','class="detail-code">POLS-420')]:
        with pytest.raises(ValueError):parse_panels(bad,url=CLIMATE)
    with pytest.raises(ValueError):parse_panels(fixture(),url=QUANTUM)

def test_local_rules_preserve_whole_menus_credits_and_ai_overlap():
    d=json.loads(Path('data/programs/'+PID+'.json').read_text());r={x['id'].removeprefix(PID+'-'):x for x in d['requirements']};c={x['code']:x for x in d['courses']}
    for slug in ['public-policy','political-science','american-politics','international-relations','cyberpolitics']:
        rule=r[slug+'-immersion'];assert rule['kind']=='choose_courses' and rule['count']==3 and rule['credits']==9
    assert 'OR International Relations' in r['political-science-immersion']['summary']
    for slug in ['climate-change-interdisciplinary-problem','quantum-information-science-and-technology']:
        assert r[slug+'-immersion']['kind']=='all'
        groups=[r[slug+'-immersion-group-'+str(i)] for i in [1,2,3]]
        assert all(x['count']==1 and x['kind']=='choose_courses' for x in groups)
    assert PID+'-math-241' not in r['quantum-information-science-and-technology-immersion-group-2']['course_ids']
    assert c['PUBL-589']['credits'] is None and c['SOIS-333']['credits']==3
    profile=requirement_profile(d)
    assert [profile[k]['count'] for k in ['required','options','unresolved']]==[23,476,14]
    assert len(c)==513 and sum(bool(x['description']) for x in c.values())==510
    sources=[];parsers={};register(sources,parsers);register(sources,parsers)
    assert len(sources)==len(set(sources)) and set(sources)<={s['url'] for s in d['sources']}
