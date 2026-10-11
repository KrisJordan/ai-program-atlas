"""Course metadata comes from live subject blocks, with no reviewed seed replay."""
import pytest
from atlas.adapters.northeastern_course_metadata import parse_subject, register_subject_sources


def page(block='', heading='Data Science (DS)'):
    return f'<header id="site-title"><h1>{heading}</h1></header><div id="textcontainer">{block}</div>'


def block(credits='4', prerequisite='CS 2100 with a minimum grade of D-', description='Introduces linear algebra and probability for AI.'):
    return f'''<div class="courseblock"><p class="courseblocktitle"><strong>DS 3000. Mathematical Foundations of Artificial Intelligence. ({credits} Hours)</strong></p><p class="cb_desc">{description}</p><p class="courseblockextra"><strong>Prerequisite(s): </strong>{prerequisite}</p></div>'''


def parse(html):
    return parse_subject(html,program_id='test-program',subject='DS',heading='Data Science (DS)',codes=['DS 3000'],url='https://catalog.northeastern.edu/course-descriptions/ds/')


def test_changed_metadata_changes_observation_and_no_review_claims():
    result=parse(page(block()))
    course=result['courses'][0]
    assert course['credits']==4
    assert 'CS 2100' in course['prerequisites']
    assert course['description']=='Studies the mathematical basis of AI through linear algebra, probability and computational exercises.'
    assert course['source_id']=='test-program-ds-courses'
    changed=parse(page(block('3','CS 2500 with a minimum grade of C')))
    assert changed['courses'][0]['credits']==3
    assert changed['courses'][0]['prerequisites']=='CS 2500 with a minimum grade of C'
    assert 'last_verified' not in result and 'curriculum_audit' not in result
    assert result['requirements']==[]


def test_changed_description_does_not_replay_unsupported_paraphrase():
    assert parse(page(block(description='This course has a different scope.')))['courses'][0]['description'] is None


def test_missing_prerequisite_remains_unknown():
    assert parse(page(block(prerequisite='')))['courses'][0]['prerequisites'] is None


@pytest.mark.parametrize('html',[
    page(block(),heading='Unrelated (XX)'),
    page(''),
    page('')+'<nav>'+block()+'</nav>',
    page(block()+block()),
])
def test_wrong_or_ambiguous_source_rejected(html):
    with pytest.raises(ValueError):parse(html)


def test_additional_description_prerequisite_preserved():
    html=page('''<div class="courseblock"><p class="courseblocktitle">LING 4654. Seminar in Linguistics. (4 Hours)</p><p class="cb_desc">Explores a topic in current linguistics research. Requires prior completion of either two 3000-level LING courses or one 3000-level LING course and permission of instructor.</p><p class="courseblockextra">Prerequisite(s): LING 2350 with a minimum grade of D-</p></div>''',heading='Linguistics (LING)')
    result=parse_subject(html,program_id='test-program',subject='LING',heading='Linguistics (LING)',codes=['LING 4654'],url='https://catalog.northeastern.edu/course-descriptions/ling/')
    prerequisites=result['courses'][0]['prerequisites']
    assert 'LING 2350' in prerequisites and 'two 3000-level LING courses' in prerequisites and 'permission of instructor' in prerequisites


def test_partner_catalog_variable_credit_and_changed_description_remain_observations():
    title='Speech-Language Pathology and Audiology (SLPA)'
    html=page('<div class="courseblock"><p class="courseblocktitle">SLPA 5107. Clinical Procedures. (3-4 Hours)</p><p class="cb_desc">Studies functional analysis of behavior in assessment.</p></div>',heading=title)
    def run(text):return parse_subject(text,program_id='test-program',subject='SLPA',heading=title,codes=['SLPA 5107'],url='https://catalog.northeastern.edu/course-descriptions/slpa/')['courses'][0]
    course=run(html)
    assert course['credits'] is None and course['description'] and course['prerequisites'] is None
    assert run(html.replace('(3-4 Hours)','(4 Hours)'))['credits']==4
    assert run(html.replace('functional analysis of behavior','a different topic'))['description'] is None


