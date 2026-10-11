import importlib,json
from pathlib import Path
import pytest
m=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.strobe_review')


def test_instructor_link_identity_is_required():
    for html in ['<main>Someone else</main>', '<main>James W. Bales<p>6.9030</p></main>', f'<main>James W. Bales<p><a href="{m.COURSE_URL}">Different course</a></p></main>']:
        with pytest.raises(ValueError):m.observe(html)


def test_actual_bounded_content_never_supplies_missing_credits_or_prerequisites():
    path=Path('/tmp/mit-strobe-instructor-0.html')
    if not path.exists():pytest.skip('Optional official instructor capture absent')
    html=path.read_text();result=m.parse(html);assert len(result['courses'])==1
    c=result['courses'][0]
    assert c['category']=='applications'and c['credits']is None and c['prerequisites']is None
    assert 'category_review'not in c and result['requirements']==[]
    changed=html.replace('the photography course','the changed-content course')
    assert changed!=html and m.parse(changed)['courses']==[]
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    reference=next(c for c in p['courses']if c['id']=='mit-ai-6-9030')
    versioned=next(c for c in p['courses']if c['id']=='mit-ai-v2025-6-9030')
    assert reference['credits']==12 and reference['source_id']!=m.SID
    assert reference['category']=='applications'and reference['prerequisites']is None
    assert versioned['name']is None and versioned['category']=='other'
