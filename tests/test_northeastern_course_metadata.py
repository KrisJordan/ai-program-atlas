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
