import importlib
import json
from pathlib import Path
import pytest

m=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.gir_subjects')


def test_chemistry_panel_extracts_actual_fields_and_rejects_missing_subject():
    h='<h1>Classes</h1>'
    for code in ['5.111','5.112']:
        h+=f'<h3 aria-controls="p{code}">{code} Principles of Chemical Science</h3><div id="p{code}">Term: Fall / Units: 5-0-7 / Prereq: None Introduction to chemistry.</div>'
    d=m.parse(h,m.CHEMISTRY)
    assert [c['credits']for c in d['courses']]==[12,12]
    assert all(c['prerequisites']=='None'and c['category']=='other'for c in d['courses'])
    assert all('category_review'not in c for c in d['courses'])
    with pytest.raises(ValueError):m.parse(h.replace('5.112 Principles','5.113 Principles'),m.CHEMISTRY)


def test_gir_science_domain_and_math_have_distinct_conditional_evidence():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    from atlas.db import validate_program
    validate_program(p)
    by={c['code']:c for c in p['courses']if c['id'].startswith('mit-ai-gir-')}
    assert by['18.01']['category']=='mathematics'and by['18.01']['credits']==12
    assert by['5.112']['category']=='applications'and by['5.112']['prerequisites']=='None'
    assert any('AP score'in n for n in by['5.112']['notes'])
    assert by['7.015']['name']is None and by['7.015']['category']=='applications'
    assert any('70'in n and'60'in n for n in by['7.015']['notes'])
    assert any('three general-elective'in n for n in by['18.01A']['notes'])
    # Separate public Fall2026 course evidence now supplies this earlier gap.
    assert by['18.01L']['category']=='mathematics'
    assert by['18.01L']['syllabus'].endswith('/courses/39048/assignments/syllabus')


def test_actual_cached_gir_sources_replay_without_new_review():
    paths={m.CALCULUS:'/tmp/mit-gir-review-0.html',m.BIOLOGY:'/tmp/mit-gir-followup-0.html',m.CHEMISTRY:'/tmp/mit-gir-final-1.html',m.SOLID:'/tmp/mit-gir-review-1.html'}
    if not all(Path(p).exists()for p in paths.values()):pytest.skip('Optional ignored source caches absent')
    observed=[c for u,p in paths.items()for c in m.parse(Path(p).read_text(),u)['courses']]
    assert len(observed)==12
    assert all(c['category']in {'mathematics','applications'}and'category_review'not in c for c in observed)