def test_discrete_credit_options_and_corequisites_are_not_added_or_relabelled():
    html=page('''<div class="courseblock"><p class="courseblocktitle">CS 4991. Research. (4,8 Hours)</p><p class="cb_desc">Offers students an opportunity to conduct research under faculty supervision.</p><p class="courseblockextra">Prerequisite(s): (CS 3100 with a minimum grade of D- or CIS 310M with a minimum grade of D-); CS 3800 with a minimum grade of D-</p><p class="courseblockextra">Corequisite(s): CS 4992</p></div>''',heading='Computer Science (CS)')
    parser=register_subject_sources('test-program',{'CS':['CS 4991']})['https://catalog.northeastern.edu/course-descriptions/cs/']
    result=parser(html);course=result['courses'][0]
    assert course['credits'] is None and course['credit_unit']=='semester_hours'
    assert '(CS 3100' in course['prerequisites'] and '); CS 3800' in course['prerequisites']
    assert '4992' not in course['prerequisites']
    assert any('4,8 semester hours' in n for n in result['notes'])
    assert any('corequisite(s): CS 4992' in n for n in result['notes'])
    changed=parser(html.replace('(4,8 Hours)','(6 Hours)').replace('CS 4992','CS 4993'))
    assert changed['courses'][0]['credits']==6
    assert any('CS 4993' in n for n in changed['notes'])
    assert not any('4,8' in n or '4992' in n for n in changed['notes'])


def test_required_prose_and_recommended_preparation_remain_distinct():
    required='Requires prior completion of MATH 1341 or permission of head mathematics advisor.'
    recommendation='Prior completion of Calculus 2 is strongly recommended.'
    html=page(f'''<div class="courseblock"><p class="courseblocktitle">MATH 1342. Calculus 2. (4 Hours)</p><p class="cb_desc">Studies convergence of sequences and series. {required}</p></div><div class="courseblock"><p class="courseblocktitle">MATH 2321. Calculus 3. (4 Hours)</p><p class="cb_desc">Develops vector calculus in two and three dimensions. {recommendation}</p></div>''',heading='Mathematics (MATH)')
    parser=register_subject_sources('test-program',{'MATH':['MATH 1342','MATH 2321']})['https://catalog.northeastern.edu/course-descriptions/math/']
    result=parser(html)
    assert 'or permission of head mathematics advisor' in result['courses'][0]['prerequisites']
    assert result['courses'][1]['prerequisites'] is None
    assert any('MATH 2321' in n and 'not a prerequisite' in n for n in result['notes'])
    changed=parser(html.replace(required,'No statement of required preparation.'))
    assert changed['courses'][0]['prerequisites'] is None


def test_registered_subjects_keep_distinct_selectors_and_reject_wrong_catalog():
    parsers=register_subject_sources('test-program',{'CS':['CS 3200'],'MATH':['MATH 1341']})
    cs=page('<div class="courseblock"><p class="courseblocktitle">CS 3200. Databases. (4 Hours)</p><p class="cb_desc">Includes fundamentals of concurrency and recovery.</p></div>',heading='Computer Science (CS)')
    math=page('<div class="courseblock"><p class="courseblocktitle">MATH 1341. Calculus 1. (4 Hours)</p><p class="cb_desc">Introduces the derivative as a limit.</p></div>',heading='Mathematics (MATH)')
    assert parsers['https://catalog.northeastern.edu/course-descriptions/cs/'](cs)['courses'][0]['code']=='CS 3200'
    assert parsers['https://catalog.northeastern.edu/course-descriptions/math/'](math)['courses'][0]['code']=='MATH 1341'
    with pytest.raises(ValueError):parsers['https://catalog.northeastern.edu/course-descriptions/cs/'](math)


