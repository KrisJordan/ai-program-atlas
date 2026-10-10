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


def test_design_paths_are_alternative_bundles_not_all_required():
    rows='<tr><td>Complete one of the following options:</td><td class="hourscol">8</td></tr>'
    for label,a,b in [('Design A','ARTG 1000','ARTG 2000'),('Design B','ARTG 3000','ARTG 4000')]:
        rows+=f'<tr class="areaheader"><td>{label}</td></tr>'+row(a,'Principles')+row(b,'Studio')
    result=parse(document(rows))
    choice=next(r for r in result['requirements'] if r['kind']=='alternative')
    paths=[r for r in result['requirements'] if r['parent_id']==choice['id']]
    assert {p['title'] for p in paths}=={'Design A','Design B'}
    for path in paths:
        assert path['kind']=='all'
        assert len([r for r in result['requirements'] if r['parent_id']==path['id']])==2


@pytest.mark.parametrize('count,number',[('four',4),('five',5)])
def test_written_course_counts_are_choices(count,number):
    rows=f'<tr><td>Complete {count} courses from the following:</td><td class="hourscol">20</td></tr>'+row('LING 3000','Linguistics')
    result=parse(document(rows))
    choice=next(r for r in result['requirements'] if r['kind']=='choose_courses')
    assert choice['count']==number
    changed=parse(document(rows.replace(count,'six')))
    assert next(r for r in changed['requirements'] if r['kind']=='choose_courses')['count']==6


def test_written_semester_hours_are_credit_choice_and_footnotes_preserved():
    rows='<tr><td>Complete four semester hours from the following:</td><td class="hourscol">4</td></tr>'+row('ARTG 1000','Design<sup>1</sup>')
    html=document(rows).replace('</table>','</table><dl class="sc_footnotes"><dt><sup>1</sup></dt><dd><p>A seminar is recommended, not required.</p></dd></dl>')
    result=parse(html)
    assert next(r for r in result['requirements'] if r['kind']=='choose_credits')['credits']==4
    assert result['courses'][0]['name']=='Design'
    assert any('recommended, not required' in r['summary'] for r in result['requirements'])


def test_single_selection_pool_with_bundle_is_an_alternative():
    rows='<tr><td>Complete one of the following:</td><td class="hourscol">4-5</td></tr>'+row('ENVR 2500','Statistics','',bundle=('ENVR 2501','Lab'))+row('MATH 3000','Statistics')
    result=parse(document(rows))
    choice=next(r for r in result['requirements'] if r['kind']=='alternative')
    assert choice['count'] is None
    assert '4-5 semester hours' in choice['summary']
    assert len([r for r in result['requirements'] if r['parent_id']==choice['id']])==2


def test_unhandled_number_word_does_not_turn_choices_into_required_courses():
    rows='<tr><td>Complete fourteen courses from the following:</td><td class="hourscol">56</td></tr>'+row('LING 3000','Linguistics')
    with pytest.raises(ValueError,match='Unsupported choice count'):
        parse(document(rows))


def test_next_unindented_subsection_ends_previous_choice():
    rows='<tr class="areaheader"><td>Physics</td></tr><tr class="areasubheader"><td>Physics 1</td></tr><tr><td>Complete one of the following:</td><td class="hourscol">5</td></tr>'+row('PHYS 1000','First Physics','',bundle=('PHYS 1001','Lab'))+'<tr class="areasubheader"><td>Physics 2</td></tr>'+row('PHYS 2000','Second Physics','5')
    result=parse(document(rows));second=next(r for r in result['requirements'] if r['title']=='PHYS 2000')
    assert next(r for r in result['requirements'] if r['id']==second['parent_id'])['title']=='Physics 2'


