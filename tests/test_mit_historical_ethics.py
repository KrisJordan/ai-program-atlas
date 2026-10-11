import importlib
from pathlib import Path
import pytest
m=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.historical_ethics')


def test_no_cached_dependency_or_single_payload_fallback():
    with pytest.raises(ValueError,match='both source payloads'):m.parse_sources({m.ARCHIVE_ID:'actual archive'})
    with pytest.raises(ValueError,match='empty'):m.parse_sources({m.ARCHIVE_ID:'actual archive',m.NUMBERING_ID:''})


def test_two_actual_sources_bind_only_dated_metadata():
    archive=Path('/tmp/mit-hass-subjects/ocw-24-231-ethics-fall-2009-syllabus.html')
    numbering=Path('/tmp/mit-hass-subjects/philosophy-undergraduate.html')
    if not archive.exists()or not numbering.exists():pytest.skip('Optional ignored dual-source captures absent')
    payloads={m.ARCHIVE_ID:archive.read_text(),m.NUMBERING_ID:numbering.read_text()}
    out=m.parse_sources(payloads);c=out['courses'][0]
    assert c['code']=='24.130' and c['credits']is None
    assert c['prerequisites']=='The prerequisites for this course include one philosophy course.'
    assert any('Fall2009' in n and 'no current' in n for n in c['notes'])
    assert c['public_site']is None and c['syllabus']is None
    assert 'category_review'not in c and 'curriculum_audit'not in out
    with pytest.raises(ValueError,match='former-number'):
        m.parse_sources({**payloads,m.NUMBERING_ID:payloads[m.NUMBERING_ID].replace('formerly 24.231','formerly 24.999')})


def test_contradictory_numbering_cannot_hide_behind_valid_row(monkeypatch):
    heading='<h1>Welcome to the MIT Philosophy Undergraduate Program</h1>'
    valid='<p>24.130 Ethics (CI-M) (formerly 24.231)</p>'
    monkeypatch.setattr(m.observer,'observe_philosophy_renumbered_ethics',lambda *_:['observed'])
    assert m.observe_sources({m.ARCHIVE_ID:'archive',m.NUMBERING_ID:heading+valid})==['observed']
    for contradiction in ['24.130 Ethics (CI-M) (formerly 24.999)',
                          '24.999 Another Subject (formerly 24.231)',
                          '24.130 Another Subject (formerly 24.231)']:
        with pytest.raises(ValueError,match='contradictory'):
            m.observe_sources({m.ARCHIVE_ID:'archive',m.NUMBERING_ID:heading+valid+'<p>'+contradiction+'</p>'})


def test_single_source_wrapper_reports_missing_dependency():
    wrapper=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.hass_metadata')
    out=wrapper.parse('Any archive content',m.SOURCES[0])
    assert out['courses']==[]
    assert out['observed_hass_dependency_gaps'][0]['missing_source_ids']==[m.NUMBERING_ID]
    assert wrapper.SOURCE_PARSERS[m.SOURCES[0]]('Any archive content')['courses']==[]


def test_explicit_wrapper_dependency_replays_only_matching_historical_content():
    wrapper=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.hass_metadata')
    archive=Path('/tmp/mit-hass-subjects/ocw-24-231-ethics-fall-2009-syllabus.html')
    numbering=Path('/tmp/mit-hass-subjects/philosophy-undergraduate.html')
    if not archive.exists()or not numbering.exists():pytest.skip('Optional ignored dual-source captures absent')
    sources={m.NUMBERING_ID:numbering.read_text()}
    out=wrapper.parse(archive.read_text(),m.SOURCES[0],source_payloads=sources)
    assert [c['id']for c in out['courses']]==[m.COURSE_ID]
    assert out['observed_hass_dependency_gaps']==[]
    assert 'category_review'not in out['courses'][0]
    changed=archive.read_text().replace('moral','altered')
    assert changed!=archive.read_text()
    assert wrapper.parse(changed,m.SOURCES[0],source_payloads=sources)['courses']==[]
