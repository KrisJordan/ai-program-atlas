from importlib import import_module
from pathlib import Path
import pytest

m = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_departments')


def economics():
    shared = ('three subjects; 14.03 for 14.01; 5 on the AP Micro exam; '
              'primary major is Economics (14-1) or Mathematical Economics (14-2); '
              'secondary major is Economics (14-1) or Mathematical Economics (14-2); '
              'Computer Science, Economics, and Data Science (6-14)')
    return f'''<main><h1>Minor and Concentrations</h1><h2>Minor</h2><ul><li>14.999 Minor-only subject</li></ul>
      <div class="accordion"><h3>Concentration in Economics</h3><p>{shared}</p>
      <p>and/or; One or two of:; not acceptable: 14.30, 14.32, 14.33, and 14.47; must take replacement subject(s) for 14.01/14.02</p>
      <ul><li>14.01 Synthetic Micro* and/or</li><li>14.02 Synthetic Macro</li><li>One or two of:<ul><li>14.03 Synthetic Advanced</li><li>14.66 Synthetic Elective (Prereq. 14.03)</li></ul></li></ul></div>
      <div class="accordion"><h3>Concentration in Development Economics</h3><p>{shared}</p>
      <p>14.01 and two of 14.74, 14.75, and 14.76; Other advanced subjects in development economics will be considered as substitutes on request; can also be used toward the minor</p>
      <ul><li>14.01 Synthetic Micro</li><li>14.73 Synthetic Poverty (Not offered 26-27)</li><li>One of:<ul><li>14.74 Synthetic A</li><li>14.75 Synthetic B</li><li>14.76 Synthetic C</li></ul></li></ul></div></main>'''


def philosophy():
    return '''<main><h1>Concentration in Philosophy</h1><div id="major"><p>24.999 Major-only Subject</p></div>
      <div id="concentrate"><p>total of three (9 or 12 unit) course 24 subjects; no more than two; 24.00 – 24.09; 24.C40; well-distributed; One philosophy subject taught at MIT’s Concourse Program; registers for them using the other department’s subject number; specific MIT philosophy subject; only if approved by the philosophy transfer credit examiner; Non-HASS subjects cannot be counted; Both forms are reviewed and approved</p></div>
      <div id="ethicsconcentration"><h1>Concentration in Ethics</h1><p>at least three subjects in ethics; at least two philosophy subjects in ethics; at least one of which must be at a non-introductory level; an elective subject in ethics; its number is at least 24.1; Full list of subjects in ethics; may petition the Ethics Concentration Advisor; Non-HASS subjects cannot be counted; Both forms are reviewed and approved</p>
      <blockquote><p>24.02 Synthetic Intro<br>24.123J/ 17.456J Synthetic Advanced</p></blockquote>
      <blockquote><p>24.02 Synthetic Intro<br>24.123J/ 17.456J Synthetic Advanced<br>STS.022J21A.407J Synthetic Printed Anomaly</p></blockquote></div></main>'''


def test_economics_isolates_minor_and_extracts_changed_options():
    d = m.parse_economics(economics())
    assert all(c['code'] != '14.999' for c in d['courses'])
    assert any(c['code'] == '14.66' and c['prerequisites'] == '14.03' for c in d['courses'])
    assert all(c['credits'] is None for c in d['courses'])
    routes = [r for r in d['requirements'] if r['id'].startswith('mit-ai-hass-economics-route-') and r['kind'] == 'choose_courses']
    assert [r['count'] for r in routes] == [1, 2, 2, 1]
    assert sum(r['kind'] == 'alternative' for r in d['requirements']) == 2
    assert any('14.73' in r['summary'] and 'not offered' in r['summary'] for r in d['requirements'])
    assert 'curriculum_audit' not in d and 'last_verified' not in d


def test_changed_economics_replacement_policy_rejected():
    with pytest.raises(ValueError, match='condition changed'):
        m.parse_economics(economics().replace('must take replacement subject(s)', 'need not replace subjects'))
    with pytest.raises(ValueError, match='accordion missing'):
        m.parse_economics(economics().replace('Concentration in Economics', 'Economics minor'))


