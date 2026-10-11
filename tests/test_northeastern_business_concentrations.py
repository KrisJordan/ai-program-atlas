"""Conditional program options and live CourseLeaf choice semantics, without seed replay."""
import hashlib
import json
from pathlib import Path
import pytest
from atlas import db
from atlas.families import resolve_program
from atlas.requirements import validate_requirements
from atlas.adapters.northeastern_business_concentrations import (
    PID,BASE,PROFILES,SOURCE_PARSERS,parse_concentration,selection_rules,
)
ROOT=Path(__file__).resolve().parents[1]


def row(code,name='Example course',hours='4',css=''):
    return f'<tr class="{css}"><td class="codecol"><a class="code" href="/search/?P={code}">{code}</a></td><td>{name}</td><td class="hourscol">{hours}</td></tr>'


def header(title):return f'<tr class="areaheader"><td>{title}</td></tr>'


def instruction(text,hours=''):return f'<tr><td>{text}</td><td class="hourscol">{hours}</td></tr>'


def document(title,rows,prose=''):
    return f'''<header id="site-title"><h1>{title}</h1></header><div>Academic Catalog 2026-2027</div>
    <nav>{row('BAD 9999')}</nav><div id="concentrationrequirementstextcontainer">
    <h2>Concentration in {title}</h2><p>{prose}</p><table class="sc_courselist"><thead><tr><th class="hourscol">Hours</th></tr></thead><tbody>{rows}</tbody></table></div>'''


def test_concentration_reads_current_credits_counts_and_ignores_navigation():
    html=document('Accounting',header('Required Courses')+row('ACCT 3401')+header('Electives')+instruction('Complete two of the following:','8')+row('ACCT 3403',hours='')+row('ACCT 3416',hours=''))
    a=parse_concentration(html,title='Accounting');validate_requirements(a)
    assert a['id']==PID and a['curriculum_status']=='partial'
    assert all(c['code']!='BAD 9999' for c in a['courses'])
    assert a['courses'][0]['credits']==4
    b=parse_concentration(html.replace('>4<','>3<').replace('two of','one of').replace('>8<','>4<'),title='Accounting')
    assert b['courses'][0]['credits']==3
    assert next(r for r in b['requirements'] if r['kind']=='choose_courses')['count']==1
    assert not {'curriculum_audit','last_verified','title','award_level'} & a.keys()
    assert all(c['description'] is None for c in a['courses'])


@pytest.mark.parametrize('change',[
    lambda h:h.replace('<h1>Accounting</h1>','<h1>Finance</h1>'),
    lambda h:h.replace('concentrationrequirementstextcontainer','unrelated'),
    lambda h:h.replace('Concentration in Accounting','Unrelated'),
    lambda h:h.replace('Academic Catalog 2026-2027','Undated page'),
    lambda h:h.replace('<th class="hourscol">Hours</th>','<th>Unknown unit</th>'),
])
def test_wrong_source_or_missing_scope_rejected(change):
    with pytest.raises(ValueError):parse_concentration(change(document('Accounting',row('ACCT 3401'))),title='Accounting')


def test_brand_course_count_is_not_confused_with_mktg_credit_minimum():
    html=document('Brand Management',header('Electives')+instruction('Complete three electives, with at least 8 credits from MKTG courses:','12')+row('MKTG 3401',hours='')+row('INNO 2301',hours=''))
    a=parse_concentration(html,title='Brand Management')
    r=next(r for r in a['requirements'] if r['kind']=='choose_courses')
    assert r['count']==3 and r['credits']==12 and 'at least 8 credits from MKTG' in r['summary']
    b=parse_concentration(html.replace('three electives','four electives').replace('8 credits','12 credits').replace('>12<','>16<'),title='Brand Management')
    assert next(r for r in b['requirements'] if r['kind']=='choose_courses')['count']==4


def test_additional_pool_has_exact_membership_and_cap_without_extra_requirement():
    rows=header('Electives')+instruction('Complete two electives, one of which may come from the additional electives list:','8')+row('INNO 2304',hours='')+'<tr class="areasubheader"><td><div class="blockindent">Additional Electives</div></td></tr>'+row('ENTR 2303',hours='')+row('MGMT 3530',hours='')+instruction('One course from an approved Dialogue may count toward the additional elective.')
    a=parse_concentration(document('Corporate Innovation',rows),title='Corporate Innovation');validate_requirements(a)
    subgroup=next(r for r in a['requirements'] if r['title']=='Additional Electives')
    assert subgroup['kind']=='note'
    assert subgroup['course_ids']==[PID+'-entr-2303',PID+'-mgmt-3530']
    assert 'At most one' in subgroup['summary'] and 'approval' in subgroup['summary']
    assert next(r for r in a['requirements'] if r['id']==subgroup['parent_id'])['count']==2
    with pytest.raises(ValueError):parse_concentration(document('Corporate Innovation',rows.replace('one of which','two of which')),title='Corporate Innovation')


