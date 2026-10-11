"""Course evidence must preserve option eligibility and program scope."""
import hashlib
import json
from pathlib import Path
import pytest
from bs4 import BeautifulSoup
from atlas.adapters import miami_named_option_reviews as m
from atlas.adapters.business_society_minors import clean


def fixture(monkeypatch, eligibility='Pre-Requisite: TEST 100 or TEST 200.'):
    html = '<div class="courseblock"><p class="courseblocktitle">ABC 101. Example project. 1-3 Credit Hours.</p><p>Invented subject. '+eligibility+' Components: LEC.</p></div>'
    text = clean(BeautifulSoup(html, 'html.parser').get_text(' ', strip=True))
    monkeypatch.setattr(m, 'SPEC', {'ABC 101': dict(key='abc', url='https://example.edu/abc/',
        program_ids=['example'], digest=hashlib.sha256(text.encode()).hexdigest(),
        category='applications', description='Invented project description.')})
    return html


@pytest.mark.parametrize('eligibility', [
    'Pre-Requisite: TEST 100 or TEST 200.',
    'Requisites: Example college and sophomore standing.',
    'Prerequisite or Corequisite: C- or Higher in TEST 100.',
])
def test_source_expression_and_variable_credit(monkeypatch, eligibility):
    result = m.parse(fixture(monkeypatch, eligibility), 'example', 'abc')
    c = result['courses'][0]
    assert c['prerequisites'] == eligibility
    assert c['credits'] is None and '1-3 credit hours' in c['description']
    assert 'category_review' not in c and 'curriculum_audit' not in result


def test_missing_changed_duplicate_and_composition(monkeypatch):
    html = fixture(monkeypatch)
    with pytest.raises(ValueError, match='changed'):
        m.parse(html.replace('Invented subject', 'Changed subject'), 'example', 'abc')
    for bad in ['<h1>Log in</h1>', html + html]:
        with pytest.raises(ValueError, match='missing or duplicate'):
            m.parse(bad, 'example', 'abc')
    previous = lambda _: {'id':'example','courses':[{'id':'fixed'}], 'requirements':[{'id':'policy'}]}
    result = m._compose(previous, html, 'example', 'abc')
    assert result['requirements'] == [{'id':'policy'}]
    assert len(result['courses']) == 2
    with pytest.raises(ValueError, match='overlapping'):
        m._compose(lambda _: m.parse(html, 'example', 'abc'), html, 'example', 'abc')


@pytest.mark.parametrize('pid,expected', [
    ('university-of-miami-artificial-intelligence-technologies-for-business-other-degree',43),
    ('miami-ai-technologies-business-bsba',54),
    ('university-of-miami-data-science-and-artificial-intelligence-ba-degree',46),
    ('miami-data-science-ai-bs',57),
])
def test_all_primary_table_named_identities_have_description_review(pid, expected):
    p = json.loads(Path('data/programs/'+pid+'.json').read_text())
    ids = {cid for r in p['requirements'] if '-table-' in r['id'] for cid in r['course_ids']}
    assert len(ids) == expected
    courses = {c['id']:c for c in p['courses']}
    assert all(courses[cid].get('description') and courses[cid].get('category_review') for cid in ids)
    assert p['curriculum_status'] == 'partial'


def test_degree_row_conditions_survive_normalized_catalog_names():
    p = json.loads(Path('data/programs/miami-data-science-ai-bs.json').read_text())
    evidence = '\n'.join(r['source_text'] or '' for r in p['requirements'] if '-table-' in r['id'])
    assert 'only if taken before CSC 120' in evidence
    assert 'project must be approved as DS&AI related' in evidence
    assert 'not permitted with MTH 524' in evidence
    courses = {c['code']:c for c in p['courses']}
    assert courses['CSC 410']['credits'] is None
    assert courses['CSC 405']['credits'] == 1
    assert courses['CSC 506']['category_review']['status'] == 'mixed'
    ba = json.loads(Path('data/programs/university-of-miami-data-science-and-artificial-intelligence-ba-degree.json').read_text())
    assert 'category_review' not in next(c for c in ba['courses'] if c['code']=='CSC 506')


def test_source_parser_keeps_pool_qualifiers_as_requirement_evidence():
    from atlas.adapters.miami_degree_curricula import observe
    html = '''<h1>Example degree</h1><div id="curriculumtextcontainer"><table>
    <tr class="areaheader"><td>Core Computer Science Courses</td></tr>
    <tr><td>Techniques</td><td>3</td></tr>
    <tr><td><a class="code" href="/course">CSC 115</a></td><td>Example (only if taken before CSC 120)</td><td>3</td></tr>
    </table></div>'''
    out = observe(html,'example','Example degree','BS','Example degree','source','https://example.edu/')
    pool = next(r for r in out['requirements'] if r['kind']=='choose_credits')
    assert 'only if taken before CSC 120' in pool['source_text']
