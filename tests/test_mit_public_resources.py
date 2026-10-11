"""Evidence links must not be advertised as course teaching websites."""
import importlib,json
from pathlib import Path
import pytest
m=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.public_resources')


def test_seed_resource_links_have_course_specific_manual_evidence():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by={c['id']:c for c in p['courses']};sources={s['id']:s for s in p['sources']}
    sites={c['id']:c['public_site']for c in p['courses']if c['public_site']}
    assert sites=={cid:r['public_site']for cid,r in m.REVIEWS.items()}
    assert len(sites)>=28
    for cid,r in m.REVIEWS.items():
        assert any(sources[sid]['url']==r['public_site']for sid in r['source_ids'])
        assert by[cid]['syllabus']==r['syllabus']
    assert by['mit-ai-6-1010']['public_site']is None
    assert by['mit-ai-6-1010']['url'] and by['mit-ai-6-1010']['category_review']['source_ids']
    assert by['mit-ai-6-8301']['public_site']=='https://advances-in-vision.github.io/'


def test_generic_source_cannot_activate_or_steal_teaching_resource():
    assert m.observed_resources('mit-ai-6-1010','https://eecsis.mit.edu/degree_requirements.pcgi?program=6-4')==dict(public_site=None,syllabus=None)
    assert m.observed_resources('different-course','https://advances-in-vision.github.io/')==dict(public_site=None,syllabus=None)
    assert m.observed_resources('mit-ai-6-8301','https://catalog.mit.edu/subjects/6/')==dict(public_site=None,syllabus=None)


def test_actual_reference_annotations_and_general_hass_panels_emit_no_course_sites():
    ref=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.reference_annotations')
    v=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.versioned')
    path=Path('/tmp/pilot-audit-mit-version.html')
    if not path.exists():pytest.skip('Optional ignored official capture absent')
    assert all(c['public_site']is None for c in ref.observe(v.parse(path.read_text())))
    h=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.hass_metadata')
    panel=Path('/tmp/mit-hass-subjects/cmsw-visible.html')
    if not panel.exists():pytest.skip('Optional visible departmental capture absent')
    rows=h.parse(panel.read_text(),'https://cmsw.mit.edu/mit_subject/')['courses']
    assert rows and all(c['public_site']is None and c['syllabus']is None for c in rows)


def test_actual_ocw_syllabus_observation_keeps_resource_semantics():
    h=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.hass_metadata')
    sid='mit-ai-hass-review-ocw-24-222-decisions-games-and-rational-choice-spring-2008'
    path=Path(h.INTEGRATED['cache_paths'][sid])
    if not path.exists():pytest.skip('Optional actual public OCW syllabus capture absent')
    url=h.SPECS[sid]['url'];rows=h.parse(path.read_text(),url)['courses']
    assert rows and all(c['public_site']==url and c['syllabus']==url for c in rows)


def test_political_syllabi_preserve_conditional_preparation_and_distinct_iap_version():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by={c['id']:c for c in p['courses']}
    congress=by['mit-ai-hass-political-subfields-17-251']
    assert '4 or 5' in congress['prerequisites']
    assert congress['syllabus'].endswith('system-i-fall-2016/pages/syllabus/')
    middle_east=by['mit-ai-hass-middle-eastern-studies-17-568']
    assert 'permission' in middle_east['prerequisites']
    assert any('advanced undergraduates' in n for n in middle_east['notes'])
    iap=by['mit-ai-hass-political-subfields-17-567']
    assert iap['credits']==9 and iap['description'] is None and iap['syllabus'] is None
    composite=by['mit-ai-hass-middle-eastern-studies-17-565-17-567']
    assert any('17.565 only' in n for n in composite['notes'])
    assert composite['syllabus'].endswith('identity-spring-2019/pages/syllabus/')


def test_history_homepage_is_course_site_without_synthesized_syllabus_fields():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by={c['id']:c for c in p['courses']}
    rome=by['mit-ai-hass-ancient-and-medieval-studies-21h-132']
    assert rome['public_site']=='https://ocw.mit.edu/courses/21h-132-the-ancient-world-rome-spring-2017/'
    assert rome['description'] and rome['prerequisites'] is None and rome['syllabus'] is None
    h=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.hass_metadata')
    sid='mit-ai-hass-review-ocw-21h-132-the-ancient-world-rome-spring-2017'
    path=Path(h.INTEGRATED['cache_paths'][sid])
    if not path.exists():pytest.skip('Optional actual public course homepage capture absent')
    rows=h.parse(path.read_text(),rome['public_site'])['courses']
    row=next(c for c in rows if c['id']==rome['id'])
    assert row['description']==rome['description']
    assert row['prerequisites'] is None and row['syllabus'] is None
