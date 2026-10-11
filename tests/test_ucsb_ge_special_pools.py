import csv
import hashlib
import io
import json
from pathlib import Path
from collections import Counter
import pytest
from atlas.adapters import ucsb_ge_special_pools as m
from atlas.curriculum_profile import requirement_profile


def test_special_tag_observer_is_bounded_and_guarded(monkeypatch):
    rows=[{'Subject & Prefix':'DEMO','Course Number':'1','Full Course Title':'Example',
           'General Subject Areas':'D','Special Subject Areas':'Writing, Ethnicity'}]
    def csv_text(rows):
        out=io.StringIO();w=csv.DictWriter(out,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows);return out.getvalue()
    e={'code':'DEMO 1','name':'Example','general_areas':['D'],
       'row_digest':hashlib.sha256(json.dumps(rows[0],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()}
    monkeypatch.setattr(m.ucsb_ge_catalog_pools,'SPEC',{'program_id':'ucsb-ai-bs','catalog_year':'2026-2027','export_row_count':1,'entries':[e]})
    out=m.parse_csv(csv_text(rows))
    assert out['special_memberships']==[{'code':'DEMO 1','special_areas':['WRT','ETH']}]
    assert 'full special-designation pool unverified' in out['pool_scope']
    assert 'courses'not in out and 'requirements'not in out
    with pytest.raises(ValueError):m.parse_csv(csv_text(rows).replace('Writing, Ethnicity','Writing'))


def test_special_overlay_memberships_do_not_create_fixed_load_or_qnt_rule():
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text());rules={r['id']:r for r in d['requirements']}
    for suffix,n in [('writing',492),('ethnicity',116),('culture',287)]:
        r=rules['ucsb-ai-bs-policy-'+suffix]
        assert len(r['course_ids'])==n and r['kind']=='choose_courses'
        assert 'not a certified complete' in r['summary']
    assert [requirement_profile(d)[k]['count']for k in ['required','options','unresolved']]==[20,827,2]
    assert not any('qnt' in r['id']for r in d['requirements'])
    path=Path('.cache/research/ucsb-course-content/ge-defg-export.csv')
    if not path.exists():pytest.skip('Optional private complete export')
    out=m.parse_csv(path.read_text());counts=Counter(a for r in out['special_memberships']for a in r['special_areas'])
    assert counts=={'WRT':492,'ETH':116,'EUR':96,'NWC':191,'QNT':3}
