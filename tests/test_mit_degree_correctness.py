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
 assert requirement_profile(p)['required']['count']==3
 assert requirement_profile(p)['required']['categories']['foundations']==2
 assert requirement_profile(p)['required']['categories']['mathematics']==1
 reviewed=[c for c in p['courses']if c.get('category_review')]
 assert {'mit-ai-v2025-6-1010','mit-ai-v2025-6-1210'}<={c['id']for c in reviewed}
 assert all(c['source_id']=='mit-ai-decision-making-bs-versioned'for c in reviewed if c['id'].startswith('mit-ai-v2025-'))
 duplicates=[c for c in p['courses']if c['code']=='6.1210'and not c['id'].startswith('mit-ai-v2025-')]
 assert duplicates and all('Limited official-title review only.'in c['category_review']['rationale']for c in duplicates)
 assert all(c['credits']is None for c in reviewed if c['name']is None and c['id'].startswith('mit-ai-v2025-'))
 assert next(c for c in reviewed if c['code']=='6.1010')['credits']==12


def test_optional_versioned_source_replay_observes_no_review_metadata():
 path=Path('/tmp/pilot-audit-mit-version.html')
 if not path.exists():pytest.skip('Optional ignored source cache absent')
 v=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.versioned')
 p=v.parse(path.read_text())
 assert {'mit-ai-v2025-6-1010','mit-ai-v2025-6-1210'}<=set(p['observed_core_description_digests'])
 assert all('category_review'not in c for c in p['courses'])


def test_independent_versioned_role_sets_include_required_discrete_math():
 p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
 ledger=json.loads(Path('research/degree-audit/mit.json').read_text())['programs'][0]
 expected=ledger['expected_versioned_course_ids']
 assert set(expected['required'])=={'mit-ai-v2025-6-1200','mit-ai-v2025-6-1010','mit-ai-v2025-6-1210'}
 ids={c['id']for c in p['courses']if c['id'].startswith('mit-ai-v2025-')}
 partial=dict(courses=[c for c in p['courses']if c['id']in ids],requirements=[r for r in p['requirements']if r['source_id']=='mit-ai-decision-making-bs-versioned'],course_identity_groups=p['course_identity_groups'])
 profile=requirement_profile(partial)
 assert profile['required']['count']==3 and profile['options']['count']==255 and profile['unresolved']['count']==0
 assert set(expected['required']).isdisjoint(expected['options'])
 assert len(expected['options'])==255
