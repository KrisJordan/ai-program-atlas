import hashlib
import json
from collections import Counter
from pathlib import Path
import pytest
from atlas import db
from atlas.adapters import drexel_computing_option_review as m

CODES = {'CS 171','CS 172','CS 383','INFO 213','CS 281','CS 283','CS 476','CS 385','CS 387','CS 417','CS 435','CS 455','CS 481','CS 482','CS 486','DSCI 351','DSCI 471','INFO 210','INFO 323','INFO 300','INFO 310','INFO 332','INFO 371','INFO 432','INFO 440'}


def test_observer_is_exact_scoped_and_does_not_certify_review(monkeypatch):
    text='CS 999 Example interface design 3.0 Credits Design and evaluation of interactive software. Repeat Status: Not repeatable for credit Restrictions: Cannot enroll if classification is Freshman Prerequisites: (CS 101 [Min Grade: C] or CS 102 [Min Grade: D]) and MATH 100 [Min Grade: C]'
    html='<article class="search-courseresult"><h3>CS 999 Example interface design 3.0 Credits</h3><div class="courseblock">'+text.split('Credits ',1)[1]+'</div></article>'
    monkeypatch.setattr(m,'SPEC',{'CS 999':{'id':'example','url':'https://example.edu/course','source_id':'example-source','digest':hashlib.sha256(text.encode()).hexdigest(),'description':'Software interface design.','category':'foundations'}})
    o=m.parse(html,'CS 999');c=o['courses'][0]
    assert c['credits']==3 and c['credit_unit']=='unknown'
    assert c['prerequisites']=='Restrictions: Cannot enroll if classification is Freshman; Prerequisites: (CS 101 [Min Grade: C] or CS 102 [Min Grade: D]) and MATH 100 [Min Grade: C]'
    assert o['observed_repeat_status']['CS 999']=='Not repeatable for credit'
    assert not {'category_review','last_verified'} & c.keys()
    assert not {'requirements','curriculum_audit','curriculum_status'} & o.keys()
    for changed in (html.replace('Grade: C','Grade: B'),html.replace('Design and evaluation','Different topic'),html.replace('3.0 Credits','4.0 Credits'),html+html,'<h1>Sign in</h1>'+html,html.replace('CS 999','CS 998')):
        with pytest.raises(ValueError):m.parse(changed,'CS 999')


@pytest.mark.parametrize('code',sorted(CODES))
def test_actual_option_cache_when_available(code):
    path=Path('/tmp/atlas-national-degree-audit/drexel-'+code.replace(' ','').lower()+'.html')
    if not path.exists():pytest.skip('Local public course result unavailable')
    o=m.parse(path.read_text(),code)
    assert o['courses'][0]['code']==code and 'category_review' not in o['courses'][0]


def test_actual_review_dispositions_do_not_change_requirement_roles():
    p=json.loads(Path('data/programs',m.PID+'.json').read_text());db.validate_program(p)
    c={x['code']:x for x in p['courses']}
    assert set(m.SPEC)==CODES
    assert Counter(c[x]['category'] for x in CODES)=={'ai_ml':11,'systems':6,'foundations':3,'mathematics':2,'applications':1,'human_context':1,'other':1}
    assert c['CS 435']['category_review']['status']=='mixed'
    assert c['CS 455']['category']=='applications' and c['INFO 440']['category']=='human_context'
    assert c['INFO 213']['category']=='ai_ml' and c['INFO 310']['category']=='foundations'
    assert c['CS 281']['credits']==4 and all(c[x]['credits']==3 for x in CODES-{'CS 281'})
    assert all(c[x]['credit_unit']=='unknown' for x in CODES)
    assert sum(bool(x.get('category_review')) for x in p['courses'])>=36
    assert len(p['courses'])==281 and p['curriculum_status']=='partial'
    # No observer emits requirement changes. CS383 remains in a choice, not a new fixed requirement.
    assert not any(r['kind']=='all' and r['course_ids']==[c['CS 383']['id']] for r in p['requirements'])
    e=next(x for x in json.loads(Path('research/degree-audit/national-degree-batch.json').read_text())['programs'] if x['program_id']==m.PID)
    assert e['status'] in ('in_progress','blocked') and e['expected_profile']['required']['count']==11