def test_zero_hour_recitation_is_known_and_corequisite_remains_concurrent():
    html=page('<div class="courseblock"><p class="courseblocktitle">CHEM 1163. Recitation for CHEM 1161. (0 Hours)</p><p class="cb_desc">Students work interactively with instructors.</p><p class="courseblockextra">Corequisite(s): CHEM 1161, CHEM 1162</p></div>',heading='Chemistry and Chemical Biology (CHEM)')
    parser=register_subject_sources('test-program',{'CHEM':['CHEM 1163']})['https://catalog.northeastern.edu/course-descriptions/chem/']
    result=parser(html)
    assert result['courses'][0]['credits']==0
    assert result['courses'][0]['prerequisites'] is None
    assert any('CHEM 1161, CHEM 1162' in n for n in result['notes'])
    assert parser(html.replace('(0 Hours)','(1 Hour)'))['courses'][0]['credits']==1


def test_concurrent_prerequisite_and_timing_advice_keep_their_source_meaning():
    html=page('<div class="courseblock"><p class="courseblocktitle">PSYC 2320. Statistics in Psychological Research. (4 Hours)</p><p class="cb_desc">Covers descriptive and inferential statistics. Should be taken before the end of the sophomore year.</p><p class="courseblockextra">Prerequisite(s): PSYC 1101 (may be taken concurrently) with a minimum grade of D- or (PSYC 101M with a minimum grade of D-; PSYC 102M with a minimum grade of D-)</p></div>',heading='Psychology (PSYC)')
    parser=register_subject_sources('test-program',{'PSYC':['PSYC 2320']})['https://catalog.northeastern.edu/course-descriptions/psyc/']
    result=parser(html);course=result['courses'][0]
    assert '(may be taken concurrently)' in course['prerequisites']
    assert 'or (PSYC 101M' in course['prerequisites']
    assert 'sophomore' not in course['prerequisites']
    assert any('timing advice' in n and 'sophomore' in n for n in result['notes'])
    changed=parser(html.replace('Should be taken before the end of the sophomore year.',''))
    assert not any('timing advice' in n for n in changed['notes'])


def test_ds_ethics_description_is_guarded_without_inventing_prerequisites():
    html=page('<div class="courseblock"><p class="courseblocktitle">DS 1300. Knowledge in a Digital World. (4 Hours)</p><p class="cb_desc">Studies normative frameworks from epistemology and ethics to evaluate technologies.</p></div>')
    parser=register_subject_sources('test-program',{'DS':['DS 1300']})['https://catalog.northeastern.edu/course-descriptions/ds/']
    result=parser(html)
    assert result['courses'][0]['description'] and result['courses'][0]['prerequisites'] is None
    assert parser(html.replace('normative frameworks from epistemology and ethics','different methods'))['courses'][0]['description'] is None


def test_every_existing_ne_family_ds_course_has_its_own_catalog_metadata():
    import json
    from pathlib import Path
    from atlas.scrape import adapters
    root=Path(__file__).resolve().parents[1];available=adapters();variants=0;observations=0
    for path in (root/'data/programs').glob('northeastern-*.json'):
        p=json.loads(path.read_text())
        if p.get('family',{}).get('id')!='northeastern-ai-combined-degrees':continue
        variants+=1;url='https://catalog.northeastern.edu/course-descriptions/ds/'
        assert list(available[p['id']].SOURCES).count(url)==1
        assert url in available[p['id']].SOURCE_PARSERS
        for c in p['courses']:
            if not c['code'].startswith('DS '):continue
            observations+=1
            assert c['description'] and c['credits']==4 and c['credit_unit']=='semester_hours'
            assert c['source_id']==p['id']+'-ds-courses'
            assert any(s['id']==c['source_id'] and s['url']==url for s in p['sources'])
            if c['code']=='DS 1300':assert c['prerequisites'] is None
            else:assert c['prerequisites']
        assert p['curriculum_status']=='partial' and p['curriculum_audit']['unresolved_requirements']
    assert variants==23 and observations==133