def test_philosophy_open_rule_and_ethics_nested_overlay():
    d = m.parse_philosophy(philosophy())
    assert len(d['courses']) == 3
    assert not any(c['code'] == '24.999' for c in d['courses'])
    assert any(c['code'] == 'STS.022J21A.407J' for c in d['courses'])
    root_rule = next(r for r in d['requirements'] if r['id'].endswith('philosophy-three'))
    assert root_rule['count'] == 3 and root_rule['course_ids'] == []
    ethics = next(r for r in d['requirements'] if r['id'].endswith('ethics-philosophy'))
    overlay = next(r for r in d['requirements'] if r['id'].endswith('ethics-nonintro'))
    assert ethics['count'] == 2 and overlay['count'] == 1
    assert len(overlay['course_ids']) == 1 and set(overlay['course_ids']) < set(ethics['course_ids'])
    assert d['requirements'][-1]['id'].endswith('printed-identities')
    assert 'curriculum_status' not in d


def test_ethics_subset_and_material_guards():
    with pytest.raises(ValueError, match='subset missing'):
        m.parse_philosophy(philosophy().replace('24.123J/ 17.456J Synthetic Advanced', '24.124J/ 17.456J Synthetic Advanced', 1))
    with pytest.raises(ValueError, match='condition changed'):
        m.parse_philosophy(philosophy().replace('Non-HASS subjects cannot be counted', 'New HASS policy'))


def test_politics_open_plan_keeps_advice_distinct_from_requirement():
    html = '''<main><h1>Concentrate in Political Science</h1><p>three-subject concentration; focused, cohesive grouping; cannot be comprised of three introductory-level subjects; One subject in a concentration may be taken outside; consult with the Concentration advisor; Two-digit subjects are introductory; recommended that it be taken first</p></main>'''
    d = m.parse_politics(html)
    assert d['requirements'][1]['count'] == 3
    assert 'not required first' in d['requirements'][1]['summary']
    assert 'courses' not in d
    with pytest.raises(ValueError):
        m.parse_politics(html.replace('One subject in a concentration may be taken outside', 'All subjects may be outside'))


@pytest.mark.parametrize('key,parser', [('economics', m.parse_economics), ('philosophy', m.parse_philosophy), ('political-science', m.parse_politics)])
def test_optional_actual_page_replay(key, parser):
    path = Path('/tmp/atlas-mit-hass-' + key + '.html')
    if not path.exists():
        pytest.skip('Optional reviewed source cache')
    d = parser(path.read_text())
    assert d['requirements']
    assert len({c['id'] for c in d.get('courses', [])}) == len(d.get('courses', []))


def test_pdf_subjects_deduplicate_across_reference_groups_and_keep_conditions():
    pdf = import_module('atlas.adapters.mit-ai-decision-making-bs.political_pdf')
    text = 'Political Science Classes in Subfields\n'
    for area in pdf.AREAS:
        text += area + '\n17.01J - Synthetic Intro\n'
    text += '17.307 - American Public Policy for Washington Interns (open only to students admitted to the\nMIT Washington Summer Internship Program)\n17.567 - Synthetic Country (9 unit IAP version for students accepted into\nthe MISTI Israel Program))\n'
    d = pdf.parse_text(text)
    assert len(d['courses']) == 3
    assert next(c for c in d['courses'] if c['code'] == '17.567')['credits'] == 9
    assert all(r['kind'] == 'note' for r in d['requirements'])
    assert len([r for r in d['requirements'] if '-condition-' in r['id']]) == 2
    assert 'curriculum_audit' not in d
    with pytest.raises(ValueError, match='subfield structure'):
        pdf.parse_text(text.replace('Public Policy\n17.01J', 'Political Economy\n17.01J'))
    with pytest.raises(ValueError, match='restriction'):
        pdf.parse_text(text.replace('open only to students admitted', 'open to anyone admitted'))


def test_optional_political_pdf_text_replay():
    path = Path('/tmp/atlas-mit-political-subfields.txt')
    if not path.exists():
        pytest.skip('Optional public PDF text cache')
    d = import_module('atlas.adapters.mit-ai-decision-making-bs.political_pdf').parse_text(path.read_text())
    assert len(d['courses']) == 66
    assert all('4on' not in c['name'] and '4cs' not in c['name'] for c in d['courses'])
    assert next(c for c in d['courses'] if c['code'] == '17.307')['name'] == 'American Public Policy for Washington Interns'
