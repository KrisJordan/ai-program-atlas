"""Exact remaining route roles and independently stated credit eligibility."""
import json
from pathlib import Path
import pytest
from atlas.adapters.rit_remaining_immersion_integration import parse
from atlas.curriculum_profile import requirement_profile
PID='rochester-institute-of-technology-artificial-intelligence-bs-degree'
P=json.loads(Path('data/programs/'+PID+'.json').read_text());R={r['id'].removeprefix(PID+'-'):r for r in P['requirements']};C={c['code']:c for c in P['courses']}
def ids(key):return {x.removeprefix(PID+'-').upper() for x in R[key]['course_ids']}

def test_gis_ban_is_different_from_conditional_major_overlap():
    assert ids('geographic-information-systems-immersion-group-1')=={'IGME-382','IGME-384'}
    assert R['geographic-information-systems-immersion-group-2']['count']==1
    assert ids('geographic-information-systems-immersion-group-2')=={'GCIS-123','IGME-386','IGME-484','IGME-489','IMGS-111','ISTE-230','STAT-145'}
    assert R['geographic-information-systems-immersion-excluded-credit']['kind']=='note'
    assert 'No GCCIS students' in C['ISCH-370']['prerequisites']
    assert 'permission' in R['principles-computing-immersion']['summary'].lower()
    assert R['principles-computing-immersion']['kind']=='note' and R['principles-computing-immersion']['parent_id'] is None
    assert 'degree requirements' not in C['ISCH-201']['prerequisites']
    assert 'GIS-IM students' in C['IGME-489']['prerequisites']
    q=json.loads(Path('research/degree-audit/buffalo-delaware-rit.json').read_text())
    row=next(x for x in q['programs'] if x['program_id']==PID)
    assert {PID+'-isch-110',PID+'-isch-370'} <= set(row['expected_course_ids']['unresolved'])
    assert not ({PID+'-isch-110',PID+'-isch-370'} & set(row['expected_course_ids']['options']))

def test_vip_accumulates_credits_on_one_project_and_keeps_null_scalar_ranges():
    assert R['vertically-integrated-projects-immersion']['credits']==9
    assert R['vertically-integrated-projects-immersion-advanced']['kind']=='choose_credits'
    assert R['vertically-integrated-projects-immersion-advanced']['credits']==3
    assert ids('vertically-integrated-projects-immersion-advanced')=={'ITDL-511'}
    assert ids('vertically-integrated-projects-immersion-remaining')=={'ITDL-211','ITDL-511'}
    assert R['vertically-integrated-projects-immersion-remaining']['credits']==6
    assert 'same project' in R['vertically-integrated-projects-immersion']['summary']
    assert C['ITDL-211']['credits'] is C['ITDL-511']['credits'] is None
    assert all('permission' in C[c]['prerequisites'] for c in ['ITDL-211','ITDL-511'])

def test_source_alternatives_topics_and_historical_statements_not_repaired():
    free='free-culture-and-free-and-open-source-computing-immersion'
    assert ids(free+'-group-1')=={'DHSS-488','ENGL-450'}
    assert 'Topic ID' in R[free]['summary']
    assert R[free+'-historical']['kind']=='note' and R[free+'-historical']['parent_id'] is None
    assert 'ISCH-110' not in ids(free+'-group-1')
    t='transmedia-storytelling-and-entertainment-immersion'
    assert R[t]['credits'] is None
    assert ids(t+'-group-1')=={'DHSS-500','ENGL-377'} and R[t+'-group-1']['kind']=='alternative'
    assert R[t+'-group-2']['count']==2 and 'ENGL-377' in ids(t+'-group-2')
    assert 'cannot also satisfy' in R[t+'-group-2']['summary']
    assert 'unresolved' in R[t]['summary']
    assert 'PRFL-330' in ids('comics-studies-immersion') and 'SOCI-246' in ids('global-justice-immersion')
    assert not any(c in C for c in ['CSCI-101','CINT-110','CINT-201','DHSS/ITDL-500'])

def test_scope_is_full_named_routes_not_complete_general_education():
    root=PID+'-immersion-observed-routes'
    assert len([r for r in P['requirements'] if r['parent_id']==root])==76
    assert P['curriculum_status']=='partial'
    q=json.loads(Path('research/rit-immersion-course-review-queue.json').read_text())
    assert q['review_state_counts']=={'existing_reviewed_description':784,'historical_reference_only':3}
    p=requirement_profile(P)
    assert [p[k]['count'] for k in ['required','options','unresolved']]==[23,770,17]
    assert len(C)==810 and sum(bool(c['description']) for c in C.values())==807

def test_composed_observer_preserves_actual_gis_metadata_not_role_certification():
    title='Geographic Information Systems Immersion';url='https://www.rit.edu/study/geographic-information-systems-immersion'
    h=f'<main><h1>{title}</h1><h2>Curriculum for 2026-2027 for {title}</h2><table class="sc_courselist"><tbody>'
    for c in ['IGME-382','IMGS-111']:h+=f'<tr><td><a class="code_bubble">{c}</a></td><td>Title</td></tr>'
    h+='</tbody></table></main>'
    for c in ['IGME-382','IMGS-111']:h+=f'<div class="courseblock"><span class="detail-code">{c}</span><span class="detail-title">Observed title</span><span class="detail-hours_html">(4 Credits)</span><div class="courseblockextra">Synthetic actual body.</div></div>'
    o=parse(h,url=url)
    assert {c['code'] for c in o['courses']}=={'IGME-382','IMGS-111'}
    assert all(c['credits']==4 and c['credit_unit']=='unknown' and 'category_review' not in c for c in o['courses'])
    assert o['requirements']==[] and 'curriculum_audit' not in o
    with pytest.raises(ValueError):parse(h.replace('detail-code">IGME-382','detail-code">IGME-999'),url=url)

def test_every_registered_observer_source_is_registered_even_for_reused_identity():
    from atlas.adapters.rit_remaining_immersion_integration import MODULES,SLUGS
    source_ids={s['id'] for s in P['sources']}
    for module in MODULES:
        for s in module.MANIFEST['sources']:
            if s['url'].rsplit('/',1)[-1] in SLUGS:assert s['id'] in source_ids
    assert 'rit-final-justice-cards-2026-2027' in C['SOCI-246']['category_review']['source_ids']
    assert 'rit-final-comics-cards-2026-2027' in C['PRFL-330']['category_review']['source_ids']