def test_physics_concurrent_registration_in_prose_is_not_prior_completion():
    html=page('<div class="courseblock"><p class="courseblocktitle">PHYS 1152. Lab for PHYS 1151. (1 Hour)</p><p class="cb_desc">Accompanies PHYS 1151. Requires concurrent registration in PHYS 1151 and PHYS 1153.</p></div>',heading='Physics (PHYS)')
    parser=register_subject_sources('test-program',{'PHYS':['PHYS 1152']})['https://catalog.northeastern.edu/course-descriptions/phys/']
    result=parser(html)
    assert result['courses'][0]['prerequisites'] is None
    assert any('concurrent-registration condition: PHYS 1151 and PHYS 1153' in n for n in result['notes'])
    changed=parser(html.replace('PHYS 1151 and PHYS 1153','PHYS 1151 only'))
    assert any('PHYS 1151 only' in n for n in changed['notes'])
    assert not any('1153' in n for n in changed['notes'])


def test_advanced_writing_grade_is_observed_without_inferring_home_college():
    html=page('<div class="courseblock"><p class="courseblocktitle">ENGW 3302. Advanced Writing in the Technical Professions. (4 Hours)</p><p class="cb_desc">Offers instruction including cross-college combined majors, relevant to technical professions and individual student goals.</p><p class="courseblockextra">Prerequisite(s): ENGW 1111 with a minimum grade of C or ENGW 1102 with a minimum grade of C</p></div>',heading='English Writing (ENGW)')
    parser=register_subject_sources('test-program',{'ENGW':['ENGW 3302']})['https://catalog.northeastern.edu/course-descriptions/engw/']
    result=parser(html)
    assert result['courses'][0]['description']
    assert 'minimum grade of C' in result['courses'][0]['prerequisites']
    assert 'family' not in result and 'hosting_unit' not in result
    assert result['requirements']==[]
    assert 'minimum grade of B' in parser(html.replace('minimum grade of C','minimum grade of B'))['courses'][0]['prerequisites']


@pytest.mark.parametrize(('subject','heading','code','condition','expected'),[
    ('PHIL','Philosophy (PHIL)','PHIL 3822','Requires two prior courses in philosophy or department permission to register.','Registration requires two prior courses in philosophy or department permission'),
    ('ECON','Economics (ECON)','ECON 5650','Requires previous coursework in macroeconomic theory.','Previous coursework in macroeconomic theory'),
])
def test_additional_disciplinary_registration_prose_is_observed(subject,heading,code,condition,expected):
    html=page(f'<div class="courseblock"><p class="courseblocktitle">{code}. A disciplinary course. (4 Hours)</p><p class="cb_desc">{condition}</p></div>',heading=heading)
    parser=register_subject_sources('test-program',{subject:[code]})[f'https://catalog.northeastern.edu/course-descriptions/{subject.lower()}/']
    course=parser(html)['courses'][0]
    assert expected in course['prerequisites']
    assert course['description'] is None  # factual extraction is not an invented summary
    assert parser(html.replace(condition,'No eligibility prose.'))['courses'][0]['prerequisites'] is None


def test_listed_disciplinary_courses_have_catalog_facts_without_forcing_descriptions():
    import json
    from pathlib import Path
    from atlas.adapters.northeastern_course_metadata import SUMMARIES
    root=Path(__file__).resolve().parents[1];observations=0
    for path in (root/'data/programs').glob('northeastern-*.json'):
        p=json.loads(path.read_text())
        if p.get('family',{}).get('id')!='northeastern-ai-combined-degrees':continue
        for c in p['courses']:
            sub=c['code'].split()[0]
            if sub not in {'BIOL','CHEM','ECON','PSYC','PHYS','PHIL'}:continue
            observations+=1
            if c['code'] not in SUMMARIES:
                assert c['description'] is None
            assert c['source_id']==p['id']+'-'+sub.lower()+'-courses'
            assert c['credit_unit']=='semester_hours'
            assert any(s['id']==c['source_id'] and c['code'] in s['locator'] for s in p['sources'])
        assert p['curriculum_status']=='partial'
    assert observations>250


