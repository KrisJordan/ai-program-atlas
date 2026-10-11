from importlib import import_module
from pathlib import Path
import pytest
m=import_module('atlas.adapters.mit-ai-decision-making-bs.hass_cmsw')


def education():
    return '''<h1>Education and Teacher Licensure</h1><h2>Concentration</h2>
    <p>25 hours per semester</p><h4>The Concentration Consists of 3 Subjects</h4>
    <p>CMS.586J Synthetic Introduction One</p><p>and/or</p><p>CMS.587J Synthetic Introduction Two</p>
    <p>one or two of these subjects</p><table>
    <tr><td>CMS.524/STS.024 Synthetic Cross-list</td></tr>
    <tr><td>CMS.S61 Synthetic Topic (Fall 2023)</td></tr>
    <tr><td>CMS.S61 Synthetic Topic (Spring 2024)</td></tr></table>
    <h2>Minor</h2><table><tr><td>EDUC 325 Separate Minor Only</td></tr></table>'''


def test_education_alternative_bundles_and_term_identity():
    d=m.parse_education(education())
    choices=[r for r in d['requirements'] if r['kind']=='choose_courses']
    assert [r['count'] for r in choices]==[1,2,2,1]
    assert choices[0]['course_ids']==choices[2]['course_ids']
    assert choices[1]['course_ids']==choices[3]['course_ids']
    topics=[c for c in d['courses'] if c['code']=='CMS.S61']
    assert len(topics)==2 and topics[0]['id']!=topics[1]['id']
    assert all(c['credits'] is None for c in d['courses'])
    assert not any(c['code']=='EDUC 325' for c in d['courses'])
    with pytest.raises(ValueError):m.parse_education(education().replace('and/or','and'))
    with pytest.raises(ValueError):m.parse_education(education().replace('CMS.587J','CMS.589J'))


def pool():
    return '''<h1>CMS Subjects: Full List and Pre-approved Electives</h1>
    <h2>Full Subject List</h2><h3>Course CMS: Comparative Media Studies</h3>
    <table><tr><th>Subject Number (Undergraduate)</th><th>Subject Number (Graduate)</th><th>Subject Name</th><th></th><th>HASS, CI-H/M</th></tr>
    <tr><td>CMS.301</td><td>CMS.801</td><td>Synthetic HASS</td><td></td><td>HASS-A</td></tr>
    <tr><td>CMS.603</td><td>CMS.995</td><td>Synthetic Unspecified</td><td></td><td></td></tr></table>
    <h2>Pre-approved Electives in Other Departments</h2><p>A sampling of classes that CMS majors used; this list is not exhaustive. With permission from their CMS Major advisor.</p>
    <table><tr><th>Subject Number (Undergraduate)</th><th>Subject Number (Graduate)</th><th>Subject Name</th><th>HASS, CI-H/M</th></tr>
    <tr><td>4.999</td><td>4.888</td><td>Synthetic External</td><td>HASS-A</td></tr></table>'''


def test_pool_retains_hass_unknown_and_major_only_reference_boundaries():
    d=m.parse_pool(pool())
    assert [c['code'] for c in d['courses']]==['CMS.301','CMS.603','4.999']
    assert [len(r['course_ids']) for r in d['requirements']]==[1,1,1]
    assert all(r['kind']=='note' and r['count'] is None for r in d['requirements'])
    with pytest.raises(ValueError):m.parse_pool(pool().replace('Subject Number (Graduate)','Subject Number (Other)'))
    with pytest.raises(ValueError):m.parse_pool(pool().replace('CMS Major advisor','Concentration advisor'))


def test_els_three_subject_rule_does_not_import_graduate_eet():
    html='''<h1>English Language Studies</h1><p>open only to matriculated MIT students; advanced writing classes are open to native-English-speaking students as well</p><h3>English Evaluation Test</h3><p>All incoming international graduate students</p><h3>Concentration in ELS (undergraduates)</h3><p>Any three subjects in English Language Studies or related fields. Concentration Advisor for ELS.</p>'''
    d=m.parse_els(html)
    assert [r['count'] for r in d['requirements'] if r['kind']=='choose_courses']==[3]
    assert 'courses' not in d
    assert 'not an undergraduate concentration requirement' in d['requirements'][-1]['summary']
    with pytest.raises(ValueError):m.parse_els(html.replace('three subjects','four subjects'))


@pytest.mark.parametrize('key',m.URLS)
def test_optional_browser_dom_projection_replay(key):
    path=Path('/tmp/atlas-mit-cmsw-browser-projection-'+key+'.html')
    if not path.exists():pytest.skip('Optional normalized browser DOM observation, not raw HTTP')
    d=m.SOURCE_PARSERS[m.URLS[key]](path.read_text())
    assert d['requirements']
    assert not {'last_verified','curriculum_audit','curriculum_status'} & d.keys()


def test_cms_uses_concentration_section_not_major_course_counts():
    html='<h1>Undergraduate Studies: Comparative Media Studies</h1><h2>Major</h2><p>Six electives</p><h2>Concentration</h2><p>four classes from the complete list of <a href="'+m.URLS['pool']+'">options</a> that carry a HASS designation. Education subjects without a media studies component count for Education but not the CMS concentration; make an appointment.</p><h3>Computing and Society</h3><p>A different field</p>'
    d=m.parse_cms(html)
    assert len(d['requirements'])==2
    assert d['requirements'][1]['count']==4
    assert d['requirements'][1]['course_ids']==[]
    with pytest.raises(ValueError):m.parse_cms(html.replace(m.URLS['pool'],'https://example.invalid/unreviewed'))


def test_writing_major_minor_tables_do_not_become_concentration_pools():
    html='''<h1>Writing Majors, Minor, Concentration</h1><h2>Minor in Writing</h2><table><tr><td>21W.999 Synthetic Minor Course</td></tr></table><h2>Concentration in Writing</h2><p>four subjects chosen in consultation with the Concentration Advisor; one may be a CI-HW. Completing the minor makes it not necessary to complete a separate Concentration; Concentration Proposal and Completion forms remain. Only five subjects in the Minor may apply to HASS. All concentration subjects must carry a HASS designation.</p>'''
    d=m.parse_writing(html)
    assert 'courses' not in d
    assert [r['count'] for r in d['requirements'] if r['kind']=='choose_courses']==[4]
    with pytest.raises(ValueError):m.parse_writing(html.replace('one may be a CI-HW','two may be CI-HW'))
