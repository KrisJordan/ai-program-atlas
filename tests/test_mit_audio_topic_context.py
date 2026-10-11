import importlib,json
from pathlib import Path
import pytest
m=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.audio_topic_context')


def test_missing_identity_cannot_activate_topic_context():
    with pytest.raises(ValueError):m.parse('<h1>Different topic</h1>')


def test_actual_topic_is_not_generic_course_metadata_or_identity_merge():
    path=Path('/tmp/mit-common-ground-0.html')
    if not path.exists():pytest.skip('Optional official C22 source capture absent')
    html=path.read_text();out=m.parse(html)
    assert out['courses']==[] and len(out['requirements'])==1
    assert out['requirements'][0]['kind']=='note'
    fields=m.observe(html)[0]['fields']
    assert fields['Term(s):']=='Fall' and fields['Units:']=='12'
    assert fields['Prerequisite:']=='Permission of instructor'
    assert fields['Level:']=='Undergraduate and Graduate'
    changed=html.replace('machine learning audio','unreviewed new content')
    assert changed!=html and m.parse(changed)['requirements']==[]
    with pytest.raises(ValueError):m.parse(html.replace('21M.389, 21M.589','21M.389'))
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    c=next(c for c in p['courses']if c['id']=='mit-ai-v2025-21m-589')
    assert c['name']is None and c['credits']is None and c['prerequisites']is None
    assert c['category']=='other'and c['category_review']['status']=='unclassified'
    assert not any(c['id']in g['course_ids']for g in p['course_identity_groups'])
