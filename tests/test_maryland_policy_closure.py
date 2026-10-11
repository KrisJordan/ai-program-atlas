import json
from pathlib import Path
from collections import Counter
import pytest
from atlas.curriculum_profile import requirement_profile
from atlas.adapters import maryland_policy_closure as m

BA='university-of-maryland-college-park-human-centered-ai-ba-degree'
BS='university-of-maryland-college-park-artificial-intelligence-computational-structures-for-ai-systems-bsai-degree'
# Source-transcribed prescribed identities, including BA's explicitly named college math.
FIXED={BA:set('HCAI100 HCAI120 HCAI121 HCAI200 HCAI300 HCAI301 WGSS115 INST204 PHIL211 MATH115'.split()),BS:set('CSAI101 MATH141 PHIL211 INST204 CMSC351 CSAI216'.split())}
# Each line below is a published BA specialization; repeated entries are not additional identities.
BA_POOLS='''INST366 PHIL341 PHIL344 PHIL347 PHIL438 PHIL440 PHPE308 HCAI410
PHIL202 PHIL360 PHIL366 PHIL408 PHIL488 LING311 LING312 LING440 LING449
PHIL362 PHIL366 PHIL370 PHIL470 PHIL478 HCAI410
AMST260 ENGL318 ENGL467 HIST206 HIST407 IMDM150 JOUR389W JOUR458A PHIL344 WGSS280
INST430 INST431 INST432 INST433 INST436 INST480
GVPT170 COMM330 GVPT331 GVPT431 GVPT432 HIST338F HIST454 HIST455 PHIL347 PHIL438L PHIL445 PLCY100 PLCY313 WGSS200
AMST260 ARCH418J ARTT255 ARTT370 COMM371 COMM373 COMM449A THET116 THET385 THET475
HCAI490'''
BS_OPTIONS='''MATH140 MATH340 CMSC141 CMSC131 INST326 CSAI220 STAT400 CSAI221 CMSC421 CMSC132 CMSC142 CSAI102 CSAI103 CSAI104 CMSC250 DATA250 ENEE290 MATH240 MATH243 MATH341 MATH461 INST414 CMSC320 DATA320 STAT426
CSAI473 CMSC422 CMSC425 CMSC426 CMSC427 CMSC454 CMSC470 CMSC474 CMSC477 CMSC498E CMSC498Y CSAI427 CSAI461 IMDM498E INST461 INST436 PSYC431
CSAI370 LING200 LING240 CSAI424 CSAI432 LING311 LING320 LING321 LING322 LING410 LING444
CMSC401 CSAI460 GEOG398E INST366 CSAI433 CSAI435 CSAI491 PLCY201 PLCY215 PLCY240 SOCY100 SOCY216 SOCY455 SOCY456 SOCY462 WGSS115
CMSC472 CMSC434 INST401 WGSS105 AMST320 CMSC471 CMSC436 CSAI431 INST362 INST402'''

def identity(code):
    parent={'PHIL438L':'PHIL438','CMSC498E':'CMSC498','CMSC498Y':'CMSC498','IMDM498E':'IMDM498','GEOG398E':'GEOG398'}.get(code)
    return 'umd-'+(parent.lower()+'-'+code.lower() if parent else code.lower())

@pytest.mark.parametrize('pid,options,fixed_count,option_count,context_count',[(BA,BA_POOLS,10,59,52),(BS,BS_OPTIONS,6,79,0)])
def test_source_transcribed_full_role_sets(pid,options,fixed_count,option_count,context_count):
    p=json.loads(Path('data/programs',pid+'.json').read_text());profile=requirement_profile(p)
    expected_fixed={identity(c) for c in FIXED[pid]};expected_options={identity(c) for c in options.split()}
    assert len(expected_fixed)==fixed_count and len(expected_options)==option_count
    assert {c['id'] for c in p['courses'] if c['id'] in expected_fixed}==expected_fixed
    assert [profile[k]['count'] for k in ['required','options','unresolved']]==[fixed_count,option_count,context_count]
    # Compare the whole actual role partition, not only matching totals.
    actual={role:set() for role in ['required','options','unresolved']}
    for c in p['courses']:
        one=requirement_profile({**p,'courses':[c]})
        for role in actual:
            if one[role]['count']:actual[role].add(c['id'])
    assert actual['required']==expected_fixed
    assert actual['options']==expected_options
    if pid==BA:
        assert 'umd-hcai490' not in actual['required']
        assert 'umd-arhu158' not in actual['required']
        assert all(not r['course_ids'] for r in p['requirements'] if '-plan-' in r['id'])


def test_policy_scope_retains_college_difference_and_never_grants_exceptions():
    assert m.SPEC['cmns-academic']['program_ids']==[BS]
    assert m.SPEC['arhu-plans']['program_ids']==[BA]
    assert '17 fall/spring' in m.SPEC['cmns-academic']['notes'][0]['summary']
    assert '20 fall/spring' in m.SPEC['registration']['notes'][0]['summary']
    assert 'no AI-specific threshold' in m.SPEC['cmns-exceptions']['notes'][0]['summary']
    assert 'fall 2024' in m.SPEC['arhu-plans']['notes'][0]['summary']


def test_shared_source_composition_keeps_existing_observations():
    old=lambda html:{'id':'p','courses':[{'id':'old-course'}],'requirements':[{'id':'old-rule'}]}
    new=lambda html:{'id':'p','requirements':[{'id':'new-rule'}]}
    result=m._compose(old,new,'fixture')
    assert result['courses']==[{'id':'old-course'}]
    assert [r['id'] for r in result['requirements']]==['old-rule','new-rule']
    with pytest.raises(ValueError,match='identity mismatch'):
        m._compose(old,lambda html:{'id':'q'},'fixture')


def test_changed_policy_fails_without_replacing_curated_observations(monkeypatch):
    import hashlib
    html='<main>Fixture college policy.</main>'
    entry={'digest':hashlib.sha256(m.policy_text(html).encode()).hexdigest(), 'notes':[{'key':'n','title':'Policy','summary':'A conditional policy.'}]}
    monkeypatch.setitem(m.SPEC,'fixture',entry)
    observed=m.parse(html,pid='p',key='fixture')
    assert list(observed)==['id','requirements']
    assert observed['requirements'][0]['course_ids']==[]
    assert 'curriculum_audit' not in observed
    with pytest.raises(ValueError,match='manual review required'):
        m.parse(html.replace('college','university'),pid='p',key='fixture')
    with pytest.raises(ValueError,match='content missing'):
        m.parse('<p>Empty page shell</p>',pid='p',key='fixture')
