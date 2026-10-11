import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_hila_reviews as hila, ucsd_sio_reviews as sio, ucsd_eds_reviews as eds, ucsd_cgs_reviews as cgs, ucsd_mus_reviews as mus, ucsd_biology_reviews as bio, ucsd_glbh_reviews as glbh, ucsd_psyc_reviews as psyc, ucsd_linguistics_reviews as ling, ucsd_physics_astronomy_reviews as physics, ucsd_chem_reviews as chem, ucsd_literature_first_reviews as lit, ucsd_engineering_reviews as eng, ucsd_health_development_reviews as health, ucsd_theatre_reviews as theatre, ucsd_environment_reviews as env, ucsd_management_interdisciplinary_reviews as inter, ucsd_area_religion_reviews as area
from atlas.curriculum_profile import requirement_profile

PID=hila.SPEC['program_id']

def test_history_sio_integration_preserves_held_identity_and_roles():
    d=json.loads(Path('data/programs',PID+'.json').read_text());cs={c['code']:c for c in d['courses']}
    assert cs['HILA 119']['credits'] is None
    assert 'EASY' in ' '.join(cs['HILA 167']['notes'])
    assert cs['HIUS 120']['name']=='Race and Oral History in San Diego (cross-listed with ETHN 120) (4 or 6)'
    assert cs['HIUS 120']['category_review']['status']=='unclassified'
    assert cs['HIUS 120D']['category_review']['status']=='mixed'
    assert 'strongly recommended' in ' '.join(cs['HIUS 120D']['notes'])
    for code in ['SIO 105','SIO 113']:
        assert cs[code]['category_review']['status']=='unclassified'
        assert cs[code]['category']=='other'
    assert cs['SIO 105']['name']=='Conservation Solutions'
    assert cs['SIO 194']['credits']==4
    assert 'six-to-eight-unit' in ' '.join(cs['SIO 194']['notes'])
    assert cs['SIO 109']['category_review']['status']=='mixed'
    assert cs['POLI 117']['category_review']['status']=='unclassified'
    assert [requirement_profile(d)[k]['count']for k in ['required','options','unresolved']]==[8,119,2241]

@pytest.mark.parametrize('module,subject,count,dispositions',[(hila,'HILA',265,20),(sio,'SIO',35,6),(eds,'EDS',31,1),(cgs,'CGS',24,0),(mus,'MUS',27,6),(bio,'BIOL',34,3),(glbh,'GLBH',24,2),(psyc,'PSYC',14,2),(ling,'LING',25,14),(physics,'PHYS',14,1),(physics,'ASTR',10,1),(chem,'CHEM',13,1),(lit,'LTEA',110,15),(eng,'ECE',9,0),(eng,'MAE',6,3),(eng,'SE',5,0),(eng,'BENG',2,1),(eng,'NANO',3,0),(health,'HDS',8,2),(health,'PH',10,0),(theatre,'THEA',35,2),(env,'ENVR',6,0),(env,'ESYS',4,2),(inter,'MGT',7,1),(inter,'INTL',4,0),(inter,'CLAS',3,0),(inter,'HMNR',2,0),(inter,'LAWS',1,0),(inter,'CCS',1,0),(area,'AAS',11,0),(area,'LATI',14,2),(area,'RELI',8,2),(area,'JWSP',9,0)])
def test_composed_source_replays_approved_metadata_only(module,subject,count,dispositions):
    s=module.SPEC['sources'][subject];p=Path(s['cache_path'])
    if not p.exists():pytest.skip('Optional ignored official chapter capture')
    a=importlib.import_module('atlas.adapters.'+PID+'.adapter')
    assert a.SOURCES.count(s['url'])==1
    r=a.SOURCE_PARSERS[s['url']](p.read_text())
    assert len(r['courses'])==count and len(r['source_dispositions'])==dispositions
    assert len({c['id']for c in r['courses']})==count
    saved={c['id']:c for c in json.loads(Path('data/programs',PID+'.json').read_text())['courses']}
    for c in r['courses']:
        assert 'category_review'not in c
        assert all(saved[c['id']][k]==v for k,v in c.items()if k!='notes')
        assert set(c['notes'])<=set(saved[c['id']]['notes'])


def test_music_study_and_cultural_ai_remain_conditional_content():
    d=json.loads(Path('data/programs',PID+'.json').read_text());cs={c['code']:c for c in d['courses']}
    assert cs['CGS 108']['category']=='human_context'
    assert cs['MUS 132R']['name']=='Recital Preparation'
    assert 'audition' in cs['MUS 132R']['prerequisites']
    assert cs['MUS 199']['credits']is None
    assert cs['MUS 160B']['category_review']['status']=='unclassified'
    assert 'music and ICAM majors only' in cs['MUS 160B']['prerequisites']
    assert any('Two production-course limitation' in n for n in cs['MUS 160B']['notes'])
    for code in ['MUS 8GS','MUS 19R','MUS 20R','MUS 126R','MUS 150GS','MUS 13AS']:
        assert cs[code]['category_review']['status']=='unclassified'


def test_biology_global_health_eligibility_and_identity_limits():
    d=json.loads(Path('data/programs',PID+'.json').read_text());cs={c['code']:c for c in d['courses']}
    assert cs['BICD 136']['prerequisites']=='BILD 1, BILD 2 recommended.'
    assert cs['BISP 182']['credits']is None and cs['BISP 193']['credits']is None
    assert cs['GLBH 107']['category_review']['status']=='unclassified'
    assert 'Refugee Health' in cs['GLBH 107']['name']
    assert cs['GLBH 111']['prerequisites']is None
    assert any('border' in n for n in cs['GLBH 111']['notes'])
    assert cs['GLBH 150B']['prerequisites']=='GLBH 150A; department approval required.'
    assert any('strictly enforces' in n for n in cs['BILD 10']['notes'])
    assert not any('lab-specific' in n for n in cs['BILD 10']['notes'])


