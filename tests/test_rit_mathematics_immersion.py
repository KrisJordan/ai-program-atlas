import copy
import json
from pathlib import Path
import pytest
from atlas.adapters.rit_mathematics_immersion import PID, SID, parse
ROOT=Path(__file__).resolve().parents[1]


def fixture():
    # Synthetic, not a copied source fixture. Changed cardinality/amounts must be observed.
    def table(role,rows):
        return '<table class="sc_courselist"><tbody><tr><td>'+role+'</td></tr>'+''.join('<tr><td><span class="code_bubble">'+code+'</span></td><td>'+name+'</td><td></td></tr>' for code,name in rows)+'</tbody></table>'
    return ('<main><h1>Mathematics Immersion</h1><h2>Curriculum for 2026-2027 for Mathematics Immersion</h2>'+
            table('Prerequisites',[('MATH-171','Calculus A')])+table('Electives',[('MATH-367H','Honors Codes and Ciphers')])+
            '<p>Select three eligible courses. No program overlap.</p></main><div class="courseblock"><span class="detail-code">MATH-367H</span><span class="detail-title">Honors Codes and Ciphers</span><span class="detail-hours_html">(3 Credits)</span><div class="courseblockextra">Synthetic cryptography and historical-source course.</div><span class="detail-requisites">Honors status or 3.3 GPA.</span></div>')


def test_rendered_roles_honors_identity_and_changed_observations():
    a=parse(fixture());b=parse(fixture().replace('(3 Credits)','(4 Credits)').replace('3.3 GPA','3.5 GPA'))
    assert [x['role'] for x in a['observed_immersion_tables']]==['Prerequisites','Electives']
    assert a['courses'][0]['code']=='MATH-367H'
    assert a['courses'][0]['credits']==3 and b['courses'][0]['credits']==4
    assert '3.5' in b['courses'][0]['prerequisites']
    assert a['courses'][0]['credit_unit']=='unknown' # semester normalization is separately reviewed D01.4 evidence
    assert a['requirements']==[]
    assert not {'curriculum_audit','last_verified','curriculum_status'} & a.keys()
    assert 'category_review' not in a['courses'][0]


@pytest.mark.parametrize('before,after',[('2026-2027','2025-2026'),('Mathematics Immersion','Some Other Immersion'),('class="sc_courselist"','class="empty"'),('class="courseblockextra"','class="missing"')])
def test_missing_context_and_shells_rejected(before,after):
    with pytest.raises(ValueError):parse(fixture().replace(before,after))


def test_duplicates_unbound_cards_and_login_rejected():
    with pytest.raises(ValueError,match='Access'):parse('<input type="password">'+fixture())
    with pytest.raises(ValueError,match='Unbound'):parse(fixture().replace('<span class="detail-code">MATH-367H','<span class="detail-code">MATH-999'))
    card=fixture().split('</main>')[1]
    with pytest.raises(ValueError,match='Duplicate rendered'):parse(fixture()+card)


def test_manual_scope_roles_and_exact_profile():
    from atlas.curriculum_profile import requirement_profile
    from atlas.db import validate_program
    d=json.loads((ROOT/'data/programs'/f'{PID}.json').read_text());validate_program(d)
    m=json.loads((ROOT/'atlas/adapters/rit_mathematics_immersion_reviews.json').read_text())
    assert len(m['courses'])==37 and len(m['prerequisite_codes'])==7
    assert sum(c['role']=='immersion_option' for c in m['courses'].values())==30
    r=next(r for r in d['requirements'] if r['id'].endswith('-mathematics-immersion'))
    assert r['count']==3 and r['kind']=='choose_courses' and len(r['course_ids'])==28
    assert all(not x.endswith(('-math-241','-math-251')) for x in r['course_ids'])
    assert not set(PID+'-'+x.lower() for x in m['prerequisite_codes']) & set(r['course_ids'])
    assert next(x for x in d['requirements'] if x['id']==r['parent_id'])['kind']=='alternative'
    c={x['code']:x for x in d['courses']}
    assert len(c)>=74 and sum(bool(x['description']) for x in c.values())>=71
    assert c['MATH-291']['category']=='human_context'
    assert c['MATH-367']['category']=='systems'
    assert c['MATH-367H']['category_review']['status']=='mixed'
    assert '3.2' in c['MATH-241H']['prerequisites'] and '3.3' in c['MATH-367H']['prerequisites']
    assert 'CHEM-BS' in c['MATH-233']['prerequisites']
    assert '1055-359' in c['MATH-412']['prerequisites']
    assert not d.get('course_identity_groups')
    profile=requirement_profile(d)
    assert [profile[k]['count'] for k in ('required','options','unresolved')]==[23,98,13]
    ledger=json.loads((ROOT/'research/degree-audit/buffalo-delaware-rit.json').read_text())
    row=next(x for x in ledger['programs'] if x['program_id']==PID)
    for k in ('required','options','unresolved'):
        assert profile[k]['categories']==row['expected_profile'][k]['categories']
        assert len(row['expected_course_ids'][k])==profile[k]['count']
    assert row['status']=='in_progress' and d['curriculum_status']=='partial'
