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


def cssh_document():
    return '''<main id="content"><h1>Transfer Credit Guidelines</h1><p>Students must petition to have the credit count; petitions are reviewed by the Office of the Provost. Before registering for any courses at an institution outside of Northeastern, keep an approved petition on file; requests after a student has enrolled or completed the coursework potentially may not be approved. Credits must come from an approved and accredited institution. Students must earn a C or higher. Pass/fail courses will not transfer. Award the number of credits as the other institution attributes to the course or less. A maximum of 80 credits from a four-year institution and 60 credits from a two-year institution (combined total of 80). Courses may not be Remedial/Developmental/ESL/Physical Education/Non-academic. Students have up to one semester after matriculation to finalize transfer credit. Submit a course description and syllabus for evaluation, with an official, approved evaluation from a Northeastern University evaluator. Provide an official transcript in its original sealed envelope. Opened transcripts cannot be accepted; electronic records are emailed directly to your academic advisor.</p></main>'''


def test_cssh_transfer_limits_are_conditional_and_semantic_changes_fail():
    from atlas.adapters.northeastern_college_policies import parse_cssh_transfer
    p=parse_cssh_transfer(cssh_document(),program_id='test')
    assert len(p['requirements'])==5 and not p['courses']
    assert all(r['kind']=='note' and not r['course_ids'] for r in p['requirements'])
    assert 'does not itself assign' in p['requirements'][0]['summary']
    for old,new in [('C or higher','D or higher'),('Pass/fail courses will not transfer','Pass/fail courses will transfer'),('combined total of 80','combined total of 100'),('Transfer Credit Guidelines','Other rules')]:
        assert old in cssh_document()
        with pytest.raises(ValueError):parse_cssh_transfer(cssh_document().replace(old,new),program_id='test')


def test_five_explicit_cssh_partners_register_only_conditional_transfer_rules():
    from atlas.adapters.northeastern_college_policies import CSSH_TRANSFER_URL
    expected={'economics','sociology','criminal-justice','philosophy','international-affairs'}
    cache=ROOT/'.cache/research/degree-audit-northeastern/home-12.html'
    for slug in expected:
        pid=f'northeastern-university-artificial-intelligence-and-{slug}-bs-boston-bs-degree'
        p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());m=import_module('atlas.adapters.'+pid+'.adapter')
        rows={r['id']:r for r in p['requirements'] if r['source_id']==pid+'-cssh-transfer-policy'}
        assert len(rows)==5 and all(r['kind']=='note' and not r['course_ids'] for r in rows.values())
        assert CSSH_TRANSFER_URL in m.SOURCES
        if cache.exists():assert {r['id']:r for r in m.SOURCE_PARSERS[CSSH_TRANSFER_URL](cache.read_text())['requirements']}==rows


SCIENCE_PARTNERS={'biology','biochemistry','chemistry','behavioral-neuroscience','ecology-and-evolutionary-biology','environmental-and-sustainability-sciences','linguistics','mathematics','physics','psychology'}


def test_ten_verified_science_variants_keep_conditional_semester_vs_cumulative_rules():
    from atlas.adapters.northeastern_college_policies import SCIENCE_URL
    for slug in SCIENCE_PARTNERS:
        pid=f'northeastern-university-artificial-intelligence-and-{slug}-bs-boston-bs-degree'
        p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());m=import_module('atlas.adapters.'+pid+'.adapter')
        rules={r['id']:r for r in p['requirements'] if r['source_id']==pid+'-science-college-policy'}
        assert len(rules)==9 and all(r['kind']=='note' and not r['course_ids'] for r in rules.values())
        assert SCIENCE_URL in m.SOURCES
        first=rules[pid+'-req-policy-science-first-year-standing']['summary']
        later=rules[pid+'-req-policy-science-later-standing']['summary']
        assert 'semester GPA below 1.800' in first
        assert 'cumulative overall GPA below 2.000' in later
        assert 'does not assign' in rules[pid+'-req-policy-science-conditional']['summary']
        assert 'before that semester' in rules[pid+'-req-policy-science-reduced-load']['summary']
        assert 'Disability Access Services' in rules[pid+'-req-policy-science-reduced-load']['summary']


def test_optional_science_actual_source_replay_and_changed_scope_guards():
    from atlas.adapters.northeastern_college_policies import parse_science_policy
    cache=ROOT/'.cache/research/degree-audit-northeastern/home-19.html'
    if not cache.exists():pytest.skip('Optional ignored official Science policy source')
    html=cache.read_text()
    for slug in SCIENCE_PARTNERS:
        pid=f'northeastern-university-artificial-intelligence-and-{slug}-bs-boston-bs-degree';p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())
        assert {r['id']:r for r in parse_science_policy(html,program_id=pid)['requirements']}=={r['id']:r for r in p['requirements'] if r['source_id']==pid+'-science-college-policy'}
    # Alter actual policy meaning rather than deriving a fixture from parser guards.
    for old,new in [('semester GPA','cumulative GPA'),('1.800','1.500'),('up to two semesters','up to three semesters'),('College of Science','College of Other Studies')]:
        assert old in html
        with pytest.raises(ValueError):parse_science_policy(html.replace(old,new),program_id='test')
