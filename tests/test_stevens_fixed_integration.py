import json
from pathlib import Path
from atlas.curriculum_profile import requirement_profile


def test_all_fixed_subjects_and_eligibility_missingness_remain_honest():
    p = json.loads(Path('data/programs/stevens-institute-of-technology-artificial-intelligence-bs-degree.json').read_text())
    profile = requirement_profile(p)
    assert profile['required']['count'] == 24
    assert profile['required']['classification'] == dict(reviewed=19,mixed=4,unclassified=1,unreviewed=0)
    assert profile['required']['categories'] == dict(foundations=6,mathematics=6,ai_ml=3,
        systems=1,human_context=2,applications=1,electives=0,other=5)
    courses = {c['code']:c for c in p['courses']}
    assert courses['CS 423']['category'] == courses['CS 424']['category'] == 'foundations'
    assert 'CS 423' in courses['CS 424']['prerequisites']
    assert courses['CS 101']['prerequisites'] is None
    assert courses['CS 101']['category_review']['status'] == 'unclassified'
    assert courses['PRV 101']['category_review']['status'] == 'mixed'
    assert 'Published eligibility:' in courses['CS 583']['prerequisites']
    assert 'probability' in courses['CS 583']['prerequisites']
    assert all(courses[code]['credit_unit']=='unknown' for code in ['CS 423','CS 424','CS 583'])
    assert p['curriculum_status'] == 'partial'
