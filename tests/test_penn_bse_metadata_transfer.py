"""BSE shares course evidence without inheriting concentration rules or dates."""
import hashlib
import json
from pathlib import Path
from atlas import db
from atlas.adapters.penn_bse import adapter
from atlas.adapters.penn_cs.course_metadata import RESOURCE_SPECS


def test_bse_enrichment_preserves_scope_and_missingness():
    p=json.loads(Path('data/programs/penn-bse-ai.json').read_text())
    db.validate_program(p)
    assert p['curriculum_status']=='partial'
    by={c['code']:c for c in p['courses']}
    assert by['CIS 5190']['category']=='electives'
    for code in ['CIS 4190','CIS 5190','CIS 4210','CIS 5210','CIS 5200']:
        assert by[code]['description'] and by[code]['public_site']
        assert by[code]['credits'] is None
    for code,term in [('CIS 4210','Fall 2022'),('CIS 5200','Spring 2023')]:
        assert term in by[code]['description']
        assert by[code]['prerequisites'] is None
    assert set(adapter.SOURCES)<={s['url'] for s in p['sources']}


def test_source_dispatch_uses_bse_identity_and_actual_text():
    url='https://www.engineering.upenn.edu/~cis5190/fall2026/index.html'
    html='<h1>CIS 4190/5190 Fall 2026</h1><p>Prerequisites: Changed preparation criterion</p><h2>Syllabus</h2>'
    out=adapter.SOURCE_PARSERS[url](html)
    assert out['id']=='penn-bse-ai'
    assert {c['code'] for c in out['courses']}=={'CIS 4190','CIS 5190'}
    assert all(c['prerequisites']=='Changed preparation criterion' for c in out['courses'])
    assert out['requirements']==[]
    assert 'curriculum_audit' not in out and 'last_verified' not in out


def test_cached_observations_never_certify_bse():
    import pytest
    for url in RESOURCE_SPECS:
        path=Path('.cache/http')/(hashlib.sha256(url.encode()).hexdigest()+'.body')
        if not path.exists():pytest.skip('Optional local cache absent')
        out=adapter.SOURCE_PARSERS[url](path.read_text())
        assert out['id']=='penn-bse-ai' and out['curriculum_status']=='partial'
        assert not out['requirements'] and 'curriculum_audit' not in out
