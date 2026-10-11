import json
from pathlib import Path
import pytest
from atlas.adapters.rit_society_immersion_route import PID, parse
ROOT=Path(__file__).resolve().parents[1]
CODES=['STSO-320','STSO-140','STSO-201','STSO-240','STSO-340','STSO-350','STSO-360','STSO-425','STSO-441','DHSS-101','DHSS-103','PHIL-307','POLS-280','VISL-234']


def fixture():
    def row(code,credits=''):
        return f'<tr><td><span data-code-bubble="{code}">{code}</span></td><td>Observed {code}</td><td>{credits}</td></tr>'
    return ('<h1>AI in Society Immersion</h1><p>The plan code for AI in Society Immersion is AISTS-IM.</p><h2>Curriculum for 2026-2027 for AI in Society Immersion</h2><p>historical, social, cultural, ethical, policy, and environmental perspectives. Immersions may not overlap with program requirements.</p><div id="curriculumContainer"><table class="sc_courselist"><tr><td>Required Course</td></tr>'+row(CODES[0],'3')+'<tr><td>Electives</td></tr><tr><td>Select two of the following:</td><td>6</td></tr>'+''.join(row(c) for c in CODES[1:])+'<tr><td>Total Hours</td><td>9</td></tr></table></div><div class="courseblock"><span class="detail-code">STSO-320</span><span class="detail-title">Observed STSO-320</span><span class="detail-hours_html">(3 Credits)</span><div class="courseblockextra">Synthetic course description.</div></div>')


def test_local_rules_do_not_become_fixed_host_requirements():
    a=parse(fixture());b=parse(fixture().replace('(3 Credits)','(4 Credits)'))
    assert len(a['courses'])==14 and a['courses'][0]['id']==PID+'-stso-320'
    assert a['courses'][0]['credits']==3 and b['courses'][0]['credits']==4
    assert all(c['credits'] is None for c in a['courses'][1:])
    assert a['requirements']==[] and a['observed_local_immersion_requirements']
    assert not {'outcomes','curriculum_status','curriculum_audit','last_verified'} & a.keys()
    assert all(c['category']=='other' and 'category_review' not in c for c in a['courses'])


@pytest.mark.parametrize('old,new',[('AISTS-IM','AISTS-MN'),('2026-2027','2025-2026'),('Select two','Select three'),('detail-title">Observed STSO-320','detail-title">Other title'),('detail-code">STSO-320','detail-code">STSO-999')])
def test_changed_identity_rules_and_misbound_course_rejected(old,new):
    with pytest.raises(ValueError):parse(fixture().replace(old,new))


def test_manual_routes_and_subjects_are_conditionally_scoped():
    from atlas.db import validate_program
    from atlas.curriculum_profile import requirement_profile
    d=json.loads((ROOT/'data/programs'/f'{PID}.json').read_text());validate_program(d)
    c={x['code']:x for x in d['courses']}
    assert len(c)==679 and sum(bool(x['description']) for x in c.values())==676
    assert all(c[code]['credits']==3 and c[code]['prerequisites'] is None for code in CODES)
    assert c['STSO-350']['category']=='human_context' # robotics title is insufficient for AI methods
    assert c['STSO-425']['category']=='human_context' # quantified nature is historical analysis, not math methods
    assert c['DHSS-101']['category_review']['status']=='mixed'
    assert c['VISL-234']['category_review']['candidate_categories']==['human_context','applications']
    req={r['id']:r for r in d['requirements']}
    local=req[PID+'-ai-society-immersion-required']
    assert local['course_ids']==[PID+'-stso-320']
    branch=req[local['parent_id']]
    assert req[branch['parent_id']]['kind']=='alternative'
    p=requirement_profile(d)
    assert [p[k]['count'] for k in ('required','options','unresolved')]==[23,641,15]
    l=json.loads((ROOT/'research/degree-audit/buffalo-delaware-rit.json').read_text());r=next(r for r in l['programs'] if r['program_id']==PID)
    assert PID+'-stso-320' in r['expected_course_ids']['options']
    assert PID+'-stso-320' not in r['expected_course_ids']['required']
    assert r['status']=='in_progress'
    for k in ('required','options','unresolved'):assert p[k]['categories']==r['expected_profile'][k]['categories']
