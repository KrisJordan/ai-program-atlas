import importlib,json
from pathlib import Path
import pytest
m=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.archived_vision')


def fixture():
    return '''<h1>6.8300/6.8301: Advances in Computer Vision</h1><h3>Spring 2024</h3>
    <h2>Course Overview</h2><p>Machine learning methods for vision.</p>
    <p>Units are 3-0-9 for 6.8300 (Graduate Level) and 4-0-11 for 6.8301 (Undergraduate Level, CI-M Subject).
    The prerequisites of this course are (6.1200 or 6.3700) and (18.06 or 18.C06). Good luck.</p>'''


def test_undergraduate_units_are_not_graduate_units_and_unreviewed_body_withheld():
    o=m.observe(fixture())
    assert o['credits']==15
    assert o['prerequisites']=='(6.1200 or 6.3700) and (18.06 or 18.C06)'
    assert m.parse(fixture())['courses']==[]


@pytest.mark.parametrize('before,after',[('Spring 2024','Spring 2026'),('6.8300/6.8301:','6.8300:'),('Undergraduate Level, CI-M Subject','Graduate Level'),('Course Overview','Other')])
def test_identity_term_and_undergraduate_fields_required(before,after):
    with pytest.raises(ValueError):m.observe(fixture().replace(before,after))


def test_actual_historical_evidence_and_changed_body_guard():
    path=Path('/tmp/mit-reference-followup-1.html')
    if not path.exists():pytest.skip('Optional ignored official linked course capture absent')
    html=path.read_text();out=m.parse(html)
    assert len(out['courses'])==1 and out['requirements']==[]
    c=out['courses'][0]
    assert c['credits']==15 and c['category']=='ai_ml'and 'category_review'not in c
    changed=html.replace('convolutional neural networks','unreviewed new subject content')
    assert changed!=html and m.parse(changed)['courses']==[]
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    seed=next(c for c in p['courses']if c['id']=='mit-ai-6-8301')
    assert seed['source_id']!=m.SID and m.SID in seed['category_review']['source_ids']
    assert seed['description']==c['description'] and seed['prerequisites']==c['prerequisites']
    assert not any(seed['id']in group['course_ids']for group in p['course_identity_groups'])
