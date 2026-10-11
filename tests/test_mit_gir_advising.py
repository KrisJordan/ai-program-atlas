import hashlib
import importlib
import json
from pathlib import Path

import pytest

m = importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.gir_advising')


def test_public_syllabus_requires_actual_identity_term_and_reviewed_body(monkeypatch):
    html = '<title>Syllabus for 18.01L Calculus</title><p>Fall Term (AY 2026-2027)</p><div id="course_syllabus">Calculus welcome.</div>'
    review = dict(m.REVIEWS['18.01L'])
    review['digest'] = hashlib.sha256(m.observed(html, m.CALCULUS)['18.01L'].encode()).hexdigest()
    monkeypatch.setattr(m, 'REVIEWS', {'18.01L': review})
    c = m.parse(html, m.CALCULUS)['courses'][0]
    assert c['category'] == 'mathematics' and c['syllabus'] == m.CALCULUS
    assert c['credits'] is None and c['prerequisites'] is None
    assert 'category_review' not in c
    changed = m.parse(html.replace('Calculus welcome.', 'Different content.'), m.CALCULUS)['courses'][0]
    assert changed['category'] == 'other' and changed['description'] is None
    with pytest.raises(ValueError):
        m.parse(html.replace('2026-2027', '2027-2028'), m.CALCULUS)


def test_physics_conditional_credit_and_prerequisites_do_not_change_fixed_roles():
    p = json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by = {c['code']: c for c in p['courses'] if c['id'].startswith('mit-ai-gir-')}
    assert by['8.012']['credits'] == 12
    assert any('six elective units' in n for n in by['8.012']['notes'])
    assert by['8.012']['prerequisites'] is None
    assert by['8.02']['prerequisites'] == 'Credit for both 8.01 and 18.01 (Calculus I).'
    assert by['8.021']['category_review']['status'] == 'unclassified'
    assert by['8.021']['name'] is None
    physics_notes = [r for r in p['requirements'] if r['id'].startswith('mit-ai-gir-advising-8-')]
    assert len(physics_notes) == 2 and all(r['kind'] == 'note' for r in physics_notes)
    assert not any(c['category'] == 'foundations' for c in by.values())


def test_actual_public_sources_replay_seven_bounded_observations():
    paths = {m.SCIENCE: Path('/tmp/mit-science-core.html'), m.CALCULUS: Path('/tmp/mit-canvas-syllabus.html')}
    if not all(p.exists() for p in paths.values()):
        pytest.skip('Optional ignored actual source cache absent')
    rows = [c for url, path in paths.items() for c in m.parse(path.read_text(), url)['courses']]
    assert len(rows) == 7
    assert all(c['description'] and 'category_review' not in c for c in rows)
