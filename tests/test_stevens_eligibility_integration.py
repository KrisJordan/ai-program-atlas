import json
from pathlib import Path
from atlas.adapters.stevens_option_eligibility_reviews import SPEC
from atlas.curriculum_profile import requirement_profile
PID='stevens-institute-of-technology-artificial-intelligence-bs-degree'

def test_verified_rules_preserve_description_preparation_and_blank_unknowns():
    p=json.loads((Path('data/programs')/(PID+'.json')).read_text());courses={c['code']:c for c in p['courses']}
    assert sum(bool(c['prerequisites']) for c in courses.values())==37
    assert courses['CH 115']['prerequisites']=='Corequisite: CH 117.'
    assert courses['BIO 181']['prerequisites'] is None
    for code in ['CS 545','CS 584']:
        assert courses[code]['prerequisites']==SPEC[code]['description_prerequisites']+' Published eligibility: '+SPEC[code]['eligibility_rule']
    assert courses['MA 661']['prerequisites']=='MA 540 or MA 611'
    assert courses['BIA 665']['prerequisites']=='MIS 637'
    assert courses['QF 102']['description'] is None and courses['HASS 101']['description'] is None
    registered={s['id'] for s in p['sources']}
    assert all(r['source_id'] in registered for r in SPEC.values() if r['review_status'].startswith('reviewed_'))
    profile=requirement_profile(p);assert [profile[k]['count'] for k in ['required','options','unresolved']]==[24,30,25]

def test_terminal_access_boundary_is_specific_and_no_invented_denials():
    ledger=json.loads(Path('research/degree-audit/national-degree-batch.json').read_text());r=next(r for r in ledger['programs'] if r['program_id']==PID)
    assert r['status']=='blocked' and len(r['blockers'])==4
    assert any('Workday' in b['issue'] and 'EN250/CE240/NANO200' in b['issue'] for b in r['blockers'])
    challenged=[s for s in r['sources'] if s['access_status']=='human_verification_required']
    assert len(challenged)==1 and challenged[0]['url']==SPEC['ENGR 116']['url']
    assert 'not individually attempted' in challenged[0]['locator']