@pytest.mark.parametrize(('subject','heading','code','prose','note'),[
    ('ENVR','Earth and Environmental Sciences (ENVR)','ENVR 3300','Students who do not meet course prerequisites may seek permission of instructor.','permission is not guaranteed'),
    ('PSYC','Psychology (PSYC)','PSYC 3506','Students who do not meet course prerequisites may seek permission of instructor.','permission is not guaranteed'),
    ('PSYC','Psychology (PSYC)','PSYC 3510','Students who do not meet course prerequisites may seek permission of instructor.','permission is not guaranteed'),
    ('PHTH','Public Health (PHTH)','PHTH 5222','Requires permission of instructor for students outside designated programs.','does not enumerate those programs'),
    ('JRNL','Journalism (JRNL)','JRNL 5360','International students wishing to register need to speak to the International Student and Scholar Institute prior to registration.','before registering'),
    ('FINA','Finance and Insurance (FINA)','FINA 4460','Familiarity with a programming language such as Python is expected.','no specific prior programming course is named'),
    ('FINA','Finance and Insurance (FINA)','FINA 4412','This course is not designed to prepare students to take the Certified Financial Planner exam.','not designed as preparation'),
])
def test_scoped_registration_conditions_keep_eligibility_uncertainty(subject,heading,code,prose,note):
    html=page(f'<div class="courseblock"><p class="courseblocktitle">{code}. Sample course. (4 Hours)</p><p class="cb_desc">{prose}</p></div>',heading=heading)
    parser=register_subject_sources('test-program',{subject:[code]})[f'https://catalog.northeastern.edu/course-descriptions/{subject.lower()}/']
    observed=parser(html)
    assert any(note in n for n in observed['notes'])
    assert observed['courses'][0]['prerequisites'] is None
    changed=parser(html.replace(prose,'The description no longer states that condition.'))
    assert not any(note in n for n in changed['notes'])
    with pytest.raises(ValueError):parser(html.replace(heading,'A different subject'))


def test_first_year_science_audience_does_not_assign_home_college_or_required_course():
    html=page('<div class="courseblock"><p class="courseblocktitle">INSC 1000. Science at Northeastern. (1 Hour)</p><p class="cb_desc">Introduces first-year students with majors in the College of Science to the liberal arts in general.</p></div>',heading='Interdisciplinary Studies in Science (INSC)')
    parser=register_subject_sources('test-program',{'INSC':['INSC 1000']})['https://catalog.northeastern.edu/course-descriptions/insc/']
    observed=parser(html)
    assert observed['courses'][0]['description'] and observed['courses'][0]['credits']==1
    assert observed['requirements']==[]
    assert 'family' not in observed and 'hosting_unit' not in observed
    assert 'curriculum_audit' not in observed and 'last_verified' not in observed
    assert parser(html.replace('(1 Hour)','(2 Hours)'))['courses'][0]['credits']==2


def test_business_required_skills_and_recommended_experience_are_distinct():
    html=page('<div class="courseblock"><p class="courseblocktitle">MGMT 3305. Power and Influence. (4 Hours)</p><p class="cb_desc">Previous work experience (e.g., part-time job or co-op) is recommended but not required for enrollment in the course.</p></div>',heading='Management (MGMT)')
    parser=register_subject_sources('test-program',{'MGMT':['MGMT 3305']})['https://catalog.northeastern.edu/course-descriptions/mgmt/']
    observed=parser(html)
    assert observed['courses'][0]['prerequisites'] is None
    assert any('Previous work experience (e.g., part-time job or co-op)' in n and 'not a prerequisite' in n for n in observed['notes'])
    html=page('<div class="courseblock"><p class="courseblocktitle">FINA 4610. Finance course. (4 Hours)</p><p class="cb_desc">Requires a working knowledge of Excel or other spreadsheet programs.</p></div>',heading='Finance and Insurance (FINA)')
    parser=register_subject_sources('test-program',{'FINA':['FINA 4610']})['https://catalog.northeastern.edu/course-descriptions/fina/']
    assert 'Excel or other spreadsheet programs' in parser(html)['courses'][0]['prerequisites']
    assert parser(html.replace('Requires a working knowledge of','Recommends experience with'))['courses'][0]['prerequisites'] is None


