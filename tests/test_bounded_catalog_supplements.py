"""Synthetic source-shaped observations for independent public policy sources."""
from importlib import import_module
import hashlib
import json
from pathlib import Path
import pytest

PIDS = {
 'cornell': 'cornell-university-artificial-intelligence-minor-minor',
 'clemson': 'clemson-university-artificial-intelligence-minor-minor',
 'usc': 'university-of-southern-california-applied-ai-in-business-minor-minor',
 'usf': 'university-of-south-florida-artificial-intelligence-bs-degree',
 'vt': 'virginia-tech-artificial-intelligence-ai-minor-minor',
}

def adapter(key):
    return import_module('atlas.adapters.'+PIDS[key]+'.adapter')

def page(text):
    return '<main>'+text+'</main>'

FIXTURES = {
 ('cornell','parse_info3170'): page('''Fall 2026; 2026-2027 Catalog
 <h3 id="head-INFO-3170">INFO 3170<div class="title-coursedescr">Understanding AI and Society</div></h3>
 <p class="catalog-descr">AI technologies shape - and are shaped by - society. We compare quantitative and qualitative studies of responsible development, deployment, and governance.</p>
 <span class="credit-val">3</span> GradeNoAud'''),
 ('clemson','parse_advising_faq'): page('''Advising FAQ. Check your undergraduate announcements.
 Generally, if a CPSC course counts beyond general electives, retake that class for a C or higher.
 For non-CPSC-prefixed courses: Transfer Course Equivalency List; Approval of Coursework to be Taken Elsewhere.
 For CPSC-prefixed coursework: Dr. Plaue; printout of the syllabus; prior to taking a class at another institution.'''),
 ('usc','parse_minor_faq'): page('''QUESTIONS ABOUT MINORS. All courses used to satisfy a Marshall minor requirement must be taken for a letter-grade. D- or higher.
 If you are not a Marshall major, courses must be taken in-residence at USC. Marshall majors have the potential to complete limited minor courses abroad.
 Withdrawing from a Marshall course is considered enrollment; counted as one of the three courses.'''),
 ('usc','parse_minor_resources'): page('''Marshall Minors.
 For Non-Marshall majors, Marshall minor courses cannot be completed abroad through USC-affiliated abroad programs.
 Marshall majors, please speak with your Marshall major advisor.'''),
 ('usf','parse_degreeworks'): page('''Degree Works. Credit Hour Breakdown.
 120: Total degree requirement. 42: Upper-level requirement. 9: Summer requirement.
 30/60: Residency requirement (30 of your last 60 must be completed at USF)'''),
 ('usf','parse_registrar_faq'): page('''Can I be excluded from the summer enrollment requirement?
 Summer employment documented on official employer letterhead every summer term not enrolled; seasonal employment only during summer.
 Academic program courses unavailable summer terms. Unusual hardship due to exceptional circumstances; supporting documentation.
 Apply during the semester in which you apply to graduate. Allow 3 weeks.
 The original and the repeat course must be taken at USF. Limit: three Grade Forgivenesses; no more than one repeat per course; repeat "D" or higher.
 Exclude an "FF" grade indicating academic dishonesty. Once a student is awarded a bachelor's degree, these courses cannot use forgiveness.'''),
 ('vt','parse_catalog_authority'): page('''Checksheets are the legacy documents.
 For the 2024-2025 catalog year and beyond, use the University Catalog for all official course and programmatic curricula information.
 Legacy sheets: 2021-2023 degree requirements. Find catalog year at the top right of your DARS audit.'''),
}

@pytest.mark.parametrize('key,function', FIXTURES)
def test_independent_observations_do_not_certify_curriculum(key,function):
    result=getattr(adapter(key),function)(FIXTURES[key,function])
    assert result['id']==PIDS[key]
    assert not {'curriculum_audit','curriculum_status','last_verified'} & result.keys()
    assert result.get('courses') or result.get('requirements')

@pytest.mark.parametrize('key,function', FIXTURES)
def test_access_page_rejected_even_with_matching_text(key,function):
    with pytest.raises(ValueError):
        getattr(adapter(key),function)('<h1>Access denied</h1>'+FIXTURES[key,function])

@pytest.mark.parametrize('key,function,old,new', [
 ('cornell','parse_info3170','2026-2027 Catalog','2025-2026 Catalog'),
 ('clemson','parse_advising_faq','prior to taking a class at another institution','after completing the class'),
 ('usc','parse_minor_faq','D- or higher','C or higher'),
 ('usc','parse_minor_resources','For Non-Marshall majors','For every student'),
 ('usf','parse_registrar_faq','three Grade Forgivenesses','four Grade Forgivenesses'),
 ('vt','parse_catalog_authority','2021-2023 degree requirements','all current requirements'),
])
def test_material_policy_change_requires_review(key,function,old,new):
    with pytest.raises(ValueError):
        getattr(adapter(key),function)(FIXTURES[key,function].replace(old,new))

def test_roster_metadata_is_term_specific_and_missingness_honest():
    result=adapter('cornell').parse_info3170(FIXTURES['cornell','parse_info3170'])
    c=result['courses'][0]
    assert c['code']=='INFO 3170' and c['credits']==3 and c['credit_unit']=='unknown'
    assert c['prerequisites'] is None and c['syllabus'] is None
    assert 'Fall 2026' in c['description']
    assert 'requirements' not in result  # The roster cannot approve a course for the minor.
    changed=FIXTURES['cornell','parse_info3170'].replace('Understanding AI and Society','Revised Social AI Title').replace('>3</span>','>4</span>')
    c=adapter('cornell').parse_info3170(changed)['courses'][0]
    assert c['name']=='Revised Social AI Title' and c['credits']==4

def test_degreeworks_extracts_fresh_amounts_without_normalization():
    a=adapter('usf');fixture=FIXTURES['usf','parse_degreeworks']
    result=a.parse_degreeworks(fixture.replace('120:', '124:'))
    assert result['requirements'][0]['credits']==124
    assert all(r['kind']=='note' and r['credit_unit']=='unknown' for r in result['requirements'])
    with pytest.raises(ValueError):
        a.parse_degreeworks(fixture.replace('30 of your last','24 of your last'))

def test_all_curated_supplements_remain_partial_and_registered():
    from atlas.db import validate_program
    for pid in PIDS.values():
        p=json.loads((Path('data/programs')/(pid+'.json')).read_text())
        validate_program(p)
        assert p['curriculum_status']=='partial'
        assert p['curriculum_audit']['unresolved_requirements']
        a=import_module('atlas.adapters.'+pid+'.adapter')
        assert set(a.SOURCES) <= {s['url'] for s in p['sources']}

@pytest.mark.parametrize('key,function', FIXTURES)
def test_optional_permitted_live_cache_replay(key,function):
    a=adapter(key);f=getattr(a,function)
    url=next(u for u,p in a.SOURCE_PARSERS.items() if p==f)
    path=Path('.cache/http')/(hashlib.sha256(url.encode()).hexdigest()+'.body')
    if not path.exists():pytest.skip('Optional local source cache unavailable')
    result=f(path.read_text())
    assert result['id']==PIDS[key]
    assert not {'curriculum_audit','curriculum_status','last_verified'} & result.keys()