def test_named_options_group_whole_sequences_and_then_end():
    rows='<tr class="areaheader"><td>Science</td></tr><tr class="areasubheader"><td>Biology</td></tr><tr><td>Complete one of the following options:</td><td class="hourscol">8-10</td></tr><tr><td>Option 1</td></tr>'+row('BIOL 1000','Biology')+row('BIOL 2000','More Biology')+'<tr><td>Option 2</td></tr>'+row('BIOL 1100','Biology With Lab','',bundle=('BIOL 1101','Lab'))+'<tr class="areasubheader"><td>Psychology</td></tr>'+row('PSYC 1101','Psychology','4')
    result=parse(document(rows));option=next(r for r in result['requirements'] if r['kind']=='alternative')
    assert {r['title'] for r in result['requirements'] if r['parent_id']==option['id']}=={'Option 1','Option 2'}
    psych=next(r for r in result['requirements'] if r['title']=='PSYC 1101')
    assert next(r for r in result['requirements'] if r['id']==psych['parent_id'])['title']=='Psychology'


def test_distribution_credit_minimum_and_each_list_are_retained():
    rows='<tr><td>Complete 16 semester hours of the following (at least one course must be taken from each list):</td><td class="hourscol">16</td></tr>'
    for title,code in [('Ecology','EEMB 1000'),('Evolution','EEMB 2000'),('Analysis','EEMB 3000')]:
        rows+=f'<tr class="areaheader"><td>{title}</td></tr>'+row(code,title)
    result=parse(document(rows));credits=next(r for r in result['requirements'] if r['kind']=='choose_credits')
    groups=[r for r in result['requirements'] if r['parent_id']==credits['id']]
    assert len(groups)==3 and all(r['count']==1 for r in groups)
    assert all('At least one' in r['summary'] for r in groups)


def test_course_title_parentheses_are_not_requirement_annotations():
    result=parse(document(row('HLTH 5280','The (in)Visibility of (dis)Ability in Society')))
    assert result['courses'][0]['name']=='The (in)Visibility of (dis)Ability in Society'


def test_course_options_do_not_capture_the_next_area():
    rows='<tr class="areaheader"><td>Chemistry elective</td></tr><tr><td>Complete one course from the following options:</td><td class="hourscol">4</td></tr>'+row('CHEM 3000','Chemistry')+'<tr class="areaheader"><td>Math</td></tr>'+row('MATH 1000','Calculus')
    result=parse(document(rows));math=next(r for r in result['requirements'] if r['title']=='Math')
    parent=next(r for r in result['requirements'] if r['id']==math['parent_id'])
    assert parent['title']=='Biology Requirements'


def test_distribution_minimum_survives_course_lab_options():
    rows='<tr><td>Complete 16 semester hours of the following (at least one course must be taken from each list):</td><td class="hourscol">16</td></tr><tr class="areaheader"><td>Ecology</td></tr>'+row('EEMB 1000','Ecology','',bundle=('EEMB 1001','Lab'))+row('EEMB 2000','Evolution')
    result=parse(document(rows));group=next(r for r in result['requirements'] if r['title']=='Ecology')
    assert group['kind']=='choose_courses' and group['count']==1 and 'At least one' in group['summary']


def test_reviewed_pooled_subheaders_keep_one_selection_pool():
    rows='<tr class="areaheader"><td>Environmental Electives</td></tr><tr><td>Complete any 4 courses from this list:</td><td class="hourscol">16-19</td></tr><tr class="areasubheader"><td>Earth</td></tr>'+row('ENVR 1000','Earth')+'<tr class="areasubheader"><td>Society</td></tr>'+row('ENVR 2000','Environment')
    result=parse_catalog(document(rows),program_id='test-program',title=TITLE,url=URL,required_sections=['Biology Requirements'],pooled_subheaders=['Environmental Electives'])
    choice=next(r for r in result['requirements'] if r['kind']=='choose_courses')
    assert choice['count']==4
    assert all(r['parent_id']==choice['id'] for r in result['requirements'] if r['course_ids'])


def test_overview_combination_restriction_is_source_guarded():
    html=document(row('EEMB 1000','Ecology'),overview='Students cannot combine majors in biology.')
    args=dict(program_id='test-program',title=TITLE,url=URL,required_sections=['Biology Requirements'],overview_rules=[('cannot combine majors in biology','Combination restriction','Biology major combination is not permitted.')])
    result=parse_catalog(html,**args)
    assert any(r['title']=='Combination restriction' for r in result['requirements'])
    changed=parse_catalog(html.replace('cannot combine majors in biology','different policy'),**args)
    assert not any(r['title']=='Combination restriction' for r in changed['requirements'])