def test_required_course_reuse_condition_is_not_part_of_course_title():
    rows=header('Required Course')+row('FINA 3301','Corporate Finance')+header('Electives')+instruction('Complete three of the following:','12')+row('FINA 3301','Corporate Finance (if not selected as a required course)',hours='')
    a=parse_concentration(document('Finance',rows),title='Finance')
    assert len(a['courses'])==1 and a['courses'][0]['name']=='Corporate Finance'
    assert any('if not selected' in r['summary'] for r in a['requirements'])


def international():
    return document('International Business',header('Required Courses')+row('INTB 1203')+instruction('Complete one or both of the following:','4-8')+row('INTB 2501',hours='')+row('INTB 3310',hours='')+header('Electives')+instruction('Complete two of the following courses (one if both courses above selected).','4-8')+row('INTB 3320',hours='')+row('FINA 4320',hours=''))


def test_international_business_conditional_elective_counts_are_two_paths():
    a=parse_concentration(international(),title='International Business');validate_requirements(a)
    for number,counts in [(1,[1,2]),(2,[2,1])]:
        group=next(r for r in a['requirements'] if r['id']==PID+'-req-international-business-path-'+str(number))
        assert [r['count'] for r in a['requirements'] if r['parent_id']==group['id']]==counts
    with pytest.raises(ValueError):parse_concentration(international().replace('one if both','two if both'),title='International Business')


def degree():
    lis=''.join(f'<li><a href="{BASE+path}">{title}</a>'+(' (available only as a second concentration)' if title=='International Business' else '')+'</li>' for title,path in PROFILES.items())
    return '<header id="site-title"><h1>Artificial Intelligence and Business Administration, BS (Boston)</h1></header><div id="programrequirementstextcontainer"><h2>Business Concentration</h2><p>Complete at least one business concentration from the following list.</p><ul>'+lis+'</ul><p>Note: If the Marketing Analytics concentration is selected, an additional general elective is required.</p><h2>Other requirements</h2></div>'


def test_actual_degree_list_controls_eligibility_not_school_navigation():
    rows=selection_rules(degree())
    assert rows[0]['kind']=='alternative' and '13 eligible' in rows[0]['summary']
    assert rows[1]['kind']=='note' and 'only as a second' in rows[1]['summary']
    for html in [degree().replace('at least one','zero'),degree().replace('only as a second','as a first'),degree().replace('Marketing Analytics</a>','Business Analytics</a>'),degree().replace('additional general elective is required','no elective is required')]:
        with pytest.raises(ValueError):selection_rules(html)


def test_reviewed_seed_preserves_family_and_conditional_scopes():
    p=json.loads((ROOT/'data/programs'/f'{PID}.json').read_text())
    f=json.loads((ROOT/'data/families/northeastern-ai-combined-degrees.json').read_text())
    db.validate_program(p,f); r=resolve_program(p,f)
    assert len([x for x in r['requirements'] if x['origin']=='family'])==56
    assert len([x for x in p['requirements'] if x['parent_id']==PID+'-req-business-concentration-options'])==13
    optional=[x for x in p['requirements'] if x['parent_id']==PID+'-req-business-concentration-second-only']
    assert len(optional)==1 and optional[0]['title'].startswith('International Business')
    assert len([s for s in p['sources'] if '/business/concentrations/' in s['url']])==14
    assert p['curriculum_status']=='partial'
    assert any('home-college' in issue for issue in p['curriculum_audit']['unresolved_requirements'])
    assert 'home-college' in p['curriculum_audit']['unresolved_requirements'][0]
    assert not any('remain unexpanded' in x['summary'] for x in p['requirements'])


@pytest.mark.parametrize('url',SOURCE_PARSERS)
def test_optional_cached_official_concentration_observation(url):
    cache=ROOT/'.cache/http'/(hashlib.sha256(url.encode()).hexdigest()+'.body')
    if not cache.exists():pytest.skip('Optional ignored live-source cache')
    validate_requirements(SOURCE_PARSERS[url](cache.read_text()))
