from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_codeonly_humanities_reviews as m


def fixture(monkeypatch,code):
    entry=deepcopy(next(e for e in m.SPEC['entries']if e['code']==code))
    subject=code.split()[0];source=m.SPEC['sources'][subject]
    parts=['<h1>'+source['heading']+'</h1><p class="course-disclaimer">2026–27</p>']
    for i,obs in enumerate(entry['observations']):
        body='General historical survey.' if i==0 else 'Specific cultural focus. Prerequisites: instructor consent.'
        obs['description_hash']=hashlib.sha256(body.encode()).hexdigest()
        parts+=['<h2>'+obs['region']+'</h2>']
        if obs['section']!=obs['region']:parts+=['<h3>'+obs['section']+'</h3>']
        parts+=['<p class="course-name">'+obs['heading']+'</p><p class="course-descriptions">'+body+'</p>']
    monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[entry],'context_guards':{}})
    return ''.join(parts)


@pytest.mark.parametrize('code',['HILD 2B','AAS 10R','AAS 11R','GSS 26','HILD 7A'])
def test_literal_groups_and_individual_blocks_emit_exact_metadata_only(monkeypatch,code):
    out=m.parse_observations(fixture(monkeypatch,code),subject=code.split()[0])
    assert [c['code']for c in out['courses']]==[code]
    assert 'category_review' not in out['courses'][0]
    assert 'course_identity_groups'not in out and 'requirements'not in out


@pytest.mark.parametrize('before,after',[('2026–27','2027–28'),('General historical survey.','Different historical survey.'),('instructor consent.','instructor consent. Graduate students only.')])
def test_shared_overview_individual_body_and_eligibility_changes_fail(monkeypatch,before,after):
    html=fixture(monkeypatch,'HILD 7A')
    with pytest.raises(ValueError):m.parse_observations(html.replace(before,after),subject='HILD')


def test_removing_shared_overview_does_not_silently_prefer_individual(monkeypatch):
    html=fixture(monkeypatch,'HILD 7A')
    start=html.index('<p class="course-name">');end=html.index('</p>',html.index('<p class="course-descriptions">',start))+4
    with pytest.raises(ValueError,match='inventory changed'):m.parse_observations(html[:start]+html[end:],subject='HILD')


def test_mutated_group_does_not_implicitly_fill_missing_numeric_member(monkeypatch):
    html=fixture(monkeypatch,'GSS 26').replace('21-22-23-25-26-27.','21-22-23-24-25-26-27.')
    with pytest.raises(ValueError):m.parse_observations(html,subject='GSS')


def test_course_movement_and_duplicate_exact_block_require_review(monkeypatch):
    html=fixture(monkeypatch,'HILD 7A')
    with pytest.raises(ValueError,match='section membership'):
        m.parse_observations(html.replace('<h2>Lower Division</h2>','<h2>Graduate</h2>',1),subject='HILD')
    with pytest.raises(ValueError,match='inventory changed'):
        m.parse_observations(html+html[html.rfind('<p class="course-name">'):],subject='HILD')


def test_chapter_context_is_independently_guarded(monkeypatch):
    html=fixture(monkeypatch,'HILD 2B')
    body='A plus marker indicates pre-1800 focus.'
    m.SPEC['context_guards']={'HILD':[{'tag':'h2','heading':'Courses','content_hash':hashlib.sha256(body.encode()).hexdigest()}]}
    html=html.replace('<h2>Lower Division</h2>','<h2>Courses</h2><p>'+body+'</p><h2>Lower Division</h2>')
    assert m.parse_observations(html,subject='HILD')['courses']
    with pytest.raises(ValueError,match='context changed'):
        m.parse_observations(html.replace('pre-1800','post-1800'),subject='HILD')


def test_new_previously_missing_identifier_is_a_review_event(monkeypatch):
    entry=next(e for e in m.SPEC['entries']if e['code']=='GSS 24')
    monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[entry]})
    html='<h1>Global South Studies</h1><p class="course-disclaimer">2026–27</p><h2>Lower Division</h2><p class="course-name">GSS 24. New Subject (4)</p><p class="course-descriptions">New evidence.</p>'
    with pytest.raises(ValueError,match='Previously missing'):m.parse_observations(html,subject='GSS')


def test_actual_chapters_compose_same_url_and_preserve_all_89_dispositions():
    rows=[];gaps=[]
    for url,parser in m.SOURCE_PARSERS.items():
        source=next(s for s in m.SPEC['sources'].values()if s['url']==url)
        path=Path(source['cache_path'])
        if not path.exists():pytest.skip('Optional ignored official chapter capture absent')
        result=parser(path.read_text());rows+=result['courses'];gaps+=result['source_dispositions']
    assert len(rows)==80 and len(gaps)==9
    assert len({c['id']for c in rows})==80
    assert {c['code']for c in gaps}=={'ANSC 140','CCE 110','CCE 120','DOC 170','ESYS 150','GSS 24','HILD 20','HILD 80GS','USP 103'}
    assert Counter(c['credits']for c in rows)=={4:77,5:3}
    assert Counter(c['category']for c in rows)=={'human_context':63,'applications':11,'other':5,'mathematics':1}
    by={c['code']:c for c in rows}
    assert by['GSS 26']['name']=='South Asia: History, Culture, and Politics'
    assert by['MCWP 40R']['prerequisites']is None and by['MCWP 50R']['prerequisites']is None
    assert by['MCWP 40']['prerequisites']=='satisfaction of Entry Level Writing Requirement.'
    assert 'IGETC' in by['MCWP 50']['prerequisites']
    assert 'Seventh College students only' in by['SYN 100']['prerequisites']
    assert 'letter grade' in by['SYN 100']['prerequisites']
    assert 'grade of C– or better' in by['INTL 101']['prerequisites']
    assert any('preferred but not required' in n for n in by['CAT 125GS']['notes'])


def test_source_supported_categories_and_variant_restrictions():
    e={e['code']:e for e in m.SPEC['entries']}
    assert e['MGT 3']['category']=='mathematics'
    assert e['ANTH 5']['category']=='applications' # anatomy, not prefix-derived humanities
    assert e['ANTH 24']['category']=='human_context'
    assert e['EDS 124BR']['category_review']['status']=='mixed'
    assert 'foundations' in e['EDS 124BR']['category_review']['candidate_categories']
    assert e['SYN 100']['category_review']['status']=='unclassified'
    assert any('prior programming experience is not required' in n for n in e['EDS 124AR']['notes'])
    assert any('letter grade' in n for n in e['MCWP 40CR']['notes'])
    assert any('Global Seminar Program' in n for n in e['HILD 30GS']['notes'])
    assert e['JWSP 1']['credits']==5