def test_required_field_participation_does_not_create_prerequisite_or_universal_requirement():
    prose='Required participation in spring break international field project.'
    html=page(f'<div class="courseblock"><p class="courseblocktitle">ENTR 3217. Entrepreneurship course. (4 Hours)</p><p class="cb_desc">{prose}</p></div>',heading='Entrepreneurship and Innovation (ENTR)')
    parser=register_subject_sources('test-program',{'ENTR':['ENTR 3217']})['https://catalog.northeastern.edu/course-descriptions/entr/']
    observed=parser(html)
    assert observed['courses'][0]['prerequisites'] is None and observed['requirements']==[]
    assert any('spring-break international field project' in n for n in observed['notes'])
    assert not any('field project' in n for n in parser(html.replace(prose,''))['notes'])


def test_zero_hour_experiential_registration_keeps_standing_without_requiring_coop():
    html=page('<div class="courseblock"><p class="courseblocktitle">COOP 3945. Co-op Work Experience. (0 Hours)</p><p class="cb_desc">Provides students an opportunity for work experience. Requires sophomore standing or above.</p></div>',heading='Cooperative Education (COOP)')
    parser=register_subject_sources('test-program',{'COOP':['COOP 3945']})['https://catalog.northeastern.edu/course-descriptions/coop/']
    observed=parser(html);course=observed['courses'][0]
    assert course['credits']==0 and course['credit_unit']=='semester_hours'
    assert 'sophomore standing or above' in course['prerequisites']
    assert observed['requirements']==[] and 'family' not in observed
    changed=parser(html.replace('sophomore standing','junior standing'))['courses'][0]
    assert 'junior standing' in changed['prerequisites'] and 'sophomore' not in changed['prerequisites']


def test_all_ne_family_course_records_have_independent_subject_catalog_provenance():
    import json
    from pathlib import Path
    from atlas.scrape import adapters
    root=Path(__file__).resolve().parents[1];registered=adapters();variants=0;unknown=0;zeros=0
    for path in (root/'data/programs').glob('northeastern-*.json'):
        p=json.loads(path.read_text())
        if p.get('family',{}).get('id')!='northeastern-ai-combined-degrees':continue
        variants+=1;sources={s['id']:s for s in p['sources']}
        for c in p['courses']:
            subject=c['code'].split()[0].lower();sid=p['id']+'-'+subject+'-courses'
            assert c['source_id']==sid
            assert sources[sid]['url']==f'https://catalog.northeastern.edu/course-descriptions/{subject}/'
            assert c['code'] in sources[sid]['locator']
            assert sources[sid]['url'] in registered[p['id']].SOURCE_PARSERS
            assert c['credit_unit']=='semester_hours'
            if c['credits'] is None:
                assert any(n.startswith(c['code']+' subject catalog credit options:') for n in p['notes'])
            unknown+=c['description'] is None;zeros+=c['credits']==0
        assert p['curriculum_status']=='partial' and p['curriculum_audit']['unresolved_requirements']
    assert variants==23 and unknown>0 and zeros>0


def test_partner_practicum_summary_requires_current_prose_and_emits_no_program_outcome():
    html=page('<div class="courseblock"><p class="courseblocktitle">MKTG 4606. Research Practicum. (4 Hours)</p><p class="cb_desc">Includes active participation in client-centric challenges and applies data analytics, digital technology and machine learning.</p></div>',heading='Marketing (MKTG)')
    parser=register_subject_sources('test-program',{'MKTG':['MKTG 4606']})['https://catalog.northeastern.edu/course-descriptions/mktg/']
    result=parser(html)
    assert 'research practicum' in result['courses'][0]['description']
    assert result['requirements']==[] and 'outcomes' not in result and 'first_offered' not in result
    changed=parser(html.replace('active participation in client-centric challenges','different teaching format'))
    assert changed['courses'][0]['description'] is None


