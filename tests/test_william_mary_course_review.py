import hashlib
import json
from pathlib import Path
from html import escape
import pytest
from atlas import db
from atlas.adapters import william_mary_course_review as m
from atlas.curriculum_profile import requirement_profile


def example(monkeypatch):
    description='An invented AI model evaluation course.'
    restriction='Prerequisite: EX 100 or instructor approval.'
    e=dict(id='wm-applied-ai-data-201',url='https://registration.wm.edu/?details&srcdb=202710&crn=12345',title='Example AI',section='Section 01, CRN 12345',description_digest=hashlib.sha256(description.encode()).hexdigest(),restriction_digest=hashlib.sha256(restriction.encode()).hexdigest(),credits=3,category='ai_ml',description='Invented model evaluation content.')
    monkeypatch.setattr(m,'SPEC',{'DATA 201':e})
    return '<div class="panel__content"><div class="panel__head"><a class="deep-link" data-query-string="?details&amp;srcdb=202710&amp;crn=12345"></a></div><div class="dtl-course-code">DATA 201</div><div class="dtl-section">Section 01, CRN 12345</div><div class="detail-title">Example AI</div><div class="detail-hours_html">3 Credit Hours</div><div class="detail-grade_mode">Grade Mode: Standard Letter</div><div class="section--description"><div class="section__content">'+description+'</div></div><div class="section--registration_restrictions"><div class="section__content">'+restriction+'</div></div></div>'


def test_only_actual_guarded_panel_supplies_observation(monkeypatch):
    html=example(monkeypatch);o=m.parse(html,'DATA 201');c=o['courses'][0]
    assert c['credits']==3 and c['credit_unit']=='unknown'
    assert c['prerequisites']=='Prerequisite: EX 100 or instructor approval.'
    assert 'category_review' not in c and 'curriculum_audit' not in o
    for before,after in [('202710','202610'),('Example AI','New topic'),('3 Credit Hours','4 Credit Hours'),('model evaluation','unrelated methods'),('or instructor','and instructor')]:
        with pytest.raises(ValueError):m.parse(html.replace(before,after),'DATA 201')
    for bad in ['<h1>W&M Class Search</h1>',html+html,'<h1>Sign in</h1>']:
        with pytest.raises(ValueError):m.parse(bad,'DATA 201')


def test_actual_rendered_panels_when_available():
    p=Path('/tmp/atlas-wm-current-courses.json')
    if not p.exists():pytest.skip('Ignored actual rendered public panels unavailable')
    caps=json.loads(p.read_text());assert len(caps)==3
    for cap in caps:
        c=m.parse(cap['html'],cap['code'])['courses'][0]
        assert c['credits']==3 and c['description'].startswith('Fall 2026')
        assert c['source_id'].startswith(m.PID+'-path-')


def test_reviewed_three_course_scope_does_not_resolve_degree_identity():
    p=json.loads(Path('data/programs',m.PID+'.json').read_text());db.validate_program(p)
    c={c['code']:c for c in p['courses']}
    assert len(c)==10 and p['curriculum_status']=='partial'
    assert {k:c[k]['category'] for k in ['DATA 201','DATA 202','DATA 305']}=={'DATA 201':'ai_ml','DATA 202':'human_context','DATA 305':'ai_ml'}
    assert all(c[k]['credits']==3 for k in ['DATA 201','DATA 202','DATA 305'])
    assert c['DATA 305']['credit_unit']=='unknown'
    assert all(c[k]['category_review']['status']=='reviewed' for k in ['DATA 201','DATA 202','DATA 305'])
    assert 'minimum grade of D-' in c['DATA 305']['prerequisites']
    assert 'Prerequisite' not in c['DATA 202']['prerequisites']
    assert p['first_offered'] is None
    assert any('AAI 301' in x for x in p['curriculum_audit']['unresolved_requirements'])
    profile=requirement_profile(p)
    assert profile['required']['categories']['ai_ml']==1
    assert profile['options']['categories']['human_context']==1
