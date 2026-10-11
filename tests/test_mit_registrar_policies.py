"""Policy boundaries use synthetic prose, not copied publisher pages."""
from importlib import import_module
from pathlib import Path
import hashlib
import json
import pytest
from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]
reg = import_module('atlas.adapters.mit-ai-decision-making-bs.registrar')
sup = import_module('atlas.adapters.mit-ai-decision-making-bs.supplement')


def test_flexible_pnr_includes_degree_requirements_but_not_exam_grades():
    html = '<h1>Flexible P/NR Grading Option</h1><main>Synthetic policy: up to 48 units after their first term. Any subject is eligible. Advanced Standing Examinations are not eligible. Designate before Add Date of your next enrolled regular term; seniors by the day before the CAP degree meetings.</main>'
    result = reg.parse('pnr', html)
    text = result['requirements'][0]['summary']
    assert 'including GIR and departmental requirements' in text
    assert 'D/F earn no credit' in text
    assert 'advanced-standing-exam grades cannot' in text
    with pytest.raises(ValueError):reg.parse('pnr', html.replace('48 units', '60 units'))
    with pytest.raises(ValueError):reg.parse('pnr', html.replace('<main>', '<nav>').replace('</main>', '</nav>'))
    assert not {'curriculum_status','curriculum_audit','last_verified'} & result.keys()


def test_optional_hass_route_retains_topic_identity_and_unknown_credits():
    html = '<main><h1>Computing and Society Concentration</h1><p>Four of any of the subjects listed below, selected in consultation with the Concentration Advisor. Include only one subject that also counts toward the HASS Distribution Requirement.</p><p>24.S00 Synthetic Topic A, HASS-H</p><p>24.S00 Synthetic Topic B, HASS-H</p><p>21A.311 Synthetic standard subject, HASS-S</p></main>'
    d = sup.parse_hass(html)
    assert len({c['id'] for c in d['courses']}) == 3
    assert all(c['credits'] is None for c in d['courses'])
    assert d['requirements'][1]['count'] == 4
    assert 'not an AI-major requirement' in d['requirements'][0]['summary']
    with pytest.raises(ValueError):sup.parse_hass(html.replace('Four of any','Three of any'))


def test_entrance_gateway_is_cohort_specific_and_repeat_forfeiture_is_conditional():
    html = '<main><h1>MIT Credit Policies at Entrance for Fall 2026</h1><p>Policy applies only to the Class of 2030 entering Fall 2026. Record grade of S; does not count toward term or cumulative averages. If you register for any version of that subject you will forfeit the credit. Restore only if you drop the registered subject by Add Date.</p></main>'
    d = sup.parse_ap_gateway(html)
    assert 'not automatically to every 6-4_2025 cohort' in d['requirements'][0]['summary']
    assert 'dropping by Add Date' in d['requirements'][0]['summary']
    with pytest.raises(ValueError):sup.parse_ap_gateway(html.replace('Fall 2026','Fall 2027'))


def test_curated_audit_distinguishes_prohibition_from_final_transfer_review():
    d=json.loads((ROOT/'data/programs/mit-ai-decision-making-bs.json').read_text())
    validate_program(d)
    assert d['curriculum_status']=='partial'
    assert not any('Distribution conflict' in gap or 'internal date conflict' in gap for gap in d['curriculum_audit']['unresolved_requirements'])
    rules={r['id']:r for r in d['requirements']}
    assert 'excludes external Distribution credit' in rules['mit-ai-registrar-hass-external']['summary']
    final=rules['mit-ai-registrar-transfer-hass-conflict']['summary']
    assert 'final signature' in final and 'neither grants an exception' in final
    assert 'individual approval' in final
    assert any('Fall2025' in gap and 'robots-disallowed' in gap for gap in d['curriculum_audit']['unresolved_requirements'])
    urls={s['url'] for s in d['sources']}
    assert set(reg.SOURCE_PARSERS)|set(sup.SOURCE_PARSERS) <= urls


@pytest.mark.parametrize('url,parser',list(reg.SOURCE_PARSERS.items())+list(sup.SOURCE_PARSERS.items()))
def test_optional_actual_source_cache_observation_has_no_review_claims(url,parser):
    cache=ROOT/'.cache/http'/(hashlib.sha256(url.encode()).hexdigest()+'.body')
    if not cache.exists():pytest.skip('Optional raw source cache not retained in repository')
    d=parser(cache.read_text())
    assert d['id']=='mit-ai-decision-making-bs'
    assert d['requirements']
    assert not {'curriculum_status','curriculum_audit','last_verified','first_offered','catalog_year'} & d.keys()


def test_transfer_recommendation_requires_final_review_and_is_not_an_exception():
    markers=[phrase for _,_,phrases,_ in reg.SPECS['transfer'][2] for phrase in phrases]
    html='<h1>Transfer credit</h1><main>'+'. '.join(markers)+'</main>'
    out=reg.parse('transfer',html)
    assert 'neither grants an exception' in out['requirements'][1]['summary']
    with pytest.raises(ValueError):
        reg.parse('transfer',html.replace('email hassreq@mit.edu for a final signature','examiner approval is final'))
    assert not {'curriculum_status','curriculum_audit','last_verified'} & out.keys()
