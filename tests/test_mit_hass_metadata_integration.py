"""Approved departmental evidence enriches rows without new review certification."""
import importlib
import json
from pathlib import Path

import pytest

m = importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.hass_metadata')


def test_changed_actual_panel_cannot_replay_saved_metadata(monkeypatch):
    html = '''<h1>Classes</h1><div class="expcol-wrap">
    <div class="field--name-field-subject-number">4.123</div>
    <div class="faux-full-title">Test Studio</div>
    <div class="field--name-field-subject-description">Original studio work.</div>
    </div>'''
    observation = m.observer.observe_architecture(html)[0]
    url = 'https://architecture.mit.edu/example'
    review = dict(source_url=url, source_id='actual', approved_for_integration=True,
                  observation_digest=m.observer.observation_digest(observation),
                  category='applications', description_summary='Studio practice.',
                  prerequisites=None, credits=None, restrictions=[], catalog_year=None)
    monkeypatch.setattr(m, 'MANIFEST', {'courses': {'row': dict(
        listed_code='4.123', listed_name='Test Studio', listed_source_id='pool',
        review_status='reviewed', observations=[review])}})
    monkeypatch.setattr(m, 'INTEGRATED', {'course_ids': ['row']})
    monkeypatch.setattr(m, 'SPECS', {'actual': {'url': url, 'parser': 'architecture'}})
    parsed = m.parse(html, url)
    assert parsed['courses'][0]['id'] == 'row'
    assert parsed['courses'][0]['description'] == 'Studio practice.'
    assert parsed['courses'][0]['credits'] is None
    assert 'category_review' not in parsed['courses'][0]
    assert 'curriculum_audit' not in parsed
    assert m.parse(html.replace('Original studio work.', 'Changed studio scope.'), url)['courses'] == []


def test_integrated_evidence_preserves_term_rules_and_withholds_conflicts():
    p = json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by = {c['id']: c for c in p['courses']}
    integrated = [by[cid] for cid in m.INTEGRATED['course_ids']]
    assert len(integrated) >= 70
    assert all(c.get('description') and c.get('category_review') for c in integrated)
    assert {s['url'] for s in m.SPECS.values()} <= {s['url'] for s in p['sources']}
    greek = [c for c in integrated if c['code'] in {'21L.607', '21L.608'}]
    assert greek and all(c['credits'] == 6 for c in greek)
    assert any(r['id'] == 'mit-ai-hass-reviewed-language-bundles' and r['kind'] == 'note'
               for r in p['requirements'])
    undergraduate = next(c for c in integrated if c['code'] == '4.603')
    assert undergraduate['prerequisites'] is None
    held = {cid for cid, row in m.MANIFEST['courses'].items()
            if row['review_status'] in {'identity_review_needed', 'source_conflict'}}
    assert held.isdisjoint(m.INTEGRATED['course_ids'])


def test_actual_integrated_source_replay_has_exact_approved_identity_scope():
    paths = {sid: Path('/tmp/mit-hass-subjects') / m.INTEGRATED.get('cache_names', {}).get(
                sid, sid.removeprefix('mit-ai-hass-review-') + '.html')
             for sid in m.SPECS}
    if not all(p.exists() for p in paths.values()):
        pytest.skip('Optional ignored official source captures absent')
    rows = [c for sid, path in paths.items()
            for c in m.parse(path.read_text(), m.SPECS[sid]['url'])['courses']]
    assert {c['id'] for c in rows} == set(m.INTEGRATED['course_ids'])
    assert all('category_review' not in c for c in rows)


def test_current_cmsw_capture_does_not_certify_archived_term_records():
    path = Path('/tmp/mit-hass-subjects/cmsw-visible.html')
    if not path.exists():
        pytest.skip('Optional ordinary-browser visible source capture absent')
    url = m.SPECS['mit-ai-hass-review-cmsw-fall2026']['url']
    rows = m.parse(path.read_text(), url)['courses']
    assert rows
    assert all(c['source_id'] == 'mit-ai-hass-review-cmsw-fall2026' for c in rows)
    archived = {cid for cid in m.INTEGRATED['course_ids']
                if any(o['approved_for_integration'] and o['source_id'].endswith('cmsw-fall2025')
                       for o in m.MANIFEST['courses'][cid]['observations'])}
    assert archived and archived.isdisjoint({c['id'] for c in rows})
