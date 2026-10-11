import json
from pathlib import Path
import pytest
from atlas.adapters.cmu_bs import reviewed_quantitative as m
from atlas.adapters.cmu_bs.core_enrichment import MATH


def test_department_membership_does_not_override_mixed_course_content():
    p=json.loads(Path('data/programs/cmu-bs-ai.json').read_text());by={c['code']:c for c in p['courses']}
    for code in ['21-150','36-303']:
        assert by[code]['category']=='other'and by[code]['category_review']['status']=='mixed'
        assert by[code]['category_review']['candidate_categories']==['mathematics','human_context']
    assert by['21-241']['prerequisites']is None  # Recommended proof preparation is not formal.
    assert 'Min. grade B'in by['36-401']['prerequisites']
    assert 'Min. grade C'in by['36-236']['prerequisites']
    assert set(m.SUBJECTS)<={c['code']for c in p['courses']if c.get('category_review')}


def test_new_directory_prose_is_observed_without_replaying_math_reviews():
    heading,_,codes=m.DIRECTORIES[MATH]
    html=f'<h1>{heading}</h1><p>2026-2027 Catalog</p>'
    for code in codes:
        html+=f'<dl class="courseblock"><dt>{code} {m.SUBJECTS[code]["name"]}</dt><dd>Spring: 7 units<br>Changed course content.<br>Prerequisite: 21-090</dd></dl>'
    d=m.parse(html,MATH)
    assert len(d['courses'])==11
    assert all(c['category']=='other' and c['credits']==7 and c['prerequisites']=='21-090'for c in d['courses'])
    assert not any('category_review'in c for c in d['courses'])
    with pytest.raises(ValueError,match='inventory changed'):m.parse(html.replace('21-150','21-151'),MATH)