def test_design_topics_description_retains_offering_variability():
    html=page('<div class="courseblock"><p class="courseblocktitle">ARTG 3400. Topics In Interaction Design Inquiry. (4 Hours)</p><p class="cb_desc">Focuses on a specific interaction design topic. Topics vary each semester.</p></div>',heading='Art - Design (ARTG)')
    parser=register_subject_sources('test-program',{'ARTG':['ARTG 3400']})['https://catalog.northeastern.edu/course-descriptions/artg/']
    assert 'varies by offering' in parser(html)['courses'][0]['description']
    assert parser(html.replace('Topics vary each semester.','Fixed topic.'))['courses'][0]['description'] is None


def test_physics_lecture_lab_and_zero_hour_recitation_stay_distinct():
    html=page('<div class="courseblock"><p class="courseblocktitle">PHYS 1165. Physics 2. (4 Hours)</p><p class="cb_desc">Includes electrostatics; capacitors, magnetism and waves.</p></div><div class="courseblock"><p class="courseblocktitle">PHYS 1166. Lab for PHYS 1165. (1 Hour)</p><p class="cb_desc">Accompanies PHYS 1165. Includes experiments.</p></div><div class="courseblock"><p class="courseblocktitle">PHYS 1167. Recitation for PHYS 1165. (0 Hours)</p><p class="cb_desc">Offers interactive problem solving.</p></div>',heading='Physics (PHYS)')
    parser=register_subject_sources('test-program',{'PHYS':['PHYS 1165','PHYS 1166','PHYS 1167']})['https://catalog.northeastern.edu/course-descriptions/phys/']
    result=parser(html)
    assert [c['credits'] for c in result['courses']]==[4,1,0]
    assert len({c['description'] for c in result['courses']})==3
    assert result['requirements']==[]
    changed=parser(html.replace('interactive problem solving','a new teaching format'))
    assert changed['courses'][2]['description'] is None
    assert changed['courses'][0]['description']==result['courses'][0]['description']


def test_remaining_metadata_queue_matches_concrete_records_without_absence_claims():
    import json
    from pathlib import Path
    from collections import defaultdict
    root=Path(__file__).resolve().parents[1]
    queue=json.loads((root/'research/northeastern-metadata-remaining.json').read_text())
    remaining=defaultdict(list);courses=[]
    for path in sorted((root/'data/programs').glob('northeastern-*.json')):
        p=json.loads(path.read_text())
        if p.get('family',{}).get('id')!=queue['family_id']:continue
        courses.extend(p['courses'])
        for c in p['courses']:
            if c['description'] is None:remaining[c['code']].append(p['id'])
    assert {r['code']:r['program_ids'] for r in queue['unreviewed_descriptions']}==dict(remaining)
    assert queue['description_scope']['accessible_unreviewed_unique_codes']==len(remaining)
    assert queue['description_scope']['accessible_unreviewed_program_course_records']==sum(map(len,remaining.values()))
    assert queue['counts']['course_observations']==len(courses)
    for field in ['description','prerequisites','credits','public_site','syllabus']:
        assert queue['counts'][field]==sum(c[field] is not None for c in courses)


def test_graduate_only_project_is_not_imposed_on_undergraduate_degree():
    prose='Graduate students are required to complete a mandatory class project.'
    html=page(f'<div class="courseblock"><p class="courseblocktitle">CIVE 5363. Climate course. (4 Hours)</p><p class="cb_desc">Includes policy issues and risk-informed trade-offs. {prose}</p></div>',heading='Civil and Environmental Engineering (CIVE)')
    args=dict(program_id='test-program',subject='CIVE',heading='Civil and Environmental Engineering (CIVE)',codes=['CIVE 5363'],url='https://catalog.northeastern.edu/course-descriptions/cive/')
    result=parse_subject(html,**args)
    assert result['courses'][0]['prerequisites'] is None and result['requirements']==[]
    assert any('not imposed on this undergraduate degree' in n for n in result['notes'])
    assert not any('mandatory class-project' in n for n in parse_subject(html.replace(prose,''),**args)['notes'])


