import importlib,json
from pathlib import Path
import pytest
m=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.architecture_ocw')


def fixture(title='Example Art History',term='Fall 2018',permission='Permission of instructor'):
    return f'''<div id="course-banner"><div class="course-number-term-detail">4.601 | {term} | Undergraduate</div><h1>{title}</h1></div><div id="course-main-content"><h2>Course Description</h2><p>Historical study of artistic patronage and institutions.</p><h2>Prerequisites</h2><p>{permission}</p><h2>Requirements</h2><p>A final paper is required.</p></div>'''


def test_exact_dated_content_observation_withdraws_changed_metadata(monkeypatch):
    html=fixture();url='https://ocw.mit.edu/courses/example/pages/syllabus/'
    record=dict(observation=m.observe(html),source_id='example-source',summary='Studies art history.',notes=['Dated only.'],courses={'example-record':dict(code='4.601',name='Example Art History')})
    monkeypatch.setattr(m,'MANIFEST',{'sources':{url:record}})
    row=m.parse(html,url)['courses'][0]
    assert row['prerequisites']=='Permission of instructor' and row['credits'] is None
    assert row['id']=='example-record' and row['syllabus']==url
    assert not any(k in row for k in ['category_review','curriculum_audit'])
    for changed in [fixture(term='Fall 2026'),fixture(permission='None'),html.replace('final paper','final exam'),fixture(title='Different Course')]:
        assert m.parse(changed,url)['courses']==[]
    with pytest.raises(ValueError,match='substantive description'):
        m.observe(html.replace('Course Description','Schedule'))


def test_pinned_actual_syllabi_preserve_exact_identity_and_degree_roles():
    seed=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text());by={c['id']:c for c in seed['courses']}
    assert sum(len(s['courses']) for s in m.MANIFEST['sources'].values())==6
    for url,saved in m.MANIFEST['sources'].items():
        for cid,identity in saved['courses'].items():
            row=by[cid]
            assert (row['code'],row['name'])==(identity['code'],identity['name'])
            assert row['description']==saved['summary'] and row['category']=='human_context'
            assert row['public_site']==row['syllabus']==url
        path=Path(saved['cache_path'])
        if path.exists():
            result=m.parse(path.read_text(),url)
            assert {c['id'] for c in result['courses']}==set(saved['courses'])
            assert result['requirements']==[]
    grad=by['mit-ai-hass-middle-eastern-studies-4-619']
    assert 'permission' in grad['prerequisites'] and any('graduate course' in n for n in grad['notes'])
