import csv
import hashlib
import io
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsb_ge_catalog_pools as pools
from atlas.adapters import ucsb_registration_review as policy
from atlas.curriculum_profile import requirement_profile


def test_catalog_policy_closes_cal_getc_without_stem_or_college_overreach():
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text())
    byid={r['id']:r for r in d['requirements']}
    transfer=byid['ucsb-ai-bs-progress-ge-current-satisfying']
    assert 'Cal-GETC' in transfer['summary'] and 'Engineering' in transfer['summary']
    assert 'Do not extend this STEM clause' in transfer['summary']
    assert transfer['kind']=='note' and transfer['course_ids']==[]
    overlap=byid['ucsb-ai-bs-progress-ge-current-provisions']['summary']
    assert 'only one' in overlap and 'major course' in overlap
    assert 'Letters and Science only' in byid['ucsb-ai-bs-progress-ge-current-special']['summary']
    assert [requirement_profile(d)[k]['count']for k in ['required','options','unresolved']]==[20,827,2]


def test_pool_manifest_is_membership_only_and_not_a_content_audit():
    assert pools.SPEC['export_row_count']==856
    assert pools.SPEC['area_memberships']=={'D':175,'E':299,'F':168,'G':273}
    assert len({e['code']for e in pools.SPEC['entries']})==856
    assert any(len(e['general_areas'])>1 for e in pools.SPEC['entries'])
    assert all('category_review'not in e and 'description'not in e for e in pools.SPEC['entries'])


def test_export_guard_rejects_changed_content_duplicate_or_shell(monkeypatch):
    row={'Subject & Prefix':'TEST','Course Number':'1','Full Course Title':'Synthetic','General Subject Areas':'Area D: Social Sciences','Course Description':'Synthetic body'}
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=row);writer.writeheader();writer.writerow(row);data=stream.getvalue()
    entry={'code':'TEST 1','name':'Synthetic','general_areas':['D'],'row_digest':hashlib.sha256(json.dumps(row,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()}
    monkeypatch.setattr(pools,'SPEC',{**pools.SPEC,'export_row_count':1,'entries':[entry]})
    result=pools.parse_csv(data)
    assert result['pool_memberships']==[{'code':'TEST 1','name':'Synthetic','general_areas':['D']}]
    assert 'courses'not in result and 'requirements'not in result
    for changed in [data.replace('Synthetic body','Changed body'),data.replace('Area D:','Area E:'),'<main>Loading</main>']:
        with pytest.raises(ValueError):pools.parse_csv(changed)
    result['pool_memberships'][0]['general_areas'].clear()
    assert pools.parse_csv(data)['pool_memberships'][0]['general_areas']==['D']


def test_optional_actual_export_and_policy_captures_replay():
    root=Path('.cache/research/ucsb-course-content');csvpath=root/'ge-defg-export.csv'
    if not csvpath.exists():pytest.skip('Optional ignored official public export')
    assert len(pools.parse_csv(csvpath.read_text())['pool_memberships'])==856
    for key in ['general','satisfying','special','provisions','engineering']:
        html=(root/('policy-ge-'+key+'-reviewed.html')).read_text()
        result=policy.parse(html,key='ge-'+key)
        assert result==policy.parse(html,key='ge-'+key)
        assert len(result['requirements'])==1 and not result['courses']
