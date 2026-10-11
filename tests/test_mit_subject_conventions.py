import importlib
import json
from pathlib import Path
import pytest

m=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.subject_conventions')


@pytest.mark.parametrize('text,total', [('Units: 3-0-9 Content',12),('Units: 0-0-0 Content',0),('Units: 4-0-11 Content',15),('Units: arranged',None),('Units: 3-0-9-12',None),('Units: 3-0',None)])
def test_only_complete_numeric_unit_triplets(text,total):
    assert m.credits(text)==total


def test_convention_source_guards_and_no_certification():
    h='<h1>Subjects</h1><h2>How to Read Subject Descriptions</h2><p>The total unit credit for a subject is obtained by adding together all the units shown. Students who have not completed the stated prerequisites must obtain the instructor’s permission. Subjects that meet together have different coursework requirements. Credit cannot also be received for.</p>'
    d=m.parse(h)
    assert len(d['requirements'])==2 and not d['courses']
    assert not {'curriculum_audit','category_review','last_verified'}&d.keys()
    with pytest.raises(ValueError):m.parse(h.replace('adding together','multiplying'))


def test_reciprocal_crosslists_keep_versions_and_different_level_courses_separate():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    from atlas.db import validate_program
    validate_program(p)
    groups={g['id']:g for g in p['course_identity_groups']}
    assert set(groups['mit-ai-versioned-crosslist-c20']['course_ids'])=={'mit-ai-v2025-16-c20','mit-ai-v2025-18-c20','mit-ai-v2025-9-c20'}
    assert set(groups['mit-ai-versioned-crosslist-c06']['course_ids'])=={'mit-ai-v2025-18-c06','mit-ai-v2025-6-c06'}
    grouped={i for g in groups.values()for i in g['course_ids']}
    assert not {'mit-ai-18-c06-j','mit-ai-v2025-6-5400','mit-ai-v2025-18-404','mit-ai-v2025-cc-1803','mit-ai-v2025-es-1803'}&grouped
