import pytest

from atlas.adapters.northeastern_course_resources import AUTHORITY, SITE, SYLLABUS, TERM_SCOPE, parse_resource


def observe(html, url):
    return parse_resource(html, program_id='test-program', url=url)


def homepage(scope=TERM_SCOPE):
    return f'<main><h1>CS 2000: Introduction to Program Design and Implementation</h1><p>{scope}</p></main><nav><a href="{SYLLABUS}">Syllabus</a></nav>'


def syllabus():
    return f'<title>Syllabus | NEU CS 2000 Public Resources</title><nav><a href="{SITE}">Home</a></nav><main><h4 id="classes">Classes</h4><p>Each class period (of CS2000) has preparation.</p><h4 id="labs">Labs</h4><p>The lab period (CS2001) includes partner exercises.</p></main>'


def test_homepage_requires_exact_course_term_campuses_and_visited_syllabus_link():
    result=observe(homepage(),SITE)
    assert result['courses']==[{'id':'test-program-cs-2000','code':'CS 2000','public_site':SITE,'source_id':'test-program-cs2000-fall-2026-site','url':SITE}]
    for html in (homepage().replace('Fall 2026','Fall 2027'),homepage().replace('Boston & Oakland','Boston'),homepage().replace('CS 2000:','CS 2100:'),homepage().replace(SYLLABUS,SITE+'login/')):
        with pytest.raises(ValueError):observe(html,SITE)


def test_syllabus_links_preserve_class_lab_scope_without_replaying_catalog_facts():
    result=observe(syllabus(),SYLLABUS)
    assert [c['code'] for c in result['courses']]==['CS 2000','CS 2001']
    assert all(c['syllabus']==SYLLABUS for c in result['courses'])
    assert result['courses'][1]['public_site']==SITE
    assert all('credits' not in c and 'prerequisites' not in c and 'description' not in c for c in result['courses'])
    assert 'does not itself state an offering year' in result['notes'][0]
    assert result['requirements']==[] and 'last_verified' not in result and 'curriculum_audit' not in result
    changed=observe(syllabus().replace('partner exercises','new exercises'),SYLLABUS)
    assert changed['observed_resource_digest']!=result['observed_resource_digest']
    with pytest.raises(ValueError):observe(syllabus().replace('(CS2001)','(CS2101)'),SYLLABUS)
    with pytest.raises(ValueError):observe(syllabus().replace('<h4 id="labs">Labs</h4>',''),SYLLABUS)


def test_course_mentions_only_in_navigation_are_not_syllabus_identity():
    html='<title>Syllabus | NEU CS 2000 Public Resources</title><nav>CS2000 CS2001</nav><main><p>Unrelated content</p></main>'
    with pytest.raises(ValueError):observe(html,SYLLABUS)
    with pytest.raises(ValueError):observe('<title>Access denied</title>'+syllabus(),SYLLABUS)


def test_instructor_teaching_link_requires_scoped_term_and_exact_destination():
    intro='Associate Teaching Professor at Khoury College of Computer Sciences at Northeastern University.'
    row=f'<p><strong>Fall 2026:</strong> <a href="{SITE}">CS2000: Introduction to Program Design and Implementation</a></p>'
    html=f'<main><p>{intro}</p><h3 id="teaching">Teaching</h3>{row}<h3>Research</h3></main>'
    assert observe(html,AUTHORITY)['courses']==[]
    for altered in (html.replace('Fall 2026','Fall 2025'),html.replace(SITE,SITE+'fall2025/'),html.replace('<h3 id="teaching">Teaching</h3>','<h3 id="teaching">Teaching</h3><h3>Research</h3>')):
        with pytest.raises(ValueError):observe(altered,AUTHORITY)


def test_reviewed_links_preserve_catalog_fact_sources_in_every_concrete_variant():
    import json
    from pathlib import Path
    from atlas.scrape import adapters
    available=adapters();count=0
    for path in (Path(__file__).resolve().parents[1]/'data/programs').glob('northeastern-*.json'):
        p=json.loads(path.read_text())
        if p.get('family',{}).get('id')!='northeastern-ai-combined-degrees':continue
        count+=1;sources={s['id']:s for s in p['sources']}
        for code in ('CS 2000','CS 2001'):
            c=next(c for c in p['courses'] if c['code']==code)
            assert c['public_site']==SITE and c['syllabus']==SYLLABUS
            assert c['source_id']==p['id']+'-cs-courses'
            assert c['description'] and c['credits'] is not None
        assert sources[p['id']+'-cs2000-fall-2026-site']['catalog_year']=='Fall 2026'
        assert sources[p['id']+'-cs2000-2001-public-syllabus']['catalog_year'] is None
        for url in (AUTHORITY,SITE,SYLLABUS):
            assert list(available[p['id']].SOURCES).count(url)==1
            assert url in available[p['id']].SOURCE_PARSERS
        assert p['curriculum_status']=='partial'
    assert count==23
