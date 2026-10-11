from importlib import import_module
from pathlib import Path
import pytest
m = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_open_fields')


def test_anthropology_scope_credits_and_dynamic_rows():
    html = '''<main><h1>MIT Anthropology Requirements</h1><article><hr><p><strong><u>Concentration</u></strong><br>Three subjects (minimum of 33 credits):</p><ul><li>One of the following:<ul><li>21A.999 Synthetic Intro</li></ul></li><li>Two additional Anthropology subjects</li></ul><hr><p>Minor</p><ul><li>21A.888 Minor-only subject</li></ul></article></main>'''
    d = m.parse_anthropology(html)
    assert [c['code'] for c in d['courses']] == ['21A.999']
    assert d['requirements'][-1]['credits'] == 33 and d['requirements'][-1]['credit_unit'] == 'unknown'
    assert d['requirements'][2]['count'] == 2 and d['requirements'][2]['course_ids'] == []
    with pytest.raises(ValueError):
        m.parse_anthropology(html.replace('minimum of 33 credits', 'minimum of 30 credits'))


def test_history_current_concentration_section_only():
    html = '''<main><h1>Undergraduate Studies</h1><details><summary>History Concentration</summary><p>A History concentration consists of three subjects; At most two may be an introductory level course; There are no geographical distribution requirements; At least two of these subjects must be taken at MIT; may apply their History concentration subjects to a History minor</p></details></main>'''
    d = m.parse_history(html)
    assert d['requirements'][1]['count'] == 3
    assert d.get('courses', []) == []
    with pytest.raises(ValueError):
        m.parse_history('<h1>21H.392 Undergraduate Independent Study</h1>')


def test_linguistics_required_alternatives_and_open_final_slot():
    html = '''<main><h1>Undergraduate HASS Concentration in Linguistics</h1><p>Three subjects, which must include: 24.900 (Introduction to Linguistics) or 24.9000 (How Language Works); one subject chosen from 24.901 (Phonology), 24.902 (Syntax), 24.903 (Semantics); one other subject in linguistics; only HASS classes can fulfill</p></main>'''
    d = m.parse_linguistics(html)
    assert [len(r['course_ids']) for r in d['requirements'][1:]] == [2, 3, 0]
    assert all(r['count'] == 1 for r in d['requirements'][1:])
    assert 'curriculum_status' not in d and 'last_verified' not in d


def test_sts_pools_do_not_make_tier_one_mandatory():
    html = '<h1>Tier II Subjects</h1><p>recommended that students take at least one Tier I subject, but not required</p><p><a>STS.999 Synthetic Course</a></p>'
    d = m.parse_sts_tier(2, html)
    assert d['requirements'][0]['kind'] == 'note'
    assert d['courses'][0]['code'] == 'STS.999'
    assert d['requirements'][0]['parent_id'] == 'mit-ai-hass-sts'
    with pytest.raises(ValueError):
        m.parse_sts_tier(2, html.replace('but not required', 'and required'))


def test_literature_duplicates_must_agree_and_do_not_import_minor_courses():
    p = '''<div class="et_pb_text_inner"><h2>Concentration</h2><p>three subjects; intermediate tier (400-, 500-, 600-); seminar (700-) tier; Two six-unit samplings courses; 300 and 600- tier; combined by petition; permission of the instructor; must meet with a concentration advisor</p></div>'''
    x = '<p>at most one such subject toward a concentration in Literature; considered the equivalent of a particular subject; General Elective Credit; do not count toward; HASS-Elective Credit</p>'
    d = m.parse_literature(p+p+x+'<h2>Minor</h2><p>21L.999 Minor Subject</p>')
    assert len(d['requirements']) == 4 and 'courses' not in d
    with pytest.raises(ValueError, match='conflicting'):
        m.parse_literature(p+p.replace('three subjects','four subjects')+x)


@pytest.mark.parametrize('key,fn', [('anthropology',m.parse_anthropology),('history-current',m.parse_history),('linguistics',m.parse_linguistics),('women-s-and-gender-studies',m.parse_wgs),('literature',m.parse_literature),('urban-studies',m.parse_urban),('science-technology-and-society-sts',m.parse_sts),('sts-tier-i',lambda h:m.parse_sts_tier(1,h)),('sts-tier-ii',lambda h:m.parse_sts_tier(2,h)),('sts-transfer',m.parse_sts_transfer)])
def test_optional_reviewed_pages(key,fn):
    p=Path('/tmp/atlas-mit-hass-rest-'+key+'.html')
    if not p.exists():pytest.skip('Optional reviewed public HTML cache')
    d=fn(p.read_text())
    assert d['requirements'] and 'curriculum_audit' not in d
    assert len({c['id'] for c in d.get('courses',[])}) == len(d.get('courses',[]))
