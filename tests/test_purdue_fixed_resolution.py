"""Malformed observations must not change reviewed membership or approval semantics."""
import json
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from atlas.curriculum_profile import requirement_profile
from atlas.degree_audit import core_review_fingerprint, validate_core_review
from test_purdue_minor import adapter, bs_fixture


@pytest.mark.parametrize('mutation, message', [
    ('duplicate_core', 'Duplicate Purdue core'),
    ('missing_or', 'explicit OR'),
    ('duplicate_selective', 'Duplicate Purdue selective'),
    ('missing_nlp', 'both courses'),
    ('missing_capstone', 'all four'),
    ('duplicate_capstone', 'Duplicate Purdue capstone'),
    ('missing_approval', 'approval condition'),
    ('changed_capstone', 'named capstone identity'),
])
def test_bs_rejects_malformed_identity_or_choice_branch(mutation, message):
    soup=BeautifulSoup(bs_fixture(),'html.parser')
    if mutation == 'duplicate_core':
        soup.table.append(BeautifulSoup(str(soup.table.find_all('tr')[1]),'html.parser'))
    elif mutation == 'missing_or':
        cell=soup.table.find_all('tr')[2].find_all('td')[0]
        cell.clear()
        cell.append(BeautifulSoup('<a>MA 26100</a> and <a>MA 27101</a>','html.parser'))
    else:
        lists=soup.find_all('ul')
        if mutation == 'duplicate_selective':
            lists[0].append(BeautifulSoup(str(lists[0].li),'html.parser'))
        elif mutation == 'missing_nlp':
            lists[0].find_all('li')[2].decompose()
        elif mutation == 'missing_capstone':
            lists[-1].find_all('li')[-1].decompose()
        elif mutation == 'duplicate_capstone':
            lists[-1].find_all('li')[-1].replace_with(BeautifulSoup(str(lists[-1].find_all('li')[1]),'html.parser'))
        elif mutation == 'missing_approval':
            lists[-1].find_all('li')[-1].string='AI Forge project Credits: 3.00'
        elif mutation == 'changed_capstone':
            lists[-1].li.a.string='CS 49000'
    with pytest.raises(ValueError, match=message):adapter('purdue-ai-bs').parse(str(soup))


def ba_fixture():
    codes=['10100','17600','18000','18200','24300']
    return '<h1>Artificial Intelligence</h1><h2>Plan of Study</h2><p>The BA in AI degree requires 24 credit hours in philosophy, with an additional 15 credit hours in CS.</p><ul>'+''.join(f'<li>CS {c}: Synthetic course</li>'for c in codes)+'</ul>'


@pytest.mark.parametrize('mutation', ['remove', 'duplicate', 'replace'])
def test_ba_rejects_changed_five_course_identity_set(mutation):
    html=ba_fixture()
    if mutation=='remove':html=html.replace('<li>CS 17600: Synthetic course</li>','')
    elif mutation=='duplicate':html=html.replace('CS 17600','CS 18000')
    else:html=html.replace('CS 17600','CS 17700')
    with pytest.raises(ValueError,match='five-course'):adapter('purdue-ai-ba').parse_department(html)


def test_replacement_rows_pin_exact_manual_major_sets_and_preserve_partial_limits():
    proposal=json.loads(Path('research/degree-audit/independent-resolution-purdue.json').read_text())
    for row in proposal['programs']:
        program=json.loads(Path('data/programs',row['program_id']+'.json').read_text())
        validate_core_review(row,program['id'])
        assert core_review_fingerprint(program)==row['reviewed_content_hash']
        actual=requirement_profile(program,include_course_ids=True)
        assert set(actual['course_ids']['required'])==set(row['expected_course_ids']['required'])
        assert actual['required']['count']==row['expected_profile']['required']['count']
        for category,count in row['expected_profile']['required']['categories'].items():
            assert actual['required']['categories'][category]==count
        assert row['full_degree_verified'] is False
        assert row['dimensions']['classification']['status']=='partial'
        if program['id']=='purdue-ai-bs':
            assert row['dimensions']['fixed_requirements']['status']=='verified'
            assert row['expected_profile']['options'] is None
            assert row['expected_course_ids']['unresolved'] is None
            assert len(row['reviewed_option_subset'])==33
            assert set(row['reviewed_option_subset'])<=set(actual['course_ids']['options'])
        else:
            assert row['dimensions']['fixed_requirements']['status']=='partial'
            assert all(c['credits'] is None for c in program['courses'])
