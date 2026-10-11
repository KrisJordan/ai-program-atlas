import json
from pathlib import Path
import pytest
from atlas.adapters.rit_combined_sts_course_cards import parse,parse_composed,SPECS
from atlas.adapters.rit_writing_closure import PID
from atlas.curriculum_profile import requirement_profile
URL=next(iter(SPECS))

def fixture():
    title=SPECS[URL][0]
    return f'<main><h1>{title}</h1><h2>Curriculum for 2026-2027 for {title}</h2><table class="sc_courselist"><tbody><tr><td><a class="code_bubble">STSO/WGST-342</a></td><td>Example</td><td></td></tr></tbody></table></main><div class="courseblock"><span class="detail-code">STSO-342</span><span class="detail-title">Gender and science example</span><span class="detail-hours_html">(3 Credits)</span><div class="courseblockextra">Synthetic social interpretation; cross-listed with an unnamed code.</div></div>'

def test_actual_identity_not_split_or_inferred_alias():
    o=parse(fixture(),url=URL)
    assert len(o['courses'])==1 and o['courses'][0]['code']=='STSO-342'
    assert o['observed_label_bindings']==[{'menu_label':'STSO/WGST-342','observed_course_code':'STSO-342'}]
    assert 'course_identity_groups' not in o and 'category_review' not in o['courses'][0]
    assert o['courses'][0]['prerequisites'] is None and o['courses'][0]['credit_unit']=='unknown'
    assert parse_composed(fixture(),url=URL)['courses']==o['courses']
    assert parse(fixture().replace('(3 Credits)','(4 Credits)'),url=URL)['courses'][0]['credits']==4

@pytest.mark.parametrize('old,new',[
 ('class="detail-code">STSO-342','class="detail-code">WGST-342'),
 ('STSO/WGST-342','OTHER-342'),
 ('2026-2027','2025-2026'),
 ('Synthetic social interpretation; cross-listed with an unnamed code.','Loading course description...'),
])
def test_changed_binding_version_and_unsettled_content_are_rejected(old,new):
    with pytest.raises(ValueError):parse(fixture().replace(old,new),url=URL)

def test_manual_routes_map_one_actual_card_per_combined_label_without_merging_wgst():
    d=json.loads(Path('data/programs/'+PID+'.json').read_text());c={x['code']:x for x in d['courses']};r={x['id']:x for x in d['requirements']}
    for code in ['STSO-225','STSO-342','WGST-225','WGST-342']:assert c[code]['category']=='human_context'
    assert not any(c['STSO-342']['id'] in g['course_ids'] for g in d.get('course_identity_groups',[]))
    for slug,n in [('environmental-studies-immersion',18),('science-technology-and-society-immersion',17)]:
        rule=r[PID+'-'+slug];assert rule['count']==3 and len(rule['course_ids'])==n
        assert PID+'-stso-342' in rule['course_ids'] and PID+'-wgst-342' not in rule['course_ids']
    assert c['STSO-488']['credits'] is None and c['STSO-489']['credits'] is None
    p=requirement_profile(d);assert [p[k]['count'] for k in ['required','options','unresolved']]==[23,709,15]
