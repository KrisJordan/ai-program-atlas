import importlib,json
from pathlib import Path
import pytest
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program
m=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.core_subjects')


def test_versioned_subject_evidence_and_changed_meaning():
 c=dict(code='6.1010',name='Fundamentals of Programming',category='other')
 first=m.classify_annotation(c,'Fundamental concepts of programming; software design.')
 assert c['category']=='foundations'
 second=m.classify_annotation(c,'Changed subject with no reviewed topical evidence.')
 assert c['category']=='other'and second!=first and 'category_review'not in c


def test_exact_fixed_versioned_identities_are_not_merged_with_catalog():
 p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text());validate_program(p)
 assert requirement_profile(p)['required']['count']==2
 assert requirement_profile(p)['required']['categories']['foundations']==2
 reviewed=[c for c in p['courses']if c.get('category_review')]
 assert {'mit-ai-v2025-6-1010','mit-ai-v2025-6-1210'}<={c['id']for c in reviewed}
 assert all(c['id'].startswith('mit-ai-v2025-')for c in reviewed)
 assert all(c['source_id']=='mit-ai-decision-making-bs-versioned'for c in reviewed)
 duplicates=[c for c in p['courses']if c['code']=='6.1210'and not c['id'].startswith('mit-ai-v2025-')]
 assert duplicates and all('category_review'not in c for c in duplicates)
 assert all(c['credits']is None for c in reviewed)


def test_optional_versioned_source_replay_observes_no_review_metadata():
 path=Path('/tmp/pilot-audit-mit-version.html')
 if not path.exists():pytest.skip('Optional ignored source cache absent')
 v=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.versioned')
 p=v.parse(path.read_text())
 assert {'mit-ai-v2025-6-1010','mit-ai-v2025-6-1210'}<=set(p['observed_core_description_digests'])
 assert all('category_review'not in c for c in p['courses'])