def test_experiential_summary_requires_title_evidence_for_half_time_abroad_scope():
    html=page('<div class="courseblock"><p class="courseblocktitle">COOP 3947. Co-op Work Experience Abroad--Half Time. (0 Hours)</p><p class="cb_desc">Provides students with an opportunity for work experience abroad.</p></div>',heading='Cooperative Education (COOP)')
    parser=register_subject_sources('test-program',{'COOP':['COOP 3947']})['https://catalog.northeastern.edu/course-descriptions/coop/']
    assert 'half-time' in parser(html)['courses'][0]['description']
    assert parser(html.replace('Abroad--Half Time.','Abroad.'))['courses'][0]['description'] is None


def test_business_intb_credit_conflict_retains_both_sources_and_original_alternative():
    import json
    from pathlib import Path
    path=next((Path(__file__).resolve().parents[1]/'data/programs').glob('northeastern-*-business-administration-*.json'))
    p=json.loads(path.read_text());c=next(c for c in p['courses'] if c['code']=='INTB 1209')
    assert 'excluded for business majors' in c['description']
    assert any(c['id'] in r['course_ids'] and r['parent_id'].endswith('intb-1203-alternatives') for r in p['requirements'])
    assert any('INTB 1209 applicability conflict' in n for n in p['curriculum_audit']['unresolved_requirements'])
    assert p['id']+'-intb-courses' in p['curriculum_audit']['source_ids']
    assert p['id']+'-concentration-international-business-catalog' in p['curriculum_audit']['source_ids']
    assert p['curriculum_status']=='partial'


def test_epidemiology_computation_scope_requires_current_course_evidence():
    html=page('<div class="courseblock"><p class="courseblocktitle">PHTH 4202. Principles of Epidemiology. (4 Hours)</p><p class="cb_desc">Studies research design, bias and causal inference; there are no computational requirements.</p></div>',heading='Public Health (PHTH)')
    parser=register_subject_sources('test-program',{'PHTH':['PHTH 4202']})['https://catalog.northeastern.edu/course-descriptions/phth/']
    observed=parser(html)
    assert 'no computation is required' in observed['courses'][0]['description']
    assert observed['courses'][0]['prerequisites'] is None
    assert observed['requirements']==[] and 'outcomes' not in observed
    assert parser(html.replace('there are no computational requirements','computational exercises are required'))['courses'][0]['description'] is None


def test_model_nato_summary_does_not_turn_selective_conference_into_entitlement():
    html=page('<div class="courseblock"><p class="courseblocktitle">POLS 4918. Model NATO. (4 Hours)</p><p class="cb_desc">Teams research countries and conduct a simulation. Students may be selected to represent the university at a national conference.</p></div>',heading='Political Science (POLS)')
    parser=register_subject_sources('test-program',{'POLS':['POLS 4918']})['https://catalog.northeastern.edu/course-descriptions/pols/']
    result=parser(html)
    assert 'conference is selective' in result['courses'][0]['description']
    assert result['requirements']==[] and 'outcomes' not in result
    assert parser(html.replace('Students may be selected','All students are required'))['courses'][0]['description'] is None


def test_same_title_africa_courses_keep_different_published_periods():
    summaries=[]
    for subject,heading,prose in [('HIST','History (HIST)','Examines Africa from 1000 C.E. to the mid-19th century.'),('AFCS','Africana Studies (AFCS)','Examines patterns of trade up to 1000 C.E.')]:
        html=page(f'<div class="courseblock"><p class="courseblocktitle">{subject} 2390. Africa and the World in Early Times. (4 Hours)</p><p class="cb_desc">{prose}</p></div>',heading=heading)
        parser=register_subject_sources('test-program',{subject:[subject+' 2390']})[f'https://catalog.northeastern.edu/course-descriptions/{subject.lower()}/']
        summaries.append(parser(html)['courses'][0]['description'])
    assert 'mid-nineteenth' in summaries[0] and 'up to 1000' in summaries[1]
    assert summaries[0]!=summaries[1]
