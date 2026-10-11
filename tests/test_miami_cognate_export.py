import copy
import importlib.util
import json
from pathlib import Path
import pytest
from atlas.adapters import miami_cognate_export as export

ROOT=Path(__file__).resolve().parents[1]


def page(n,rows):
    return dict(page=n,title=export.TITLE,updated='2026-10-02',headers=export.HEADERS,rows=rows)


PAGES=[page(1,[
 ['AAA','101','A wrapped title','Arts & Humanities','Fall','100001'],
 ['','','continues here','People & Society','Fall','100001'],
 ['AAA','BAS','Alphabetic course number','Arts & Humanities','Spring','100002'],
 ['','200T','Transfer Credit Elective','STEM','N/A','100003'],
]),page(2,[
 ['AAA','101','A wrapped title continues here','Arts & Humanities','Fall','100001'],
 ['','102','Clipped tit..','People & Society','Fall','100004'],
])]


def test_wrapped_title_alpha_transfer_and_multiple_areas_are_preserved():
    r=export.parse_master_pages(PAGES)
    courses={c['code']:c for c in r['rows']}
    assert len(courses)==4
    assert courses['AAA 101']['name']=='A wrapped title continues here'
    assert courses['AAA 101']['areas']==['Arts & Humanities','People & Society']
    assert courses['AAA 101']['pages']==[1,2]
    assert len(courses['AAA 101']['row_locators'])==3
    assert courses['AAA BAS']['source_course_id']=='100002'
    assert courses['AAA 102']['name'] is None
    assert r['counts']['physical_rows']==6 and r['counts']['area_memberships']==5
    assert r['counts']['repeated_area_memberships']==1
    assert sum(p['physical_rows'] for p in r['page_accounting'])==6
    assert not {'curriculum_audit','curriculum_status','last_verified'} & r.keys()


@pytest.mark.parametrize('change',[
 lambda p:p[1].update(page=3),
 lambda p:p[0].update(updated='2026-11-02'),
 lambda p:p[0].update(headers=['Wrong']),
 lambda p:p[0]['rows'][0].__setitem__(3,'Unknown Area'),
 lambda p:p[0]['rows'][1].__setitem__(5,'999999'),
 lambda p:p[1]['rows'][0].__setitem__(5,'999999'),
 lambda p:p[1]['rows'][0].__setitem__(2,'Conflicting title'),
 lambda p:p[0]['rows'][0].__setitem__(2,''),
 lambda p:p[0]['rows'][0].__setitem__(1,'?101'),
])
def test_unreviewed_identity_schema_page_or_context_fails_closed(change):
    pages=copy.deepcopy(PAGES);change(pages)
    with pytest.raises(ValueError):export.parse_master_pages(pages)


def test_partial_or_unreconciled_capture_cannot_emit_full_pool():
    r=export.parse_master_pages(PAGES)
    with pytest.raises(ValueError):export.full_individualized_observation(r,pid='synthetic')


def test_full_manifest_row_accounting_and_visible_page_locators():
    m=json.loads((ROOT/'research/miami-individualized-cognate-pool.json').read_text())
    assert m['counts']==dict(pages=50,physical_rows=2463,course_identities=2075,
        area_memberships=2463,repeated_area_memberships=0,truncated_names=121,
        by_area={'Arts & Humanities':1109,'People & Society':905,'STEM':449})
    assert len(m['rows'])==2075
    assert sum(len(r['row_locators']) for r in m['rows'])==2463
    assert sum(len(r['areas']) for r in m['rows'])==2463
    assert sum(p['physical_rows'] for p in m['page_accounting'])==2463
    assert m['scope']['complete_dated_master_capture'] is True
    assert m['scope']['complete_degree_inventory'] is False
    courses={r['code']:r for r in m['rows']}
    assert courses['APY 435']['pages']==[3] # Plain text included clipped page2 context.
    assert courses['MIP BAS']['name']=='Secondary Bassoon'
    assert courses['APY 423']['name']=='Paleopathology: Health and disease in ancient peoples'
    o=export.full_individualized_observation(m,pid='synthetic')
    assert len(o['courses'])==1680 and len(o['requirements'])==3
    assert all(c['credits'] is None and c['prerequisites'] is None for c in o['courses'])
    assert 'No selected course may satisfy another degree requirement' in o['requirements'][0]['summary']
    assert all(r['kind']=='note' for r in o['requirements'])


def test_optional_public_pdf_layout_replay():
    path=ROOT/'var/miami-cognates-public-export.pdf'
    if not path.exists() or importlib.util.find_spec('pymupdf') is None:
        pytest.skip('Optional ignored public PDF and local extraction package')
    result=export.parse_master_pages(export.extract_master_pdf(path))
    manifest=json.loads((ROOT/'research/miami-individualized-cognate-pool.json').read_text())
    assert result['rows']==manifest['rows']
    assert result['counts']==manifest['counts']
    assert result['page_accounting']==manifest['page_accounting']
