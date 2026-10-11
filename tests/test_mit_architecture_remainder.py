import importlib
import json
from pathlib import Path

import pytest

m = importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.architecture_remainder')


def test_art_foundations_are_not_computing_and_broad_titles_stay_unknown():
    p = json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by = {c['id']: c for c in p['courses']}
    assert len(m.MANIFEST['courses']) == 58
    studio = by['mit-ai-hass-architecture-design-pdf-4-302']
    assert studio['category'] == 'applications'
    assert studio['description'] is None
    assert studio['category_review']['rationale'].startswith('Limited official-title-only')
    assert by['mit-ai-hass-architecture-design-pdf-4-02a']['credits'] == 9
    assert by['mit-ai-hass-architecture-htc-pdf-4-605']['category'] == 'human_context'
    unknown = by['mit-ai-hass-middle-eastern-studies-4-616']
    assert unknown['category_review']['status'] == 'unclassified' and unknown['category'] == 'other'
    assert any('qualified undergraduates' in n for n in unknown['notes'])
    assert all(by[cid].get('category_review') for cid in m.MANIFEST['courses'])


def test_changed_source_cannot_reuse_title_judgment(monkeypatch):
    saved = next(iter(m.MANIFEST['courses'].values()))
    cid = next(iter(m.MANIFEST['courses']))
    row = dict(id=cid, code=saved['code'], name=saved['name'], source_id=saved['source_id'], category='human_context')
    out = m.enrich({'courses': [row]}, 'Changed actual source', saved['source_url'])
    assert out['courses'][0]['category'] == 'other'
    assert 'category_review' not in out['courses'][0]


def test_actual_sources_replay_exact_scope_without_adding_reviews():
    if not all(Path(s['cache_path']).exists() for s in m.MANIFEST['sources'].values()):
        pytest.skip('Optional ignored source captures absent')
    seen = set()
    adapter = importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.adapter')
    for url, source in m.MANIFEST['sources'].items():
        text = Path(source['cache_path']).read_text()
        before = m.source_parse(url, text)
        after = adapter.SOURCE_PARSERS[url](text)
        assert after['requirements'] == before['requirements']
        for c in after['courses']:
            if c['id'] in m.MANIFEST['courses']:
                seen.add(c['id'])
                assert c['category'] == m.MANIFEST['courses'][c['id']]['category']
                assert 'category_review' not in c
    assert seen == set(m.MANIFEST['courses'])
    assert len(adapter.SOURCES) == len(set(adapter.SOURCES))
