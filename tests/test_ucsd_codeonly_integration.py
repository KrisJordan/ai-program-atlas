"""Primary integration checks; source helpers retain their own full-block guards."""
import importlib
import json
from pathlib import Path

PID='university-of-california-san-diego-artificial-intelligence-bs-degree'
MODULES=('ucsd_math_remaining_reviews','ucsd_cogs_remaining_reviews','ucsd_ltsp_remaining_reviews','ucsd_codeonly_language_reviews','ucsd_performance_remaining_reviews','ucsd_codeonly_social_reviews','ucsd_codeonly_science_reviews','ucsd_linguistics_remaining_reviews','ucsd_computing_design_remaining_reviews','ucsd_codeonly_humanities_reviews')


def test_initial_codeonly_batches_are_disjoint_and_actual_dispositions():
    courses={c['id']:c for c in json.loads(Path('data/programs',PID+'.json').read_text())['courses']}
    entries=[e for name in MODULES for e in importlib.import_module('atlas.adapters.'+name).SPEC['entries']]
    assert len(entries)==652 and len({e['id']for e in entries})==652
    assert sum(e['approved_for_integration']for e in entries)==605
    for entry in entries:
        c=courses[entry['id']]
        assert 'not a review of course content'not in c['category_review']['rationale']
        if entry['approved_for_integration']:
            assert c['description']==entry['description']
            assert c['category_review']==entry['category_review']
        else:
            assert c['description']is None
            assert c['category_review']['status']=='unclassified'


def test_conditional_units_section_scopes_and_exact_identities():
    d=json.loads(Path('data/programs',PID+'.json').read_text());cs={c['code']:c for c in d['courses']}
    assert cs['COMM 101']['credits']==6
    assert cs['ENG 10']['credits']==cs['ENG 15']['credits']==2
    assert cs['MUS 80']['credits']is None
    assert all(cs['MUS 2'+suffix]['credits']==4 for suffix in 'ABC')
    assert 'Music majors' in cs['MUS 2A']['prerequisites']
    assert 'TDMV 138' in cs['TDMV 148']['prerequisites']
    assert cs['FILM 71']['code']=='FILM 71'
    assert next(s for s in d['sources']if s['id']==cs['CSS 2']['source_id'])['catalog_year']=='2023–24'
    assert cs['MUS 127']['category']==cs['ETHN 179']['category']=='human_context'
    assert all(cs[code]['description']is None for code in ['MATH 15A','MAE 8','DSC 131','MUS 10'])
    assert cs['LIGN 167']['category']=='ai_ml'


def test_final_queue_and_section_policy_correction_are_explicit():
    d=json.loads(Path('data/programs',PID+'.json').read_text());cs={c['code']:c for c in d['courses']}
    assert not any('not a review of course content' in c.get('category_review',{}).get('rationale','') for c in cs.values())
    assert not any('metadata is unreviewed' in gap for gap in d['curriculum_audit']['metadata_gaps'])
    assert 'Section preparation rule' in cs['ETHN 110']['prerequisites']
    assert 'upper-division standing or consent' in cs['ETHN 110']['prerequisites']
    assert 'lower-division political science' in cs['POLI 100H']['prerequisites']
    assert 'Section preparation rule' not in (cs['POLI 5']['prerequisites'] or '')
    assert cs['JWSP 1']['credits']==5
    assert cs['SYN 100']['category_review']['status']=='unclassified'
    assert 'Seventh College' in cs['SYN 100']['prerequisites']
