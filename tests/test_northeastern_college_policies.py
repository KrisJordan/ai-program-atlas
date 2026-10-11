"""Conditional college policies must not become degree/course assignments."""
import json
from pathlib import Path
from importlib import import_module
import pytest
from atlas.adapters.northeastern_college_policies import parse_khoury_policy,KHOURY_URL
ROOT=Path(__file__).resolve().parents[1]


def document():
    return '''<main id="main"><h1>Academic Policies and Procedures</h1>
<h3>Academic progression standards</h3><p>It is expected that full-time Khoury students enroll in four courses with appropriate labs and recitations and complete at least 12 semester hours each academic semester. Any exceptions to the course load requirement must be approved before the semester. Pass/fail courses are restricted to electives outside of the major, minor, and NUpath requirements.</p>
<h3>GPA requirements for graduation</h3><p>Require2.000 in major (CS/CY/AI) courses and2.000 overall.</p>
<h3>Criteria for academic probation</h3><p>Not following a program of study approved by the student’s academic advisor; Not earning at least 12 semester hours in each academic full-term semester.</p>
<h4>First-year students</h4><p>Maintain overall cumulative GPA of at least 1.800 at the end of each full-term semester and GPA of at least 2.000 in the major at the end of the second academic full-term semester.</p>
<h4>Upperclass and transfer students</h4><p>Maintain overall cumulative GPA of at least 2.000 and GPA of at least 2.000 in the major at the end of the second academic full-term semester of the curriculum completed on campus and each full-term academic semester thereafter.</p>
<h3>Academic dismissal from major</h3><p>Require GPA of at least 2.000 in the major at the end of the third academic full-term semester. Students off their plan for more than one semester may be dismissed. Eligible students may remain as a transitional major for one semester.</p>
<h3>Changing to Khoury College from a non-Khoury major</h3>
<h4>Admission requirements for students changing majors</h4><p>Must be in good academic standing. Must have overall GPA of 2.0 or higher in Khoury classes. Successful completion of CS 2000/2001 or CS 2100/2101 or DS 2500/DS 2501 (whichever comes first). Students are not eligible for a major change based on passing the CS 2000/2001 placement test alone. Until eligible, remain in your current college as a transitional student. For admission into CS/Business, CY/Business, or AI/Business, a GPA of 2.0 or higher average in any business courses is required.</p>
<h3>Guided self-placement test for students changing majors</h3><p>Students currently in a Khoury combined major, but not in Khoury College as their home college must meet with their assigned Khoury secondary academic advisor. If the combined major you want is offered by your home college, you can choose to stay in your home college.</p>
<h3>Preparing to graduate</h3><p>Clearance by Khoury advising office and the university registrar’s office. Review and approve your official Graduation Clearance Contract. Apply to graduate on the Student Hub. Notify your academic advisor of any changes in registration or graduation plans.</p></main>'''


def test_conditional_rules_never_invent_home_college_or_course_obligations():
    p=parse_khoury_policy(document(),program_id='test')
    assert p['courses']==[] and len(p['requirements'])==11
    assert all(r['kind']=='note' and not r['course_ids'] for r in p['requirements'])
    root=p['requirements'][0]
    assert root['parent_id'] is None and 'do not resolve' in root['summary']
    entry=next(r for r in p['requirements'] if r['id'].endswith('transfer-entry'))
    assert 'conditional entry pathways' in entry['summary'] and 'Placement alone does not' in entry['summary']
    business=next(r for r in p['requirements'] if r['id'].endswith('business-transfer'))
    assert 'Only when applying' in business['summary'] and 'unrelated degrees' in business['summary']
    assert 'curriculum_audit' not in p and 'last_verified' not in p


@pytest.mark.parametrize('old,new',[
 ('Academic Policies and Procedures','Other policies'),
 ('2.0 or higher in Khoury classes','1.0 or higher in Khoury classes'),
 ('not eligible for a major change based on passing','eligible for a major change based on passing'),
 ('second academic full-term semester of the curriculum completed on campus','fourth academic semester'),
 ('as a transitional major for one semester','as a transitional major for two semesters'),
])
def test_changed_identity_threshold_or_scope_fails_review(old,new):
    with pytest.raises(ValueError):parse_khoury_policy(document().replace(old,new),program_id='test')


def test_navigation_mentions_cannot_supply_missing_policy_body():
    with pytest.raises(ValueError):parse_khoury_policy('<nav>'+document()+'</nav><main id="main"><h1>Other page</h1></main>',program_id='test')


def test_all24_registered_adapters_preserve_scoped_reviewed_policy_graph():
    from atlas.families import resolve_program
    family=json.loads((ROOT/'data/families/northeastern-ai-combined-degrees.json').read_text())
    cache=ROOT/'.cache/research/degree-audit-northeastern/home-8.html'
    count=0
    for path in (ROOT/'data/programs').glob('northeastern*.json'):
        p=json.loads(path.read_text())
        if p['program_kind']!='degree':continue
        count+=1;m=import_module('atlas.adapters.'+p['id']+'.adapter')
        assert KHOURY_URL in m.SOURCES and KHOURY_URL in m.SOURCE_PARSERS
        resolved=resolve_program(p,family if p.get('family') else None)
        stored=[r for r in resolved['requirements'] if r['source_id']==p['id']+'-khoury-advising-policy']
        assert len(stored)==11 and all(r['kind']=='note' and not r['course_ids'] for r in stored)
        if cache.exists():
            observed=m.SOURCE_PARSERS[KHOURY_URL](cache.read_text())['requirements'];lookup={r['id']:r for r in stored}
            for r in observed:assert all(lookup[r['id']][k]==v for k,v in r.items())
    assert count==24
