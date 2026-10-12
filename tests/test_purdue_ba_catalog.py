"""Current BA catalog choices must survive refresh without stale-source promotion."""
import copy
import hashlib
import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from bs4 import BeautifulSoup

from atlas import db
from atlas.adapters import purdue_ba_catalog as catalog
from atlas.curriculum_profile import requirement_profile
from atlas.http import FetchResult
from atlas.scrape import scrape_one


def fixture(monkeypatch):
    # Synthetic markup: no copied catalog page or descriptions in version control.
    sections = [('Area A: Required Courses (16 credits)', ['PHIL 25601','PHIL 30000','PHIL 31400','PHIL 32300','PHIL 41400']),
                ('Area B: Required Computer Science Courses (20-22 credits)', ['CS 17600','CS 18000','CS 18200','CS 24300','CS 36100','MA 16010','MA 16020','MA 16100','MA 16500']),
                ('Ethics/ Value Theory (3 credits)', ['PHIL 20700','PHIL 20800']),
                ('History of Philosophy (3 credits)', ['PHIL 30100','PHIL 30200','PHIL 30300','PHIL 30400','PHIL 30600','PHIL 31000']),
                ('Philosophy of Science, Tech, and Mathematics (3 credits)', ['PHIL 22100','PHIL 32200','PHIL 35000','PHIL 42100','PHIL 55300']),
                ('Area D: Breadth Requirement (3 credits)', ['AD 22000','AD 26700','AD 32600','ANTH 21000','COM 25100','COM 41500','ENGL 22300','ENGL 32001','ENGL 42100','ENGL 42400','HIST 28400','HIST 30701','HIST 30705','HIST 38506','POL 22800','POL 25801','SOC 34400','SOC 38100']),
                ('Area E: Research Requirement (3 credits)', ['PHIL 41500'])]
    spec = copy.deepcopy(catalog.CONTENT)
    html = '<h1>Artificial Intelligence, BA</h1><p>2026-2027 University Catalog</p><div class="acalog-core"><h2>Degree Requirements</h2><h3>120 Credits Required</h3></div><div class="acalog-core"><h2>Departmental/Program Major Course Requirements (51-53 credits)</h2></div>'
    for heading, codes in sections:
        html += '<div class="acalog-core"><h3>'+heading+'</h3><ul>'
        for i, code in enumerate(codes):
            if code in ['MA 16100','MA 16500']:html += '<li class="acalog-adhoc">OR</li>'
            credits = '1.00 to 3.00' if code == 'PHIL 41500' else '4.00' if code in ['CS 18000','PHIL 32300','MA 16500'] else '5.00' if code == 'MA 16100' else '3.00'
            html += f'''<li class="acalog-course"><a onclick="showCatalogData('19', '3', '{100+i}', '', this)">{code} - Synthetic subject</a> Credit Hours: {credits} {'and' if code == 'MA 16010' else ''}</li>'''
        html += '</ul></div>'
    headings = ['Note for Areas C & D','Other Departmental - Liberal Arts Core (35-76 credits)','Core I: Disciplinary Diversity (6-18 credits)','Core II: Social Diversity (1-3 credits)','Core III: Linguistic Diversity (8-16 credits)','Foundational Requirements (21-36 credits)','Notes','Electives (0-34 credits)','GPA Requirements','Course Requirements and Notes','College of Liberal Arts Pass/No Pass Option Policy','University Core Requirements','Civics Literacy Proficiency Requirement','Upper Level Requirement','Pre-Requisite Information','World Language Courses']
    for key, heading in zip(spec['_policies'], headings):
        node = '<div class="acalog-core"><h3>'+heading+'</h3><p>Synthetic policy.</p></div>'
        spec['_policies'][key]['content_hash'] = hashlib.sha256(catalog.text(BeautifulSoup(node,'html.parser')).encode()).hexdigest()
        html += node
    outcome = '<div class="acalog-core"><h2>Program Learning Outcomes</h2><p>Synthetic learning outcome.</p></div>'
    spec['_outcome_hash'] = hashlib.sha256(catalog.text(BeautifulSoup(outcome,'html.parser')).encode()).hexdigest()
    monkeypatch.setattr(catalog, 'CONTENT', spec)
    return html + outcome


def test_catalog_bundle_and_practicum_are_not_flattened(monkeypatch):
    html = fixture(monkeypatch)
    p = catalog.parse(html)
    profile = requirement_profile(p, include_course_ids=True)
    assert profile['required']['count'] == 11
    assert profile['options']['count'] == 35
    assert 'purdue-cs-10100' not in profile['course_ids']['required']
    assert not any(c.startswith('purdue-ma-') for c in profile['course_ids']['required'])
    rules = {r['id']:r for r in p['requirements']}
    assert rules['purdue-ai-ba-calculus']['count'] == 1
    assert rules['purdue-ai-ba-calculus-applied']['course_ids'] == ['purdue-ma-16010','purdue-ma-16020']
    assert rules['purdue-ai-ba-area-e']['credits'] == 3
    assert next(c for c in p['courses'] if c['code']=='PHIL 41500')['credits'] is None
    assert catalog.parse(html) == p
    assert 'curriculum_audit' not in p and 'last_verified' not in p
    assert all('category_review' not in c for c in p['courses'])


