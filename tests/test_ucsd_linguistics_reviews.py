import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_linguistics_reviews as m


def test_expanded_language_heading_and_half_units(monkeypatch):
    e=dict(next(e for e in m.SPEC['entries']if e['code']=='LISP 1A'));body='Conversation. Must be taken with LISP 1AX. Prerequisites: no prior study of Spanish.'
    e['description_hash']=hashlib.sha256(body.encode()).hexdigest();monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[e],'supplementary_blocks':[]})
    html='<h1>Linguistics</h1><p class="course-disclaimer">2026–27</p><p class="course-name">'+e['heading']+'</p><p>'+body+'</p>'
    r=m.parse_observations(html);c=r['courses'][0]
    assert c['code']=='LISP 1A'and c['credits']==2.5
    assert 'category_review'not in c and'requirements'not in r
    assert any('conjunction' in n for n in c['notes'])
    with pytest.raises(ValueError):m.parse_observations(html.replace('LISP 1AX','LISP 1BX'))


def test_actual_language_variants_do_not_replace_unsuffixed_identity():
    path=Path(m.SPEC['sources']['LING']['cache_path'])
    if not path.exists():pytest.skip('Optional ignored Linguistics chapter')
    r=m.parse_observations(path.read_text());cs={c['code']:c for c in r['courses']}
    assert len(cs)==25 and len(r['source_dispositions'])==14
    assert sum(c['credits']==2.5 for c in cs.values())==10
    assert sum(c['credits']==4 for c in cs.values())==15
    assert 'LIHL 118'in cs and'LIHL 112'not in cs
    assert len(m.SPEC['supplementary_blocks'])==39
    assert not any(c.startswith('LIHL 112')for c in cs)
    assert cs['LIGN 152']['prerequisites']is None
    assert any('Recommended preparation' in n for n in cs['LIGN 152']['notes'])
    assert cs['LIGN 8']['prerequisites']=='none. Satisfies DEI requirement.'
    assert 'C– or better' in cs['LISP 1B']['prerequisites']
    assert 'grade of D or better' in cs['LISP 1B']['prerequisites']


def test_related_variant_body_changes_withdraw_disposition_evidence():
    path=Path(m.SPEC['sources']['LING']['cache_path'])
    if not path.exists():pytest.skip('Optional ignored Linguistics chapter')
    html=path.read_text();from bs4 import BeautifulSoup
    soup=BeautifulSoup(html,'html.parser')
    heading=next(h for h in soup.select('p.course-name')if '112F.'in h.get_text())
    heading.find_next_sibling('p').append(' Changed condition.')
    with pytest.raises(ValueError,match='Related heritage-language'):
        m.parse_observations(str(soup))
