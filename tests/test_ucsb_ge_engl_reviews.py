import csv
import hashlib
import io
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsb_ge_engl_reviews as m


def test_manual_english_content_decisions_and_precise_evidence_limits():
    e={e['code']:e for e in m.SPEC['entries']}
    assert len(e)==121
    assert sum(x['category_review']['status']=='reviewed'for x in e.values())==108
    assert {c for c,x in e.items()if x['category_review']['status']=='unclassified'}=={'ENGL 65AA','ENGL 122WE','ENGL 131AW'}
    assert sum(x['category_review']['status']=='mixed'for x in e.values())==10
    assert set(e['ENGL 102QA']['category_review']['candidate_categories'])=={'human_context','mathematics','ai_ml'}
    assert e['ENGL 155AI']['category']=='human_context'
    assert e['ENGL 155AI']['category_review']['candidate_categories']==[]
    assert 'design and construction' in e['ENGL 155AI']['category_review']['rationale']
    assert set(e['ENGL 170MB']['category_review']['candidate_categories'])=={'human_context','applications'}
    for code in ['ENGL 92SS','ENGL 92TC','ENGL 192CR','ENGL 192SS','ENGL 192WW']:
        assert e[code]['category']=='human_context'
    assert sum(x['prerequisite_flag']=='Yes'for x in e.values())==101
    assert sum(x['credits']==5 for x in e.values())==16
    assert sum(x['credits']==4 for x in e.values())==105
    assert 'fieldwork' in e['ENGL 141PR']['description'] and e['ENGL 141PR']['category']=='human_context'
    assert 'critical' in e['ENGL 155AI']['description'].lower()


def test_export_conditions_do_not_invent_identity_or_rules():
    e={e['code']:e for e in m.SPEC['entries']}
    assert e['ENGL 15']['credits']==5 and e['ENGL 15SH']['credits']==4
    assert any('15SH' in n for n in e['ENGL 15']['notes'])
    assert any('Same course' in n for n in e['ENGL 119X']['notes'])
    assert any('Pass 1 restriction' in n for n in e['ENGL 92SS']['notes'])
    assert any('24 total units' in n for n in e['ENGL 101MM']['notes'])
    assert any('only 8 units' in n for n in e['ENGL 114EM']['notes'])
    assert e['ENGL 92RA']['unit_fields']['Units - Units Variable - Min']=='0'
    assert e['ENGL 92RA']['unit_fields']['Units - Units Variable - Max']=='5'
    assert any('no separate' in n for n in e['ENGL 92RA']['notes'])
    assert e['ENGL 105SF']['source_code']=='ENGL 105SF '
    assert e['ENGL 105SF']['id']=='ucsb-engl-105sf'
    assert e['ENGL 105SF']['name']=='Shakespeare and Film'
    assert all('course_identity_groups'not in x for x in e.values())


def synthetic(row):
    out=io.StringIO();writer=csv.DictWriter(out,fieldnames=row);writer.writeheader();writer.writerow(row);return out.getvalue()


def test_full_row_guard_flags_units_and_comments_without_manual_review(monkeypatch):
    row={'Subject & Prefix':'ENGL','Course Number':'105SF ','Full Course Title':' Shakespeare and Film',
         'Course Description':'Synthetic source text','Prerequisites':'No','Advisor Enrollment Comments':'Condition',
         'Repeat Comments':'Repeat limit','Units - Units Fixed - Unit Value':'5'}
    entry={**m.SPEC['entries'][0],'code':'ENGL 105SF','row_digest':hashlib.sha256(json.dumps(row,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()}
    monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[entry]});monkeypatch.setattr(m.pools,'parse_csv',lambda data:{})
    out=m.parse_csv(synthetic(row));assert 'category_review'not in out['courses'][0]
    assert out['courses'][0]['prerequisites']is None and 'requirements'not in out
    for k,v in [('Prerequisites','Yes'),('Course Description','Changed description'),('Advisor Enrollment Comments','Different restriction'),('Repeat Comments','Other limit'),('Units - Units Fixed - Unit Value','4')]:
        with pytest.raises(ValueError):m.parse_csv(synthetic({**row,k:v}))
    out['courses'][0]['notes'].clear();assert m.parse_csv(synthetic(row))['courses'][0]['notes']
    with pytest.raises(ValueError):m.parse_csv(synthetic(row)+synthetic({**row,'Course Number':'105SF'}).split('\n',1)[1])


def test_optional_complete_actual_export_replay():
    p=Path('.cache/research/ucsb-course-content/ge-defg-export.csv')
    if not p.exists():pytest.skip('Ignored official public CSV export')
    out=m.parse_csv(p.read_text());assert len(out['courses'])==121 and out==m.parse_csv(p.read_text())
    assert all(c['prerequisites']is None and 'category_review'not in c for c in out['courses'])
    assert all(c['credit_unit']=='quarter_hours'for c in out['courses'])
    with pytest.raises(ValueError):m.parse_csv('<html>Human verification required</html>')
