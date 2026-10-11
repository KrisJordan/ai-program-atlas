"""Source-specific observation safeguards for the GenAI and GeoAI minors."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]


def adapter(slug):
    spec = importlib.util.spec_from_file_location(slug, ROOT/'atlas/adapters'/slug/'adapter.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def vanderbilt_overview():
    core = ''.join(f'<details><summary>AI {code}: {name}</summary></details>' for code, name in [('1010','Tools'),('1020','Foundations'),('2200','Ethics')])
    return ('<h1>Join the GenAI Minor</h1><p>non-CS students</p><h2>Required Courses</h2><div>' + core + '<details><summary>AI-integrated course</summary><ul><li>ANTH 3050: Test application</li><li>CHBE 2250- Test simulation</li></ul><p>Other courses may count; submit the syllabus for review</p></details></div>')


def vanderbilt_catalog():
    rows=['AI 1010 Tools','AI 1020 Foundations','Ethics and responsible use of AI: one of AI 2200, HIST 1590, PHIL 1009, PHIL 2620','One course from AI Applications and Evaluation']
    return '<h3>Generative Artificial Intelligence Minor</h3><p>requires 12 hours</p><table>'+''.join('<tr><td>'+r+'</td><td>3 hours</td></tr>' for r in rows)+'<tr><td>Total:</td><td>12 hours</td></tr></table><p>AI Applications and Evaluation</p>'+''.join(f'<p>TEST {3000+i} Application {i}</p>' for i in range(9))+'<h3>Other Minor</h3><p>TEST 3999 Not this minor</p>'


def florida_catalog():
    groups=[('Introductory course',['GIS 2114','GIS 2002'],'3'),('Geographic Techniques courses (select two)',['GIS 3043','GIS 4037','GIS 4102C','GIS 4124','MET 3753'],'6-8'),('GeoAI and Geographic Analysis courses (select two)',['GIS 3420C','GIS 4113','GIS 4115C','GIS 4324','GIS 4424C','GIS 4500','MET 4224C'],'6'),('Capstone course',['GIS 4123C'],'3')]
    rows=[]
    for heading,codes,credits in groups:
        rows.append(f'<tr class="areaheader"><td>{heading}</td><td>{credits}</td></tr>')
        for code in codes:
            rows.append(f'<tr><td><a class="code" href="/search/?P={code}">{code}</a></td><td>Test title {code}</td></tr>')
    return '<h1>GeoAI and Geographic Analysis</h1><p>minor Required Courses Completed with minimum grades of C No more than six transfer credits minimum of twelve credits of coursework exclusive Students pursuing the Certificate of Geographic Artificial Intelligence and Big Data or the Certificate of Geospatial Information Analysis are not eligible</p><table class="sc_courselist">'+''.join(rows)+'<tr class="listsum"><td>Total Credits</td><td>18-20</td></tr></table>'


def test_overview_does_not_infer_integrated_quantity_or_credits():
    result=adapter('vanderbilt-genai-minor').parse(vanderbilt_overview())
    assert len(result['courses'])==5
    group=next(r for r in result['requirements'] if r['id'].endswith('-integrated'))
    assert group['kind']=='note' and group['count'] is None and group['credits'] is None
    assert all(c['credits'] is None for c in result['courses'])
    assert 'curriculum_audit' not in result and 'last_verified' not in result


def test_overview_missing_audience_or_approval_rejected():
    m=adapter('vanderbilt-genai-minor')
    for phrase in ('non-CS students','Other courses may count','Required Courses'):
        with pytest.raises(ValueError):m.parse(vanderbilt_overview().replace(phrase,''))


def test_catalog_choice_pools_are_scoped_and_changed_cardinality_rejected():
    m=adapter('vanderbilt-genai-minor');html=vanderbilt_catalog();r=m.parse_catalog(html)
    assert len(r['courses'])==15 and len(r['requirements'])==4
    assert [len(x['course_ids']) for x in r['requirements'][:3]]==[2,4,9]
    assert [x['count'] for x in r['requirements'][1:3]]==[1,1]
    assert not any(c['code']=='TEST 3999' for c in r['courses'])
    for old,new in [('one of','two of'),('requires 12 hours','requires 15 hours'),('TEST 3008','NOT_A_CODE')]:
        with pytest.raises(ValueError):m.parse_catalog(html.replace(old,new))


def test_empty_catalog_shell_cannot_pass_as_curriculum():
    with pytest.raises(ValueError):adapter('vanderbilt-genai-minor').parse_catalog('<div id="kuali-catalog"></div>')


def test_geoai_preserves_alternatives_ranges_and_unknown_course_amounts():
    r=adapter('florida-geoai-geographic-analysis-minor').parse(florida_catalog())
    assert len(r['courses'])==15 and len(r['requirements'])==9
    assert [x['count'] for x in r['requirements'][:4]]==[1,2,2,None]
    assert r['requirements'][1]['credits'] is None and '6-8' in r['requirements'][1]['summary']
    assert all(c['credits'] is None for c in r['courses'])


@pytest.mark.parametrize('old,new',[('select two','select three'),('No more than six transfer credits','No more than nine transfer credits'),('minimum of twelve credits','minimum of six credits'),('GeoAI and Geographic Analysis</h1>','Geography</h1>')])
def test_geoai_changed_rules_trigger_review(old,new):
    with pytest.raises(ValueError):adapter('florida-geoai-geographic-analysis-minor').parse(florida_catalog().replace(old,new))


def test_policy_scopes_are_guarded():
    m=adapter('florida-geoai-geographic-analysis-minor')
    for fn in (m.parse_university_policy,m.parse_clas_policy):
        with pytest.raises(ValueError):fn('<h1>Other college</h1><p>Minor requirements</p>')
    v=adapter('vanderbilt-genai-minor')
    assert v.parse_credit_definition('<h4>CREDIT HOUR DEFINITION</h4><p>Credit hours are semester hours</p>')['credit_unit']=='semester_hours'


def test_reviewed_records_preserve_conflicts_and_unknown_dates():
    for slug,count in [('vanderbilt-genai-minor',21),('florida-geoai-geographic-analysis-minor',15)]:
        p=json.loads((ROOT/'data/programs'/f'{slug}.json').read_text())
        assert p['curriculum_status']=='partial' and p['first_offered'] is None
        assert p['curriculum_audit']['unresolved_requirements'] and len(p['courses'])==count
        sources={s['id'] for s in p['sources']}
        assert all(x['source_id'] in sources for x in p['requirements']+p['courses']+p['outcomes'])
    p=json.loads((ROOT/'data/programs/vanderbilt-genai-minor.json').read_text())
    assert any(r['id'].endswith('overview-conflict') and r['kind']=='note' for r in p['requirements'])
    assert any('Catalog versus overview' in x for x in p['curriculum_audit']['unresolved_requirements'])
