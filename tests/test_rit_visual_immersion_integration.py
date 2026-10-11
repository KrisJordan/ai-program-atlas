"""Review regressions for seven conditional visual/museum immersion paths."""
import json
from pathlib import Path
from collections import Counter
import pytest
from atlas.adapters.rit_visual_immersion_integration import parse_composed
from atlas.curriculum_profile import requirement_profile
PID='rochester-institute-of-technology-artificial-intelligence-bs-degree'
P=json.loads(Path('data/programs/'+PID+'.json').read_text())
R={r['id'].removeprefix(PID+'-'):r for r in P['requirements']}
C={c['code']:c for c in P['courses']}

def codes(key):return {x.removeprefix(PID+'-').upper() for x in R[key]['course_ids']}

def test_distinct_cultural_records_and_actual_label_bindings():
    assert {'MUSE-388','VISL-388','WGST-388'} <= codes('art-history-immersion')
    assert {'MUSE-221','MUSE-388'} <= codes('museum-studies-immersion')
    assert 'COMM-390' in codes('journalism-immersion')
    assert 'COMM/VISL-390' not in C and 'MUSE/HIST-221' not in C
    assert 'at least two' in R['museum-studies-immersion']['summary'].lower()
    assert 'another subject' in R['american-arts-immersion']['summary']
    assert 'more than one discipline' in R['film-studies-immersion']['summary']
    assert '300 level' in R['art-history-immersion']['summary']
    assert 'No 300-level minimum' in R['visual-culture-immersion']['summary']

def test_imaging_credit_range_and_local_required_membership():
    assert codes('science-film-photography-and-imaging-immersion-required')=={'SOFA-103'}
    r=R['science-film-photography-and-imaging-immersion-choices']
    assert r['count']==2 and r['credits'] is None and '6–8' in r['summary']
    assert codes('science-film-photography-and-imaging-immersion-choices')=={'IMGS-221','IMGS-261','IMGS-321','IMGS-341','IMGS-351'}
    assert C['IMGS-261']['credits']==C['IMGS-351']['credits']==4
    assert 'SCIMGS-IM' in C['IMGS-221']['prerequisites']
    assert C['MUSE-249']['credits'] is None and 'nine-hour' in R['museum-studies-immersion']['summary']
    profile=requirement_profile(P)
    assert profile['required']['count']==23
    assert PID+'-sofa-103' not in profile['required'].get('course_ids',[])
    assert all(R[k]['parent_id']==PID+'-immersion-observed-routes' for k in ['american-arts-immersion','art-history-immersion','film-studies-immersion','journalism-immersion','museum-studies-immersion','science-film-photography-and-imaging-immersion','visual-culture-immersion'])

def test_composed_source_uses_observed_fields_and_rejects_unbound_cards():
    title='Art History Immersion';url='https://www.rit.edu/study/art-history-immersion'
    h=f'<main><h1>{title}</h1><h2>Curriculum for 2026-2027 for {title}</h2><table class="sc_courselist"><tbody>'
    for c in ['ARTH-521','MUSE-224']:h+=f'<tr><td><a class="code_bubble">{c}</a></td><td>Title</td></tr>'
    h+='</tbody></table></main>'
    for c in ['ARTH-521','MUSE-224']:h+=f'<div class="courseblock"><span class="detail-code">{c}</span><span class="detail-title">Observed changed name</span><span class="detail-hours_html">(2 Credits)</span><div class="courseblockextra">Synthetic observed body.</div></div>'
    o=parse_composed(h,url=url)
    assert {c['code'] for c in o['courses']}=={'ARTH-521','MUSE-224'}
    assert all(c['credits']==2 and c['description']=='Synthetic observed body.' and 'category_review' not in c for c in o['courses'])
    assert o['requirements']==[] and 'curriculum_audit' not in o
    with pytest.raises(ValueError):parse_composed(h.replace('detail-code">MUSE-224','detail-code">MUSE-999'),url=url)
