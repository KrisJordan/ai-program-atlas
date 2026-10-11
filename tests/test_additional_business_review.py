"""Guard the explicit business review boundary and changed-source behavior."""
import importlib
import json
from pathlib import Path
import pytest
from atlas.additional_major_audit import validate_ledger
from atlas.adapters.additional_business_metadata import parse_metadata

ROOT=Path(__file__).resolve().parents[1]
PIDS=('villanova-analytics-ai-co-major','marquette-applied-ai-business-major')


def test_manual_business_review_rejects_changed_eligibility_and_same_count_option():
    ledger=json.loads((ROOT/'research/additional-major-review-business.json').read_text())
    programs=[json.loads((ROOT/'data/programs'/f'{pid}.json').read_text()) for pid in PIDS]
    validate_ledger(ledger,programs)
    programs[0]['major_relationship']['eligibility']+=' Different cohort.'
    with pytest.raises(ValueError,match='stale'):
        validate_ledger(ledger,programs)
    programs=[json.loads((ROOT/'data/programs'/f'{pid}.json').read_text()) for pid in PIDS]
    programs[1]['requirements'][4]['count']=1
    with pytest.raises(ValueError,match='stale'):
        validate_ledger(ledger,programs)


def test_changed_course_description_does_not_reuse_reviewed_ethics_category():
    url='https://bulletin.marquette.edu/course-descriptions/insy/'
    html='''<main><div class="courseblock"><span class="detail-code">INSY 4180</span>
    <span class="detail-title">Ethics, Governance, and Responsible Use in AI</span>
    <span class="detail-hours_html">(3 credits)</span>
    <div class="courseblockextra">Changed to a course in neural-network implementation.</div>
    <span class="detail-prereq">Prerequisite: BUAD 2001</span></div></main>'''
    result=parse_metadata(html,pid=PIDS[1],url=url)
    assert result['courses'][0]['description'] is None
    assert result['courses'][0]['category']=='other'
    assert result['courses'][0]['prerequisites']=='BUAD 2001'
    assert 'category_review' not in result['courses'][0]
    assert 'curriculum_audit' not in result
    with pytest.raises(ValueError,match='identity'):
        parse_metadata(html.replace('INSY 4180','INSY 4190'),pid=PIDS[1],url=url)


def test_marquette_consent_and_fixed_ethics_sequence_are_retained():
    p=json.loads((ROOT/'data/programs'/f'{PIDS[1]}.json').read_text())
    courses={c['code']:c for c in p['courses']}
    assert 'Completed the Disruptive Tech focus or the Machine Learning focus' in courses['INSY 4180']['prerequisites']
    assert 'Sr. stndg.' in courses['INSY 4180']['prerequisites']
    assert 'cons. of instr.' in courses['AIM 4410']['prerequisites']
    assert all(c['credits']==3 for c in courses.values())


@pytest.mark.parametrize('pid',PIDS)
def test_permitted_actual_capture_parses_match_reviewed_metadata(pid):
    rows=json.loads((ROOT/'atlas/adapters'/pid/'course_reviews.json').read_text())
    cache=ROOT/'.cache/additional-business'
    import hashlib
    for url in dict.fromkeys(r['url'] for r in rows):
        path=cache/(hashlib.sha256(url.encode()).hexdigest()+'.html')
        if not path.exists():pytest.skip('Optional ignored actual source captures unavailable')
        result=parse_metadata(path.read_text(),pid=pid,url=url)
        assert all(c['description'] for c in result['courses'])
        assert not any(n.startswith('Changed descriptions') for n in result['notes'])
        assert 'last_verified' not in result
