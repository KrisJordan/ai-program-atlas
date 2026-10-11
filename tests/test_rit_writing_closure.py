import hashlib
import importlib.util
import json
from pathlib import Path
import pytest
from atlas.adapters.rit_writing_closure import PID, SPECS, STUDENTS, parse, parse_reviewed_document
ROOT=Path(__file__).resolve().parents[1]


def fixture(url):
    title, headings=SPECS[url]
    sections=[]
    for h in headings:
        body='<p>Published source policy text about permission and current approval. '*4+'</p>'
        if h=='UWRT 150':
            body='<h3>Course Description</h3><p>Three-credit analytical writing and revision course.</p><a href="/writing/example.pdf">Sample Syllabus</a>'
        sections.append('<section><h2>'+h+'</h2>'+body+'</section>')
    return '<main><h1>'+title+'</h1>'+''.join(sections)+'<p>'+'Public writing guidance. '*20+'</p></main>'


@pytest.mark.parametrize('url',SPECS)
def test_identity_and_changed_actual_body_not_manual_review(url):
    html=fixture(url);a=parse(html,url=url);b=parse(html.replace('guidance','updated guidance'),url=url)
    assert a['observed_source_content_sha256']!=b['observed_source_content_sha256']
    assert a['requirements']==[]
    assert not {'curriculum_audit','last_verified','category_review','curriculum_status'} & a.keys()
    with pytest.raises(ValueError):parse(html.replace('<h1>','<h1>Wrong '),url=url)
    with pytest.raises(ValueError):parse('<input type="password">'+html,url=url)


def test_syllabus_link_is_actual_scoped_observation():
    html=fixture(STUDENTS);d=parse(html,url=STUDENTS)
    assert d['courses']==[{'id':PID+'-uwrt-150','code':'UWRT-150','public_site':STUDENTS,'syllabus':'https://www.rit.edu/writing/example.pdf'}]
    with pytest.raises(ValueError,match='syllabus'):parse(html.replace('Sample Syllabus','Unrelated'),url=STUDENTS)
    with pytest.raises(ValueError,match='syllabus'):parse(html.replace('/writing/example.pdf','https://elsewhere.example/sample.pdf'),url=STUDENTS)
    with pytest.raises(ValueError,match='section'):parse(html.replace('UWRT 150','UWRT 325'),url=STUDENTS)


def test_document_replay_rejects_changed_text():
    with pytest.raises(ValueError,match='changed'):parse_reviewed_document('Unreviewed document',key='wi-petition')


def test_seed_preserves_counts_example_scope_and_pending_inventory():
    from atlas.db import validate_program
    d=json.loads((ROOT/'data/programs'/f'{PID}.json').read_text());validate_program(d)
    assert len(d['courses'])>=74 and d['curriculum_status']=='partial'
    c=next(c for c in d['courses'] if c['code']=='UWRT-150')
    assert 'undated sample' in c['description'] and 'Syllabus%20(Sample)' in c['syllabus']
    assert c['public_site']==STUDENTS
    r={r['id'].split(PID+'-')[-1]:r for r in d['requirements']}
    assert 'C or better' in r['wi-substitution-form']['summary']
    assert 'does not guarantee' in r['wi-substitution-form']['summary']
    assert 'ISTE150' in r['fyw-exemption']['summary'] and 'ISTE110' in r['fyw-exemption']['summary']
    assert 'March 2013' in r['science-list-version']['summary']
    assert any('RIT Login' in x for x in d['curriculum_audit']['unresolved_requirements'])
    spec=importlib.util.spec_from_file_location('rit_writing_adapter',ROOT/'atlas/adapters'/PID/'adapter.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    assert set(SPECS)<=set(m.SOURCES)<=set(s['url'] for s in d['sources'])


@pytest.mark.parametrize('key',['wi-petition','uwrt150-sample','science-perspectives'])
def test_optional_actual_documents(key):
    p=ROOT/'.cache/research/rit-degree-closure'/f'{key}.txt'
    if not p.exists():pytest.skip('Ignored source capture unavailable')
    result=parse_reviewed_document(p.read_text(),key=key)
    assert result['courses']==result['requirements']==[]
    assert not {'curriculum_audit','last_verified','category_review'}&result.keys()