def test_history_source_conflicts_keep_individual_amounts_and_held_subjects():
    d=json.loads(Path('data/programs',PID+'.json').read_text());cs={c['code']:c for c in d['courses']}
    assert cs['HITO 193']['credits']==6
    assert cs['POLI 194']['credits']==cs['USP 194']['credits']==4
    for code in ['HITO 193','POLI 194','USP 194']:
        assert any('Cross-source credit conflict' in n for n in cs[code]['notes'])
    assert cs['HISA 199']['credits']is None
    assert any('pool' in n.lower() and '4units' in n for n in cs['HISA 199']['notes'])
    assert cs['HISC 144']['category_review']['status']=='unclassified'
    assert 'South Asian' in cs['HISC 144']['category_review']['rationale']
    assert cs['HINE 116']['category_review']['status']=='unclassified'


def test_language_half_units_and_physics_scope_are_preserved():
    d=json.loads(Path('data/programs',PID+'.json').read_text());cs={c['code']:c for c in d['courses']}
    assert cs['LISP 1A']['credits']==cs['LISP 1AX']['credits']==2.5
    assert any('LISP 1AX' in n for n in cs['LISP 1A']['notes'])
    assert cs['LIHL 112']['category_review']['status']=='unclassified'
    assert any('112F' in n for n in cs['LIHL 112']['notes'])
    assert cs['LIHL 118']['category_review']['status']=='reviewed'
    assert cs['PHYS 1A']['credits']==3
    assert any('separate terms' in n for n in cs['PHYS 1A']['notes'])
    assert 'Corequisites: MATH 10B or 20B.' in cs['PHYS 11']['prerequisites']
    assert cs['ASTR 150']['category_review']['status']=='unclassified'
    assert cs['ASTR 154']['credits']==5
    assert set(cs['ASTR 154']['category_review']['candidate_categories'])=={'mathematics','ai_ml'}


def test_chemistry_directional_credit_and_positive_counterpart_evidence():
    d=json.loads(Path('data/programs',PID+'.json').read_text());cs={c['code']:c for c in d['courses']}
    assert cs['CHEM 117']['category_review']['status']=='mixed'
    assert cs['CHEM 172']['prerequisites']=='CHEM 6C or 6CH.'
    assert any('CHEM 171 is recommended preparation' in n for n in cs['CHEM 172']['notes'])
    assert any('May receive credit for CHEM 6CH after CHEM 6C' in n for n in cs['CHEM 6CH']['notes'])
    assert any('Positive counterpart evidence' in n for n in cs['SIO 141']['notes'])
    assert cs['CHEM 15']['category_review']['status']=='unclassified'


def test_literature_engineering_scope_and_holds_survive_integration():
    d=json.loads(Path('data/programs',PID+'.json').read_text());cs={c['code']:c for c in d['courses']}
    assert cs['LTCS 108']['category']=='human_context'
    assert cs['LTSP 166']['category']=='applications'
    assert 'or consent' in cs['LTFR 123']['prerequisites']
    assert 'LTFR 104' in cs['LTFR 123']['prerequisites']
    assert cs['LTIT 12AR']['prerequisites'] is None
    assert cs['LTAM 110GS']['name']=='Latino/a Literature in Translation'
    assert cs['LTAM 110GS']['category_review']['status']=='unclassified'
    assert cs['LTWR 126']['description'] is None
    assert any('renumbered' in n for n in cs['LTWR 126']['notes'])
    assert cs['LTWL 199']['credits'] is None
    assert cs['BENG 196']['credits'] is None and cs['ECE 193H']['credits'] is None
    assert cs['ECE 25']['prerequisites']=='none.'
    assert cs['MAE 190']['name']=='Digital Storytelling: Dynamic STEM Communication'
    assert cs['MAE 118']['category_review']['status']=='unclassified'
    assert 'immediately preceding quarter' in cs['MAE 156B']['prerequisites']
    assert any('not imposed as AI-degree graduation' in n for n in cs['MAE 156B']['notes'])
    assert [requirement_profile(d)[k]['count']for k in ['required','options','unresolved']]==[8,119,2241]


def test_health_environment_and_performance_conditions_are_not_universal_rules():
    d=json.loads(Path('data/programs',PID+'.json').read_text());cs={c['code']:c for c in d['courses']}
    assert cs['PH 102']['category']=='mathematics'
    assert cs['PH 193']['category_review']['status']=='unclassified'
    assert 'senior public health majors only' in cs['PH 193']['prerequisites']
    assert cs['HDS 194A']['credits']==cs['HDS 194C']['credits']==4
    assert cs['HDS 191']['credits']==6
    assert any('one academic year' in n for n in cs['HDS 191']['notes'])
    assert cs['TDPF 163']['credits'] is None
    assert 'concurrent enrollment' in cs['TDPF 163']['prerequisites']
    assert cs['ENVR 144']['credits']==2
    assert any('noncredit' in n.lower().replace('-','') for n in cs['ENVR 144']['notes'])
    assert cs['MGT 12']['name']=='Principles of Accounting'
    assert cs['MGT 12']['category_review']['status']=='unclassified'
    assert cs['LATI 175']['category']=='applications'
    assert cs['LATI 150']['category']=='human_context'
    assert cs['AAS 170']['credits']==cs['AAS 170R']['credits']==4
    assert cs['AAS 198']['credits'] is None
    assert cs['ESD 119']['description'] is None
    assert cs['ESD 119']['category_review']['status']=='unclassified'
    assert 'Neither source explicitly' in cs['ESD 119']['category_review']['rationale']
