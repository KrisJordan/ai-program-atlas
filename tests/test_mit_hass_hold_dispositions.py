"""Unresolved identity does not license metadata adoption or prefix categories."""
from importlib import import_module
from pathlib import Path
import json
m=import_module('atlas.adapters.mit-ai-decision-making-bs.hass_hold_dispositions')


def test_original_title_review_withdraws_when_literal_identity_changes():
    cid='mit-ai-hass-russian-and-eurasian-studies-21g-612';r=m.ROWS[cid]
    parser=lambda name:dict(courses=[dict(id=cid,code=r['code'],name=name,category='systems',notes=[])],requirements=[dict(id='guarded-field')])
    parse=m.with_dispositions(parser,r['url'])
    out=parse(r['name'])
    assert out['courses'][0]['category']=='human_context'
    assert 'category_review'not in out['courses'][0]
    assert out['requirements']==[dict(id='guarded-field')]
    assert parse('A changed unknown subject')['courses'][0]['category']=='other'


def test_held_metadata_stays_unadopted_and_broad_title_unknown():
    d=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text());by={c['id']:c for c in d['courses']}
    assert len(m.ROWS)==22
    assert sum(r['hold_status']=='source_conflict'for r in m.ROWS.values())==2
    for cid,r in m.ROWS.items():
        c=by[cid]
        assert c['category']==r['category']
        assert c['category_review']['source_ids']==[r['source_id']]
        assert c['description']is None
    r=by['mit-ai-hass-ancient-and-medieval-studies-4-614']
    assert r['name']=='Building Islam'and r['category_review']['status']=='unclassified'
    assert r['category']=='other'
    assert by['mit-ai-hass-russian-and-eurasian-studies-21g-612']['name']=='Russian II (Regular)'
    assert by['mit-ai-hass-african-and-african-diaspora-studies-21w-742j']['category']=='human_context'
