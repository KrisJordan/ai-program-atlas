"""Synthetic IU concentration regression cases; full source bodies are never committed."""
import hashlib
import importlib
import json
from pathlib import Path
import pytest
from atlas.db import validate_program

ROOT=Path(__file__).resolve().parents[1]
M=importlib.import_module('atlas.adapters.indiana-cs-ai-specialization.adapter')


def fixture():
    pools=[['CSCI-B 351 Synthetic AI','CSCI-B 365 Synthetic data','CSCI-B 455 Synthetic learning'],['CSCI-B 351 Synthetic AI','MATH-M 365 Synthetic probability OR STAT-S 350 Synthetic inference','CSCI-B 490 Synthetic seminar (Topic: Generative AI and Applications)'],['CSCI-B 401 Synthetic theory']]
    phrases=['Select two courses from the following:','Select two courses from the following (if not used above):','Select one course from the following:']
    return '<main id="content"><div id="image_hd_content"><h5>Artificial Intelligence Specialization</h5><ol>'+''.join('<li>'+h+'<ul>'+''.join('<li>'+c+'</li>' for c in p)+'</ul></li>' for h,p in zip(phrases,pools))+'</ol></div></main>'


def test_observed_choices_nested_alternative_and_no_reviewer_claims():
    d=M.parse(fixture());r=d['requirements']
    roots=[x for x in r if x['parent_id'] is None]
    assert [x['count'] for x in roots]==[2,2,1]
    math=next(x for x in r if len(x['course_ids'])==2)
    assert math['kind']=='choose_courses' and math['count']==1 and math['parent_id']==roots[1]['id']
    assert 'Do not reuse' in roots[1]['summary']
    assert all(c['name'].startswith('Synthetic') for c in d['courses'])
    assert not {'last_verified','curriculum_status','curriculum_audit'}&d.keys()
    with pytest.raises(ValueError):M.parse(fixture().replace('if not used above','may reuse'))
    with pytest.raises(ValueError):M.parse(fixture().replace('Select two courses','Select three courses',1))
    with pytest.raises(ValueError):M.parse('<h1>Sign in</h1><input type="password">'+fixture())


def test_local_scope_review_and_source_registration():
    p=json.loads((ROOT/'data/programs/indiana-cs-ai-specialization.json').read_text());validate_program(p)
    assert p['curriculum_status']=='complete' and p['curriculum_audit']['scope']=='concentration'
    assert not p['curriculum_audit']['unresolved_requirements']
    assert set(M.SOURCES)<={s['url'] for s in p['sources']}
    assert len(p['courses'])==14 and len(p['requirements'])==23
    assert next(c for c in p['courses'] if c['code']=='CSCI-B 490')['credits'] is None


@pytest.mark.parametrize('url',M.SOURCES)
def test_cached_sources_reparse_without_review_claims(url):
    path=ROOT/'.cache/http'/(hashlib.sha256(url.encode()).hexdigest()+'.body')
    if not path.exists():pytest.skip('Optional local evidence cache unavailable')
    d=M.SOURCE_PARSERS[url](path.read_text())
    assert d['id']==M.PROGRAM_ID and not {'last_verified','curriculum_status','curriculum_audit'}&d.keys()


def test_policies_reject_changed_honors_grade_and_overlap():
    text='<main>Specializations Artificial Intelligence Equivalent honors versions of regular courses may substitute for all requirements; add or change your specialization through SAMS; minimum grade of C- in each specialization course</main>'
    assert len(M.parse_specialization_policies(text)['requirements'])==2
    with pytest.raises(ValueError):M.parse_specialization_policies(text.replace('C-','C+'))
    with pytest.raises(ValueError):M.parse_specialization_policies(text.replace('SAMS','another system'))
