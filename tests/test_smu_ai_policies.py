"""Published policy scope, changed rules, and manually reviewed local audits."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from atlas import db
from atlas.adapters import smu_ai_policies as p

ROOT = Path(__file__).resolve().parents[1]


def page_fixture(name='Example school', tab_name='Eligibility', body='<h2>Eligibility</h2><p>Current reviewed condition.</p>', published=True, temporary=None):
    """Small synthetic Nuxt reference graph; no copied catalog payload."""
    values = []
    def add(value):
        values.append(value)
        return len(values) - 1
    item = add({'name': add(tab_name), 'content': add(body)})
    widget = add({'type': add('tabs'), 'data': add([item])})
    add({'name': add(name), 'published': add(published), 'widgets': add([widget]), 'temporaryContent': add(temporary)})
    return '<main><h1>' + name + '</h1></main><script id="__NUXT_DATA__" type="application/json">' + json.dumps(values) + '</script>'


def test_only_current_published_named_tab_is_evidence():
    html = page_fixture(temporary='<h2>Eligibility</h2><p>Draft unrelated rule.</p>')
    body = p.tab(html, 'Example school', 'Eligibility')
    assert 'Current reviewed condition' in body.get_text()
    assert 'Draft unrelated' not in body.get_text()
    with pytest.raises(ValueError):
        p.tab(page_fixture(published=False), 'Example school', 'Eligibility')
    with pytest.raises(ValueError):
        p.tab(page_fixture(tab_name='Other tab'), 'Example school', 'Eligibility')
    with pytest.raises(ValueError):
        p.tab(page_fixture(body='<h2>Wrong section</h2>'), 'Example school', 'Eligibility')
    with pytest.raises(ValueError):
        p.tab(page_fixture(), 'Other school', 'Eligibility')


def test_draft_or_navigation_cannot_supply_missing_tab():
    html = page_fixture(tab_name='Other tab', temporary='<h2>Eligibility</h2>Current condition')
    with pytest.raises(ValueError):
        p.tab(html, 'Example school', 'Eligibility')
    with pytest.raises(ValueError):
        p.tab('<nav>'+page_fixture()+'</nav><main><h1>Different</h1></main>', 'Example school', 'Eligibility')
    with pytest.raises(ValueError):
        p.tab('<h1>Access denied</h1>'+page_fixture(), 'Example school', 'Eligibility')
    with pytest.raises(ValueError):
        p.tab('<input type="password">'+page_fixture(), 'Example school', 'Eligibility')


def test_changed_policy_clause_requires_review():
    body = p.tab(page_fixture(body='<h2>Eligibility</h2><p>Minimum GPA 2.500, subject to approval.</p>'), 'Example school', 'Eligibility')
    assert p.require(body, 'Minimum GPA 2.500', 'subject to approval')
    with pytest.raises(ValueError):
        p.require(body, 'Minimum GPA 3.000')


@pytest.mark.parametrize('url,parser', p.SOURCE_PARSERS.items())
@pytest.mark.parametrize('key', ['smu-ba', 'smu-bs'])
def test_optional_reviewed_policy_replay(url, parser, key):
    path = ROOT/'.cache/http'/(hashlib.sha256(url.encode()).hexdigest()+'.body')
    if not path.exists():
        pytest.skip('Optional ignored source capture absent')
    html = path.read_text()
    observed = parser(html, key)
    assert observed['id'] == p.CONFIG[key][0]
    assert len(observed['requirements']) >= 3
    assert all(r['source_id'].startswith(observed['id']) for r in observed['requirements'])
    assert not {'curriculum_audit','last_verified','curriculum_status'} & observed.keys()
    with pytest.raises(ValueError):
        parser('<h1>Access denied</h1>'+html, key)
    # Change a material condition in the actual current publication, not a seed.
    before, after = {
        p.PROGRESS: ('75 credit hours', '90 credit hours'),
        p.LYLE: ('2.500 and C-', '3.500 and C-'),
        p.GRADES: ('up to six courses', 'up to eight courses'),
        p.TRANSFER: ('no more than 30 credit hours', 'no more than 45 credit hours'),
    }[url]
    assert before in html
    with pytest.raises(ValueError):
        parser(html.replace(before, after), key)


@pytest.mark.parametrize('key', ['smu-ba', 'smu-bs'])
def test_local_complete_audit_preserves_scope_and_registered_sources(key):
    pid = p.CONFIG[key][0]
    seed = json.loads((ROOT/'data/programs'/(pid+'.json')).read_text())
    db.validate_program(seed)
    assert seed['curriculum_status'] == 'complete'
    audit = seed['curriculum_audit']
    assert audit['scope'] == 'concentration'
    assert not audit['unresolved_requirements'] and audit['metadata_gaps']
    assert len(seed['courses']) == 2
    assert seed['first_offered'] is None
    assert all(r['source_id'] in audit['source_ids'] for r in seed['requirements'])
    assert any('entire host Computer Science degree' in n for n in seed['notes'])
    relationship = next(r for r in seed['requirements'] if r['id'].endswith('-credential-relationship'))
    assert ('appears on the transcript but not diploma' if key == 'smu-bs' else 'appears on neither transcript nor diploma') in relationship['summary']
    spec = importlib.util.spec_from_file_location(pid, ROOT/'atlas/adapters'/pid/'adapter.py')
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    assert set(adapter.SOURCES) <= {s['url'] for s in seed['sources']}
    assert set(p.SOURCE_PARSERS) <= adapter.SOURCE_PARSERS.keys()
