"""Synthetic CourseLeaf layouts test observation semantics, not seed replay."""
import pytest
from atlas.adapters.northeastern_courseleaf import parse_catalog
from atlas.requirements import validate_requirements

TITLE = 'Artificial Intelligence and Biology, BS (Boston)'
URL = 'https://catalog.northeastern.edu/undergraduate/example/'


def row(code, name, hours='', css='', bundle=None):
    codecell = f'<a class="code" href="/search/?P={code}">{code}</a>'
    if bundle:
        codecell += f'<br/><span>and <a class="code" href="/search/?P={bundle[0]}">{bundle[0]}</a></span>'
        name += f'<br/><span>and {bundle[1]}</span>'
    return f'<tr class="{css}"><td class="codecol">{codecell}</td><td>{name}</td><td class="hourscol">{hours}</td></tr>'


def document(rows, title=TITLE, section='Biology Requirements', overview=''):
    return f'''<html><header id="site-title"><h1>{title}</h1></header>
    <div>Academic Catalog 2026-2027</div><div id="textcontainer">{overview}</div>
    <nav>{row('BAD 1000', 'Navigation Course', '99')}</nav>
    <div id="programrequirementstextcontainer"><h2>{section}</h2>
    <table class="sc_courselist"><tbody>{rows}</tbody></table><p>128 total semester hours required</p></div></html>'''


def parse(html):
    return parse_catalog(html, program_id='test-program', title=TITLE, url=URL,
                         required_sections=['Biology Requirements'],
                         outcome_claims=[('biological processes', 'Students examine biological processes.')])


def test_bundle_alternatives_and_actual_changes():
    html = document(row('BIOL 1000','Biology','5',bundle=('BIOL 1001','Lab for Biology'))
                    + row('BIOL 1002','Advanced Biology','',css='orclass'))
    result = parse(html)
    validate_requirements(result)
    assert [x['credits'] for x in result['courses']] == [None, None, None]
    bundle = next(x for x in result['requirements'] if len(x['course_ids']) == 2)
    alt = next(x for x in result['requirements'] if x['kind'] == 'alternative')
    assert bundle['credits'] == 5 and bundle['parent_id'] == alt['id']
    assert len([x for x in result['requirements'] if x['parent_id'] == alt['id']]) == 2
    assert next(x for x in parse(html.replace('>5<','>6<'))['requirements'] if len(x['course_ids'])==2)['credits']==6
    assert all(x['code'] != 'BAD 1000' for x in result['courses'])
    assert 'last_verified' not in result and 'curriculum_audit' not in result
    assert result['curriculum_status'] == 'partial'


def test_credit_choice_and_range_does_not_create_excluded_courses():
    rows = '''<tr class="areaheader"><td>Electives</td></tr>
    <tr><td colspan="2">Complete 4 semester hours from the following:</td><td class="hourscol">4</td></tr>
    <tr><td colspan="2">CS 2300 or higher, except <a class="code">CS 5010</a></td></tr>'''
    result = parse(document(rows + row('CS 2400','Programming')))
    choice = next(x for x in result['requirements'] if x['kind']=='choose_credits')
    assert choice['credits']==4
    assert [x['code'] for x in result['courses']] == ['CS 2400']
    assert any('except CS 5010' in x['summary'] for x in result['requirements'])
    assert next(x for x in parse(document(rows.replace('4 semester','8 semester').replace('>4<','>8<')+row('CS 2400','Programming')))['requirements'] if x['kind']=='choose_credits')['credits']==8


def test_course_plus_lab_choice_is_one_bundle_alternative():
    rows = '<tr><td>Complete one course and its corresponding lab, if indicated:</td><td class="hourscol">4-5</td></tr>'
    result = parse(document(rows+row('BIOL 1000','Biology','',bundle=('BIOL 1001','Lab'))+row('BIOL 2000','Evolution')))
    choice = next(x for x in result['requirements'] if x['kind']=='alternative')
    assert choice['count'] is None
    assert len([x for x in result['requirements'] if x['parent_id']==choice['id']])==2
    assert result['courses'][0]['credits'] is None


def test_single_course_credits_change_and_missing_metadata_stays_null():
    result=parse(document(row('BIOL 1000','Biology','4')))
    assert result['courses'][0]['credits']==4
    assert result['courses'][0]['description'] is None
    assert parse(document(row('BIOL 1000','Biology','3')))['courses'][0]['credits']==3


@pytest.mark.parametrize('html',[
    document(row('BIOL 1000','Biology'),title='Unrelated Program'),
    document(row('BIOL 1000','Biology'),section='Unrelated Section'),
    f'<h1>{TITLE}</h1><nav>Biology Requirements</nav>',
    document(''),
    document(row('BIOL 1000','Biology',css='orclass')),
])
def test_wrong_source_or_changed_structure_is_rejected(html):
    with pytest.raises(ValueError):parse(html)


def test_outcomes_require_current_overview_evidence():
    rows=row('BIOL 1000','Biology')
    assert parse(document(rows))['outcomes']==[]
    result=parse(document(rows,overview='Students explore biological processes.'))
    assert result['outcomes'][0]['kind']=='source_stated'
    assert result['outcomes'][0]['source_id']=='test-program-catalog'


def test_concurrent_course_mention_is_not_another_row_course():
    result=parse(document(row('BIOL 4900','Research Capstone (concurrent with <a class="code">BIOL 4991</a>)','4')))
    assert [x['code'] for x in result['courses']]==['BIOL 4900']
    assert result['courses'][0]['name']=='Research Capstone'
    assert any('concurrent with BIOL 4991' in x['summary'] for x in result['requirements'])


def test_conflicting_amounts_or_unit_changes_are_rejected():
    rows='<tr><td>Complete 4 semester hours from the following:</td><td class="hourscol">8</td></tr>'+row('CS 2400','Programming')
    with pytest.raises(ValueError,match='Conflicting credit'):
        parse(document(rows))
    with pytest.raises(ValueError,match='semester-hour'):
        parse(document(row('BIOL 1000','Biology','4')).replace('semester hours','quarter hours'))


def test_capstone_concurrent_alternative_is_nested_under_that_capstone():
    rows=(row('BIOL 4991','Research')+row('BIOL 4994','Internship')
          +row('BIOL 4900','Research Capstone (concurrent with BIOL 4991 or BIOL 4994, which may count toward electives)','4'))
    result=parse(document(rows))
    capstone=next(r for r in result['requirements'] if r['title']=='BIOL 4900')
    concurrent=next(r for r in result['requirements'] if r['title']=='BIOL 4900 concurrent research')
    assert concurrent['parent_id']==capstone['id'] and concurrent['kind']=='alternative'
    options=[r for r in result['requirements'] if r['parent_id']==concurrent['id']]
    assert {r['course_ids'][0] for r in options}=={'test-program-biol-4991','test-program-biol-4994'}
    assert len(result['courses'])==3
    validate_requirements(result)
