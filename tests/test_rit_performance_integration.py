import json
from pathlib import Path
import pytest
from atlas.adapters.rit_music_harmonica_course import parse,parse_composed
from atlas.adapters.rit_writing_closure import PID
from atlas.curriculum_profile import requirement_profile

def fixture():
    return '<main><h1>Music Immersion</h1><h2>Curriculum for 2026-2027 for Music Immersion</h2><table class="sc_courselist"><tbody><tr><td><a class="code_bubble">SOIS-240</a></td><td>Example</td><td></td></tr></tbody></table></main><div class="courseblock"><span class="detail-code">SOIS-240</span><span class="detail-title">Synthetic harmonica title</span><span class="detail-hours_html">(3 Credits)</span><div class="courseblockextra">Synthetic cultural history content.</div><span class="detail-requisites">Second-year standing.</span></div>'

def test_harmonica_observes_actual_content_and_keeps_manual_review_separate():
    o=parse(fixture());c=o['courses'][0]
    assert c['credits']==3 and c['prerequisites']=='Second-year standing.' and c['credit_unit']=='unknown'
    assert c['description']=='Synthetic cultural history content.' and 'category_review' not in c
    assert o['requirements']==[] and parse_composed(fixture())['courses']==o['courses']
    assert parse(fixture().replace('(3 Credits)','(2 Credits)'))['courses'][0]['credits']==2
    for before,after in [('2026-2027','2025-2026'),('class="detail-code">SOIS-240','class="detail-code">PRFL-240'),('Synthetic cultural history content.','Loading course description...')]:
        with pytest.raises(ValueError):parse(fixture().replace(before,after))

def test_repeated_ensemble_bundles_are_not_three_distinct_course_identities():
    d=json.loads(Path('data/programs/'+PID+'.json').read_text());r={x['id'].removeprefix(PID+'-'):x for x in d['requirements']};c={x['code']:x for x in d['courses']}
    music=r['music-immersion'];assert music['count']==3 and music['credits']==9
    assert all(PID+'-prfl-'+str(i) not in music['course_ids'] for i in range(280,286))
    for i in range(280,286):
        rule=r['music-immersion-prfl-'+str(i)+'-bundle'];assert rule['kind']=='choose_credits' and rule['credits']==3 and len(rule['course_ids'])==1
        assert c['PRFL-'+str(i)]['credits'] is None and 'zero-credit' in rule['summary']
    assert c['PRFL-220']['credits']==1
    assert r['theatre-arts-immersion-prfl-220-bundle']['credits']==3
    assert 'one credit per enrollment' in r['theatre-arts-immersion-prfl-220-bundle']['summary']
    assert '0–1' not in r['theatre-arts-immersion-prfl-220-bundle']['summary']
    assert r['theatre-arts-immersion-dance-entry']['kind']=='alternative' and r['theatre-arts-immersion-dance-entry']['count']==1
    assert len(r['theatre-arts-immersion-dance-entry']['course_ids'])==5
    assert r['dance-immersion-lower']['count']==r['dance-immersion-additional']['count']==1
    assert 'same course counted twice' in r['dance-immersion-additional']['summary']
    assert r['theatre-design-and-stagecraft-immersion-group-1']['kind']=='all'
    assert c['PRFN-250']['category']==c['PRFN-341']['category']==c['SOIS-240']['category']=='human_context'
    assert c['PRFN-243']['category_review']['status']=='mixed'
    p=requirement_profile(d);assert [p[k]['count'] for k in ['required','options','unresolved']]==[23,641,15]
    assert len(c)==679 and sum(bool(x['description']) for x in c.values())==676
