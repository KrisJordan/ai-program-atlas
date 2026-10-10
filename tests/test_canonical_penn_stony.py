"""Current official-host source observations preserve eligibility and classification."""
import hashlib,importlib,json
from pathlib import Path
import pytest
from bs4 import BeautifulSoup
from atlas.db import validate_program
from atlas.adapters.penn_bse.canonical_handbook import parse,parse_writing,URL
ROOT=Path(__file__).resolve().parents[1]
STONY=importlib.import_module('atlas.adapters.stony-brook-ai-business-innovation-specialization.adapter')


def test_writing_worksheet_categories_do_not_become_mandatory_courses():
    html='<main><div id="faq_64"><table><tr><th>Course</th><th>Title</th><th>Category</th></tr><tr><td>WRIT0100</td><td>Synthetic seminar</td><td>H</td></tr><tr><td>WRIT 1380</td><td>Synthetic tutoring</td><td>FE</td></tr><tr><td>WRIT0320</td><td>Synthetic topic</td><td>-</td></tr></table></div></main>'
    courses,rules=parse_writing(BeautifulSoup(html,'html.parser'))
    assert [c['code'] for c in courses]==['WRIT 0100','WRIT 1380','WRIT 0320']
    assert all(c['credits'] is None for c in courses)
    assert all(r['kind']=='note' for r in rules)
    fe=next(r for r in rules if 'FE' in r['title'])
    assert 'does not automatically fill SS/H' in fe['summary']
    unknown=next(r for r in rules if r['id'].endswith('unknown'))
    assert 'advising review' in unknown['summary']
    with pytest.raises(ValueError):parse_writing(BeautifulSoup(html.replace('<td>H</td>','<td>NEW</td>'),'html.parser'))


def stony_fixture():
    return '<main><h1>Specializations</h1><h2>Bachelors of Science in Business Management Specializations</h2><p>AI for Business Innovation. Students planning to graduate by May 2027 are not eligible to declare this specialization. Business Major Specialization Declaration Form. A course cannot be used to fulfill two areas of specialization. No more than 6 transfer credits with approval of the Director of Undergraduate Studies. Transcript after graduation, but not on your degree. Complete a new declaration form. Declare after you have taken all of your fundamental classes. Not all specialization courses are offered every academic year.</p></main>'


def test_stony_graduation_cohort_is_not_a_launch_date():
    observed=STONY.parse(stony_fixture())
    assert observed['program_kind']=='concentration' and len(observed['requirements'])==6
    assert 'first_offered' not in observed and 'curriculum_status' not in observed
    assert 'May 2027' in observed['requirements'][0]['summary']
    with pytest.raises(ValueError):STONY.parse(stony_fixture().replace('May 2027','May 2028'))
    with pytest.raises(ValueError):STONY.parse(stony_fixture().replace('6 transfer credits','9 transfer credits'))
    with pytest.raises(ValueError):STONY.parse('<h1>Sign in</h1><input type="password">'+stony_fixture())


@pytest.mark.parametrize('pid',['penn-bse-ai',STONY.PROGRAM_ID])
def test_reviewed_partial_records_have_registered_sources_and_gaps(pid):
    p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());validate_program(p)
    assert p['curriculum_status']=='partial' and p['curriculum_audit']['unresolved_requirements']
    module=importlib.import_module('atlas.adapters.penn_bse.adapter') if pid=='penn-bse-ai' else STONY
    assert set(module.SOURCES)<={s['url'] for s in p['sources']}
    if pid==STONY.PROGRAM_ID:assert p['first_offered'] is None and not p['courses']


def test_cached_canonical_handbook_observes_current_policies():
    path=ROOT/'.cache/http'/(hashlib.sha256(URL.encode()).hexdigest()+'.body')
    if not path.exists():pytest.skip('Optional local evidence cache unavailable')
    html=path.read_text();d=parse(html)
    assert len(d['courses'])==49 and len(d['requirements'])==18
    assert not {'curriculum_audit','curriculum_status','last_verified'}&d.keys()
    assert any('40-unit' in r['summary'] and 'Do not impose' in r['summary'] for r in d['requirements'])
    assert any('omits ARIN' in r['summary'] for r in d['requirements'])
    with pytest.raises(ValueError):parse(html.replace('minimum cumulative GPA of 2.0','minimum cumulative GPA of 2.5'))
    with pytest.raises(ValueError):parse(html.replace('faq_65','faq_removed'))
