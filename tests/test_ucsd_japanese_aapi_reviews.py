import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_japanese_aapi_reviews as m


def fixture(monkeypatch,code='JAPN 135A',body='Professional language communication.'):
    e=dict(next(e for e in m.SPEC['entries']if e['code']==code));e['description_hash']=hashlib.sha256(body.encode()).hexdigest();key=e['source_key'];src=m.SPEC['sources'][key]
    html=f'<h1>{src["heading"]}</h1><h2>Courses</h2><p class="course-disclaimer">For course descriptions not found in the UC San Diego General Catalog 2026–27</p><h3>{e["division"]}</h3><p class="course-name">{e["heading"]}</p><p class="course-descriptions">{body}</p>'
    sources={**m.SPEC['sources'],key:{**src,'chapter_context_sha256':m.chapter_context_hash(html)}};monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[e],'sources':sources});return html,key


def test_language_not_business_methods_and_placement_scope(monkeypatch):
    html,key=fixture(monkeypatch);c=m.parse_observations(html,subject=key)['courses'][0]
    assert c['category']=='human_context'and c['credits']==4
    assert any('placement test and oral interview' in n for n in c['notes'])
    assert 'category_review'not in c


def test_no_unit_amount_and_unspecified_topic_remain_unknown(monkeypatch):
    html,key=fixture(monkeypatch,'JAPN 180');c=m.parse_observations(html,subject=key)['courses'][0]
    assert c['credits']is None and c['category']=='other'and c['prerequisites']is None
    assert not any('placement test' in n for n in c['notes'])


def test_research_seminar_does_not_silently_replace_old_topics(monkeypatch):
    html,key=fixture(monkeypatch,'JAPN 190');r=m.parse_observations(html,subject=key)
    assert r['courses']==[]and r['source_dispositions'][0]['status']=='source_title_conflict'


@pytest.mark.parametrize('subject,count,holds',[('JAPN',5,1),('AAPI',2,0)])
def test_actual_replay_guards_edition_body_and_context(subject,count,holds):
    p=Path(m.SPEC['sources'][subject]['cache_path'])
    if not p.exists():pytest.skip('Optional official source capture absent')
    html=p.read_text();r=m.parse_observations(html,subject=subject)
    assert len(r['courses'])==count and len(r['source_dispositions'])==holds
    assert all('category_review'not in c for c in r['courses'])
    with pytest.raises(ValueError):m.parse_observations(html.replace('2026','2027'),subject=subject)
    if subject=='JAPN':
        with pytest.raises(ValueError,match='context'):
            m.parse_observations(html.replace('oral interview','written interview'),subject=subject)


def test_soc_and_soci_are_not_merged_from_title():
    hold=m.SPEC['identity_holds'][0]
    assert hold['code']=='SOC 102'
    assert 'SOC-102' in hold['finding']and'SOCI102' in hold['finding']
    assert 'no description, prerequisite or credit transfer' in hold['finding']
