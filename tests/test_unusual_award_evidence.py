"""Exact institutional award labels survive normalization and observation refresh."""
from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from atlas import db
from atlas.awards import major_award_buckets, validate_award_options
from atlas.family_store import ingest_family
from atlas.http import FetchResult
from atlas.scrape import scrape_one

ROOT=Path(__file__).resolve().parents[1]
CASES=[
 ('miami-ai-technologies-business-bsba','B.S.B.A.','other'),
 ('university-of-miami-artificial-intelligence-technologies-for-business-other-degree','B.B.A.','other'),
 ('northeastern-chemical-engineering-ai-bsche','BSChE','other'),
 ('northeastern-university-environmental-engineering-and-artificial-intelligence-bsenve-boston-other-degree','BSEnvE','other'),
 ('university-of-maryland-college-park-artificial-intelligence-computational-structures-for-ai-systems-bsai-degree','BSAI','BS'),
 ('university-of-south-florida-artificial-intelligence-bs-degree','BSAI','BS'),
]

def seed(pid):return json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())

@pytest.mark.parametrize('pid,label,bucket',CASES)
def test_exact_evidence_normalization_and_no_curriculum_mutation(pid,label,bucket):
    p=seed(pid);before=deepcopy(p);validate_award_options(p)
    option,=p['award_options']
    assert option['label']==label and option['normalized']==bucket
    assert option['source_id'] in {s['id'] for s in p['sources']}
    assert option['locator']
    assert major_award_buckets(p)==[bucket] and p==before
    if label in {'BSChE','BSEnvE'}:assert bucket!='BSE'
    if bucket=='BS':assert 'Bachelor of Science' in option['locator']

@pytest.mark.parametrize('pid,label,bucket',CASES)
def test_curated_awards_survive_observation_and_repeat_ingest(tmp_path,pid,label,bucket):
    p=seed(pid);c=db.connect(tmp_path/'atlas.sqlite');db.migrate(c)
    try:
        if p.get('family'):
            f=json.loads((ROOT/'data/families'/f"{p['family']['id']}.json").read_text())
            db.upsert_institution(c,p['institution']);ingest_family(c,f,program_updates={pid:p})
        else:
            assert db.ingest_program(c,p)
        assert not db.ingest_program(c,p)
        # A valid fresh observation intentionally omits reviewed award metadata.
        observed={'id':pid,'title':p['title'],'award_level':p['award_level']}
        url=p['sources'][0]['url']
        module=SimpleNamespace(SOURCES=(url,),parse=lambda _:observed)
        body='<h1>Source observation fixture</h1>'
        fetcher=SimpleNamespace(fetch=lambda url,force=False:FetchResult(url,body,hashlib.sha256(body.encode()).hexdigest(),'2026-10-11',200,True))
        assert scrape_one(c,pid,module,fetcher)['new_candidates']==1
        assert scrape_one(c,pid,module,fetcher)['new_candidates']==0
        exported=next(x for x in db.export_data(c)['programs'] if x['id']==pid)
        assert exported['award_options']==p['award_options']
        assert major_award_buckets(exported)==[bucket]
        assert not db.ingest_program(c,p)
        assert c.execute('PRAGMA foreign_key_check').fetchall()==[]
    finally:c.close()

@pytest.mark.parametrize('pid,label,bucket',CASES)
def test_existing_primary_source_parser_does_not_rewrite_award_metadata(pid,label,bucket):
    module=importlib.import_module('atlas.adapters.'+pid+'.adapter')
    url=module.SOURCES[0]
    path=ROOT/'.cache/http'/(hashlib.sha256(url.encode()).hexdigest()+'.body')
    if not path.exists():pytest.skip('Private reviewed source cache is optional')
    observed=module.parse(path.read_text())
    # Parser omissions are deliberate: reviewed mappings are retained by the queue.
    assert 'award_options' not in observed or observed['award_options']==seed(pid)['award_options']
    assert observed['id']==pid
