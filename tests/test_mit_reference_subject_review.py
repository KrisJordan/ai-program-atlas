import importlib
import json
from pathlib import Path

m=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.reference_subjects')


def test_exact_reference_identity_and_title_required():
    c=dict(id='mit-ai-6-1210',name='Introduction to Algorithms',category='other')
    m.observe([c]);assert c['category']=='foundations'and'category_review'not in c
    c['name']='Introduction to something else';m.observe([c]);assert c['category']=='other'
    other=dict(id='different-source-6-1210',name='Introduction to Algorithms',category='other')
    m.observe([other]);assert other['category']=='other'


def test_ambiguous_titles_stay_unclassified_and_versions_stay_distinct():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text());by={c['id']:c for c in p['courses']}
    assert by['mit-ai-6-3260-j']['category']=='other'
    assert by['mit-ai-v2025-6-3260']['category']=='mathematics'
    assert by['mit-ai-6-5931']['category']=='systems'
    assert 'Limited official-title review only.'in by['mit-ai-6-5931']['category_review']['rationale']
    assert by['mit-ai-6-5931']['description']is None
    assert len(m.REVIEWS)==63 and sum(r['category']!='other'for r in m.REVIEWS.values())==39