@pytest.mark.parametrize('before,after', [
    ('Artificial Intelligence, BA','Artificial Intelligence, BS'),
    ('2026-2027 University Catalog','2025-2026 University Catalog'),
    ('120 Credits Required','124 Credits Required'),
    ('(51-53 credits)','(50-53 credits)'),
    (' and</li>',' or</li>'),
    ('>OR<','>AND<'),
    ('CS 36100','CS 10100'),
    ('PHIL 41400','PHIL 40000'),
    ('PHIL 20800','PHIL 20700'),
    ('HIST 30705','HIST 39999'),
    ('Synthetic policy.','Changed policy.'),
    ('Synthetic learning outcome.','Changed learning outcome.'),
])
def test_catalog_changes_require_review(monkeypatch,before,after):
    html = fixture(monkeypatch)
    assert before in html
    with pytest.raises(ValueError):catalog.parse(html.replace(before,after))


def test_truncated_option_menu_is_not_a_complete_smaller_pool(monkeypatch):
    soup = BeautifulSoup(fixture(monkeypatch),'html.parser')
    next(li for li in soup.select('li.acalog-course') if 'PHIL 20800' in li.text).decompose()
    with pytest.raises(ValueError,match='choice inventory changed'):catalog.parse(str(soup))


def test_scrape_reruns_are_deterministic_and_preserve_curated_reviews(monkeypatch,tmp_path):
    html = fixture(monkeypatch)
    p = json.loads(Path('data/programs/purdue-ai-ba.json').read_text())
    conn = db.connect(tmp_path/'scrape.sqlite');db.migrate(conn);db.ingest_program(conn,p)
    module = SimpleNamespace(SOURCES=(catalog.URL,),parse=catalog.parse)
    class Capture:
        def fetch(self,url,force=False):
            assert url==catalog.URL
            return FetchResult(url,html,'2026-10-12T00:00:00+00:00',hashlib.sha256(html.encode()).hexdigest(),200,True)
    first = scrape_one(conn,p['id'],module,Capture())
    second = scrape_one(conn,p['id'],module,Capture())
    assert first['status']==second['status']=='success'
    assert first['new_candidates']==1 and second['new_candidates']==0
    assert second['source_changes']==0
    current=db.program_record(conn.execute('SELECT * FROM programs WHERE id=?',(p['id'],)).fetchone())
    assert current==p
    conn.close()


def test_curated_chart_manual_counts_and_current_content():
    p=json.loads(Path('data/programs/purdue-ai-ba.json').read_text())
    actual=requirement_profile(p,include_course_ids=True)
    assert actual['required']['count']==11 and actual['options']['count']==35
    assert actual['required']['categories']==dict(foundations=2,mathematics=1,ai_ml=1,systems=0,human_context=6,applications=0,electives=0,other=1)
    assert actual['options']['categories']==dict(foundations=0,mathematics=5,ai_ml=0,systems=0,human_context=26,applications=3,electives=0,other=1)
    c={c['code']:c for c in p['courses']}
    assert c['PHIL 32300']['category_review']['status']=='mixed'
    assert c['PHIL 35000']['category_review']['status']=='mixed'
    assert c['PHIL 30000']['category']=='human_context'
    assert c['CS 18200']['category']=='mathematics'
    assert all(c['description'] and c['prerequisites'] is None for c in p['courses'])
    assert p['hosting_unit']=='Department of Philosophy, College of Liberal Arts'
    assert len([o for o in p['outcomes'] if o.get('statement_type')=='learning_outcome'])==5


def test_optional_permitted_browser_capture():
    path=Path('.cache/research/purdue-ba/expanded.html')
    if not path.exists():pytest.skip('Optional ignored browser capture unavailable')
    p=catalog.parse(path.read_text())
    assert len(p['courses'])==46
    assert p==catalog.parse(path.read_text())
    original=Path('.cache/research/purdue-ba/catalog.html')
    unexpanded=catalog.parse(original.read_text())
    assert unexpanded['requirements']==p['requirements']
    assert [(c['id'],c['name'],c['credits']) for c in unexpanded['courses']]==[(c['id'],c['name'],c['credits']) for c in p['courses']]
    assert catalog.URL in importlib.import_module('atlas.adapters.purdue-ai-ba.adapter').SOURCES
