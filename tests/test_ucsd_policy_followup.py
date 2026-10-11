import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_degree_policies as p
from atlas.db import validate_program


def tag_fixture():
    return '''<p class="course-name">CSE 101. Synthetic algorithm course (4) Tag: Theory/Abstraction</p><p class="course-name">CSE 120. Synthetic systems course (4) Tags: Systems, Applications of Computing</p><p class="course-name">CSE 999. Untagged example (4)</p>'''


def test_tags_multi_category_changed_code_and_no_unmarked_inference():
    r=p.parse_tags(tag_fixture());assert len(r['courses'])==2
    pools={n['title']:n['course_ids']for n in r['requirements']}
    assert pools['Systems CSE course tags']==pools['Applications of Computing CSE course tags']
    changed=p.parse_tags(tag_fixture().replace('CSE 120','CSE 121').replace('course (4) Tags','course (2) Tags'))
    assert next(c for c in changed['courses']if c['code']=='CSE 121')['credits']==2
    assert 'curriculum_audit' not in r
    with pytest.raises(ValueError):p.parse_tags(tag_fixture().replace('Theory/Abstraction','Unexpected'))


def test_college_observation_is_conditional_and_guarded():
    name,guards,_=p.COLLEGES['eighth-college']
    html='<h1>'+name+'</h1><p>'+'; '.join(guards)+'</p>'
    r=p.parse_college(html,'eighth-college')
    assert 'only if enrolled here' in r['requirements'][0]['title']
    assert r['requirements'][0]['kind']=='note'
    with pytest.raises(ValueError):p.parse_college(html.replace('FA24 admits or later','changed'),'eighth-college')


def test_reviewed_seed_preserves_conflicts_and_unknown_pools():
    d=json.loads(Path('data/programs/'+p.PID+'.json').read_text());validate_program(d)
    assert d['curriculum_status']=='partial'
    assert len([n for n in d['requirements']if '-policy-college-' in n['id']])==8
    assert len([n for n in d['requirements']if '-tag-pool-' in n['id']])==3
    assert any('36/44' in s for s in d['curriculum_audit']['unresolved_requirements'])
    assert any('CSE 154' in s for s in d['notes'])
    # A known source difference is not silently deleted from the catalog option pool.
    assert 'ucsd-cse-154' in next(n for n in d['requirements']if n['id']==p.PID+'-ai-electives')['course_ids']
