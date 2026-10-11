import pytest
from atlas.adapters.rit_current_curriculum_guidance import parse

def fixture():return '<main><h1>Curriculum Requirements for Current Students</h1><p>View your Academic Advising Report. Use the academic year that you matriculated into your current program or the academic year that you have been advised to follow.</p><a href="https://academiccatalog.rit.edu/">Current catalog</a></main>'

def test_guidance_observes_applicability_without_inventing_student_cohort():
    o=parse(fixture());assert 'advised to follow' in o['observed_curriculum_guidance']
    assert o['observed_curriculum_links'][0]['url']=='https://academiccatalog.rit.edu/'
    assert all(k not in o for k in ['courses','requirements','curriculum_audit','catalog_year','last_verified'])

@pytest.mark.parametrize('before,after',[('Current Students','Graduate Students'),('academic year that you matriculated','different year that you matriculated'),('https://academiccatalog.rit.edu/','https://example.com/')])
def test_guidance_rejects_wrong_scope_or_destination(before,after):
    with pytest.raises(ValueError):parse(fixture().replace(before,after))
