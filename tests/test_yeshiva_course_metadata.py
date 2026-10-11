import hashlib
import importlib
import json
from pathlib import Path
import pytest
m=importlib.import_module('atlas.adapters.yeshiva-cs-ai-concentration.adapter')
ROOT=Path(__file__).parents[1]

def example(requisites='Prerequisite(s): COM 1000. Corequisite(s): COM 2000.',credits='3'):
    narrative='Build and analyze a test system.'
    profile=dict(code='COM 3000',name='Test Methods',description='Study test systems.',description_sha256=hashlib.sha256(narrative.encode()).hexdigest(),source_id='test')
    html='<main id="main"><h1><span>COM 3000</span> Test Methods</h1><div class="desc">'+narrative+' '+requisites+'</div><div class="sc_credits"><h3>Credits</h3><div class="credits">'+credits+'</div></div><div class="sc_prereqs"></div><div class="sc_coreqs"></div></main>'
    return html,profile

def test_requisites_are_observed_with_alternatives_and_corequisites():
    h,p=example();c=m.parse_course_metadata(h,p)['courses'][0]
    assert c['prerequisites']=='COM 1000. Corequisite(s): COM 2000.'
    h=h.replace('COM 1000.','COM 1500 or COM 1700 may be taken as a prerequisite or corequisite.')
    c=m.parse_course_metadata(h,p)['courses'][0]
    assert 'COM 1500 or COM 1700' in c['prerequisites'] and 'COM 2000' in c['prerequisites']
    assert c['credit_unit']=='unknown' # Separate reviewed policy supplies normalization.

def test_changed_credits_are_observed_not_replayed():
    h,p=example(credits='4');assert m.parse_course_metadata(h,p)['courses'][0]['credits']==4

def test_unstated_requisites_stay_null():
    h,p=example(requisites='');assert m.parse_course_metadata(h,p)['courses'][0]['prerequisites'] is None

@pytest.mark.parametrize('before,after',[
('COM 3000','COM 3999'),('Test Methods','Other Methods'),
('Build and analyze a test system.','Build an unrelated system.'),
('<div class="sc_prereqs"></div>','<div class="sc_prereqs">Dean approval.</div>'),
('</main>','<p>Only majors admitted after review.</p></main>'),
('<div class="credits">3</div>','<div class="credits">3 or 4</div>'),
])
def test_changed_scope_or_unreviewed_prose_fails(before,after):
    h,p=example()
    with pytest.raises(ValueError):m.parse_course_metadata(h.replace(before,after),p)

def test_navigation_cannot_supply_course_identity():
    h,p=example()
    with pytest.raises(ValueError):m.parse_course_metadata('<nav>'+h+'</nav>',p)

def test_reviewed_seed_and_finite_ledger():
    from atlas.db import validate_program
    p=json.loads((ROOT/'data/programs/yeshiva-cs-ai-concentration.json').read_text());validate_program(p)
    ledger=json.loads((ROOT/'research/yeshiva-course-metadata-2026-10-11.json').read_text())
    assert len(p['courses'])==22 and len(p['requirements'])==13 and p['curriculum_status']=='partial'
    assert sum(c['credits'] for c in p['courses'])==75
    assert all(c['description'] and c['credit_unit']=='semester' for c in p['courses'])
    assert sum(c['prerequisites'] is not None for c in p['courses'])==21
    assert next(c for c in p['courses'] if c['code']=='COM 1300')['prerequisites'] is None
    assert 'Corequisite(s): COM 3820' in next(c for c in p['courses'] if c['code']=='COM 3800')['prerequisites']
    assert 'or COM 3810' in next(c for c in p['courses'] if c['code']=='COM 4020')['prerequisites']
    assert p['requirements'][0]['credits']==75 and p['requirements'][0]['credit_unit']=='semester'
    assert ledger['counts']['unattempted_course_pages']==0 and ledger['counts']['access_failures']==0
    assert any('74' in n and '75' in n for n in p['notes'])
    assert next(s for s in p['sources'] if s['id'].endswith('-credit-hour-definition'))['source_date']=='2018-11-01'

def test_optional_actual_22_course_replay_and_pdf_guard():
    seed=json.loads((ROOT/'data/programs/yeshiva-cs-ai-concentration.json').read_text());lookup={c['code']:c for c in seed['courses']}
    for url,p in m.COURSE_PROFILES.items():
        path=ROOT/'.cache/research'/('yu-course-'+p['code'].lower().replace(' ','-')+'.html')
        if not path.exists():pytest.skip('Ignored official course captures absent')
        observed=m.parse_course_metadata(path.read_text(),p)['courses'][0];expected=lookup[p['code']]
        for field in ['code','name','description','prerequisites','credits','source_id','url']:assert observed[field]==expected[field]
    text=(ROOT/'.cache/research/yu-credit-hour-policy.txt').read_text()
    assert 'semester' in m.parse_credit_policy_pdf_text(text)['notes'][0]
    with pytest.raises(ValueError):m.parse_credit_policy_pdf_text(text+' Additional exemption.')
