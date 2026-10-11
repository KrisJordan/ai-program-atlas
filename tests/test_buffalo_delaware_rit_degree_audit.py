import importlib.util
import json
from pathlib import Path
import pytest
from atlas.curriculum_profile import requirement_profile
from atlas.families import resolve_program
from atlas.requirements import validate_requirements
from atlas.adapters.rit_ai_degree_courses import parse_rendered_courses, PROGRAM_ID

ROOT=Path(__file__).resolve().parents[1]
LEDGER=json.loads((ROOT/'research/degree-audit/buffalo-delaware-rit.json').read_text())

def load(pid):
    return json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())

@pytest.mark.parametrize('entry',LEDGER['programs'],ids=lambda x:x['program_id'])
def test_independently_reviewed_profiles_and_sources(entry):
    p=load(entry['program_id'])
    family=json.loads((ROOT/'data/families'/f"{p['family']['id']}.json").read_text()) if p.get('family') else None
    resolved=resolve_program(p,family)
    validate_requirements(resolved)
    profile=requirement_profile(resolved)
    sets=entry['expected_course_ids']
    assert set().union(*map(set,sets.values()))=={c['id'] for c in p['courses']}
    assert sum(len(v) for v in sets.values())==len(p['courses'])
    for kind in ('required','options','unresolved'):
        assert profile[kind]['count']==entry['expected_profile'][kind]['count']
        assert profile[kind]['categories']==entry['expected_profile'][kind]['categories']
    assert p['curriculum_status']=='partial'
    expected_status = 'in_progress' if entry['program_id'] == PROGRAM_ID else 'blocked'
    assert entry['status'] == expected_status
    if entry['program_id'] == PROGRAM_ID:
        assert 'accessible GE/WI pool review' in entry['checks']['degree_wide_requirements']
        assert all('not fully mapped' not in b.get('gap', '') for b in entry['blockers'])
    assert entry['blockers'] and entry['second_pass_status']=='pending'
    sources={s['id'] for s in p['sources']}
    for c in p['courses']:
        r=c['category_review']; assert set(r['source_ids'])<=sources
        assert r['rationale'] and r['locator']
        assert c['category'] not in {'electives'}
        assert (c['category']=='other')==(r['status'] in {'mixed','unclassified'})

def test_rit_uncoded_slots_have_no_accidental_elective_memberships():
    p=load(PROGRAM_ID);r={r['id']:r for r in p['requirements']}
    for suffix in ['global','natural','scientific','ethical','artistic','immersion','open','prep','wellness','total','first-year-admission','transfer-admission']:
        assert r[PROGRAM_ID+'-'+suffix]['course_ids']==[]
    assert all(r[PROGRAM_ID+'-'+suffix]['credits']==0 and '0 semester credits' in r[PROGRAM_ID+'-'+suffix]['summary'] for suffix in ['sequence-4','sequence-19','prep'])
    assert len(r[PROGRAM_ID+'-ai-electives']['course_ids'])==3
    assert len(r[PROGRAM_ID+'-robotics-option']['course_ids'])==2
    assert len(r[PROGRAM_ID+'-advising-elective-conflict']['course_ids'])==7

def test_rit_actual_subjects_and_eligibility_are_preserved():
    p=load(PROGRAM_ID);c={c['code']:c for c in p['courses']}
    assert len([x for x in c.values() if x['description']])==446
    assert len([x for x in c.values() if x['prerequisites']])==219
    for code,category in {'IDAI-360':'mathematics','ISTE-230':'systems','IDAI-485':'systems','SWEN-261':'foundations','IDAI-490':'foundations','YOPS-10':'other','PSYC-223':'applications'}.items():
        assert c[code]['category']==category
    assert 'AISYS-MN' in c['ISTE-476']['prerequisites'] and 'AI BS' not in c['ISTE-476']['prerequisites']
    assert c['EEEE-485']['prerequisites']=='EEEE-346 or equivalent.'
    assert 'self-reference' in c['CSCI-431']['prerequisites']
    assert c['CSCI-634']['credits']==3 and c['CSCI-634']['credit_unit']=='semester_hours'
    assert c['YOPS-10']['credits']==0 and c['IDAI-499']['credits']==0
    assert c['LING-581']['prerequisites'].startswith('The description expects')
    assert c['LING-351']['prerequisites'] is None

CARD='''<h1>Artificial Intelligence Bachelor of Science Degree</h1>
<h2>Curriculum for 2026-2027 for Artificial Intelligence BS</h2>
<div class="courseblock"><span class="detail-code">YOPS-10</span>
<span class="detail-title">RIT 365: RIT Connections</span>
<span class="detail-hours_html">(0 Credits)</span>
<div class="courseblockextra">Synthetic orientation description for parser structure testing.</div>
<span class="detail-requisites">This class is restricted to incoming 1st year or Global campus students.</span></div>'''

def test_course_card_observation_requires_exact_context_and_omits_review():
    d=parse_rendered_courses(CARD);c=d['courses'][0]
    assert c['credits']==0 and c['credit_unit']=='unknown' and c['category']=='other'
    assert c['id']==PROGRAM_ID+'-yops-10'
    assert not {'category_review','curriculum_audit','last_verified'} & c.keys()
    assert not {'curriculum_audit','curriculum_status'} & d.keys()
    for old,new in [('2026-2027','2027-2028'),('Bachelor of Science','Master of Science'),('(0 Credits)','(variable)'),('YOPS-10','unknown')]:
        with pytest.raises(ValueError):parse_rendered_courses(CARD.replace(old,new))
    changed=parse_rendered_courses(CARD.replace('Synthetic orientation description','Changed evidence'))
    assert changed['courses'][0]['description']!=c['description']
    assert 'category_review' not in changed['courses'][0]

def test_delaware_adapter_does_not_classify_by_prefix_or_title_keyword():
    path=ROOT/'atlas/adapters/delaware-ai-engineering-major/adapter.py'
    spec=importlib.util.spec_from_file_location('ud_degree_audit',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    html='<h1>Artificial Intelligence Engineering BS</h1><h2>Sample Plan of Study</h2>'
    for year,code in [('First Year','MATH 219'),('Second Year','CISC 210'),('Third Year','ELEG 401'),('Fourth Year','ELEG 625')]:
        html+=f'<div class="et_pb_toggle"><h5>{year}</h5><ul><li>{code} – Broad interdisciplinary topic</li></ul></div>'
    d=m.parse(html)
    assert len(d['courses'])==4 and all(c['category']=='other' for c in d['courses'])
    assert requirement_profile(d)['unresolved']['count']==4
