import hashlib
import json
from pathlib import Path
import pytest
from atlas.adapters.cmu_bs import reviewed_scs as m
from atlas.adapters.cmu_bs.course_metadata import parse_metadata, COURSE_SOURCE
from atlas.db import validate_program


def fixture(body='Probability theory and applications.', prerequisite='21-120'):
    return f'<h1>School of Computer Science Courses</h1><p>2026-2027 Catalog</p><dl class="courseblock"><dt>15-259 Probability and Computing</dt><dd>Spring: 12 units<br>{body}<br>Prerequisite: {prerequisite}</dd></dl>'


def test_changed_description_does_not_replay_reviewed_subject(monkeypatch):
    original=parse_metadata(fixture(),pid=m.PID,codes={'15-259'})
    monkeypatch.setattr(m,'SUBJECTS',{'15-259':dict(name='Probability and Computing',category='mathematics',description_digest=original['observed_description_digests']['15-259'])})
    monkeypatch.setattr(m,'CONDITIONS',{})
    a=m.parse(fixture());b=m.parse(fixture(body='Programming and operating systems.'))
    assert a['courses'][0]['category']=='mathematics'
    assert b['courses'][0]['category']=='other'
    assert 'category_review'not in a['courses'][0]
    changed=m.parse(fixture(prerequisite='21-122'))
    assert changed['courses'][0]['prerequisites']=='21-122'
    assert changed['courses'][0]['category']=='mathematics'
    with pytest.raises(ValueError,match='metadata observed'):m.parse(fixture().replace('15-259','15-258'))


def test_reviewed_domains_mixed_subjects_and_roles_are_distinct():
    p=json.loads(Path('data/programs/cmu-bs-ai.json').read_text());validate_program(p)
    by={c['code']:c for c in p['courses']}
    for code in ['15-151','15-259','10-425']:assert by[code]['category']=='mathematics'
    for code in ['15-386','15-387','16-384']:assert by[code]['category']=='applications'
    for code in ['10-405','10-414','11-442','17-416']:
        assert by[code]['category']=='other'and by[code]['category_review']['status']=='mixed'
        assert len(by[code]['category_review']['candidate_categories'])==2
    assert by['15-112']['category']=='foundations'
    assert sum(c.get('category_review')is not None for c in p['courses'])==56
    nodes=[r for r in p['requirements']if r['id'].startswith('cmu-bs-ai-course-entry-')]
    assert len(nodes)==7 and all(r['kind']=='note' and not r['course_ids']for r in nodes)
    assert '21-241 and 21-122 and 15-112' in by['15-387']['prerequisites']
    assert 'desirable'not in by['15-387']['prerequisites']


def test_optional_live_directory_inventory_replay():
    path=Path('.cache/http',hashlib.sha256(COURSE_SOURCE.encode()).hexdigest()+'.body')
    if not path.exists():pytest.skip('Ignored source cache absent')
    d=m.parse(path.read_text())
    assert len(d['courses'])==51 and len(d['requirements'])==7
    assert not any('category_review'in c for c in d['courses'])
    assert not {'curriculum_audit','last_verified'}&d.keys()
