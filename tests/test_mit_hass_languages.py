from pathlib import Path
from importlib import import_module
import pytest
m=import_module('atlas.adapters.mit-ai-decision-making-bs.hass_languages')


def programs():
    return '''<main><h1>Academic Programs</h1><h2>HASS Concentrations</h2><p>consult with the relevant advisor and submit the HASS Concentration Form</p><h4>Chinese, French, German, Japanese, Korean, Portuguese, Russian, Spanish, Other Languages</h4><p>advance at least through semester “IV”; minimum of three subjects; commence at semester I should typically complete four subjects; commence at semester II or above need only three subjects; With advisor approval, other subject combinations; appropriate transfer credit examiner and the Concentration advisor; another accredited institution</p><h4>Theory of Language</h4><p>two subjects at semester IV or higher in different languages plus one linguistic theory subject</p><h4>Studies in International Literatures and Cultures</h4><p>three, twelve-unit subjects with a coherent theme or area of focus selected in consultation with the SILC advisor</p><h2>Minors</h2><p>Six subjects: 21G.999 Minor-only</p></main>'''


def test_eleven_conditional_fields_and_placement_routes_not_minor_requirements():
    d=m.parse_programs(programs())
    roots=[r for r in d['requirements'] if r['parent_id'] is None]
    assert len(roots)==11 and all(r['kind']=='note' for r in roots)
    assert len([r for r in d['requirements'] if r['kind']=='alternative'])==9
    assert all(r['count']==4 for r in d['requirements'] if r['id'].endswith('-beginner'))
    assert all(r['count']==3 for r in d['requirements'] if r['id'].endswith('-higher'))
    assert 'courses' not in d and 'curriculum_audit' not in d
    assert not any('Six subjects' in r['summary'] for r in d['requirements'])
    with pytest.raises(ValueError,match='condition changed'):
        m.parse_programs(programs().replace('different languages','same language'))


def test_japanese_enrollment_order_is_not_other_language_default():
    html='''<main><h1>Japanese Studies</h1><a href="https://languages.mit.edu/academic-programs/">Academic Programs</a><p>Concentration; placement information; Enrollment limited to 16; sophomores, first-years, juniors, seniors and graduate students; Within each category, priority will be given to pre-registered students</p></main>'''
    d=m.parse_field('japanese',html)
    r=d['requirements'][0]
    assert r['parent_id']=='mit-ai-hass-language-japanese'
    assert 'sophomores, first-years' in r['summary']
    assert 'does not state the majors-first' in r['summary']
    with pytest.raises(ValueError):m.parse_field('japanese',html.replace('limited to 16','limited to 18'))


def test_russian_source_link_is_required_and_no_cap_is_inferred():
    html='''<main><h1>Russian Studies</h1><a href="https://languages.mit.edu/academic-programs/">Academic Programs</a><p>Concentration and placement information</p></main>'''
    d=m.parse_field('russian',html)
    assert 'no general enrollment-cap' in d['requirements'][0]['summary']
    with pytest.raises(ValueError):m.parse_field('russian',html.replace('academic-programs/','other/'))


@pytest.mark.parametrize('key,fn',[('language-programs',m.parse_programs),('language-placement',m.parse_placement),('language-transfer',m.parse_transfer)]+[(k,lambda h,k=k:m.parse_field(k,h)) for k in m.FIELD_SPECS])
def test_optional_public_language_pages(key,fn):
    p=Path('/tmp/atlas-mit-hass-rest-'+key+'.html')
    if not p.exists():pytest.skip('Optional reviewed official page cache')
    d=fn(p.read_text())
    assert d['requirements'] and 'last_verified' not in d
    if key=='language-placement':
        cs={c['code']:c for c in d['courses']}
        assert cs['21G.302']['name']=='French II'
        assert cs['21G.310']['name'] is None
        assert all(c['credits'] is None for c in cs.values())
