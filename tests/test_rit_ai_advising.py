import hashlib
import json
from pathlib import Path
import pytest
from atlas.adapters import rit_ai_advising as a
from atlas.db import validate_program
ROOT=Path(__file__).resolve().parents[1]


def test_reviewed_pdf_observation_preserves_source_conflict(monkeypatch):
 text='Synthetic visually reviewed 2026–27 advising PDF'
 monkeypatch.setattr(a,'REVIEWED_HASH',hashlib.sha256(a.clean(text).encode()).hexdigest())
 d=a.parse_reviewed(text)
 assert len(d['courses'])==7 and len(d['requirements'])==3
 assert all(c['credits']==3 and c['credit_unit']=='semester_hours' for c in d['courses'])
 assert all(r['kind']=='note' for r in d['requirements'])
 assert 'CSCI-632' in d['requirements'][1]['summary'] and 'CSCI-634' in d['requirements'][1]['summary']
 assert d['requirements'][0]['course_ids']==[a.PROGRAM_ID+'-idai-490']
 assert not {'last_verified','curriculum_status','curriculum_audit'} & d.keys()
 for changed in [text+' changed','<h1>Access denied</h1>','%PDF-1.7']:
  with pytest.raises(ValueError):a.parse_reviewed(changed)


def test_curated_pool_not_silently_expanded():
 d=json.loads((ROOT/'data/programs'/f'{a.PROGRAM_ID}.json').read_text());validate_program(d)
 assert len(d['courses'])>=74 and d['curriculum_status']=='partial'
 existing=next(r for r in d['requirements'] if r['id']==a.PROGRAM_ID+'-ai-electives')
 assert not any(x.endswith(('-csci-632','-ling-582','-ling-584')) for x in existing['course_ids'])
 assert any('IDAI-490 program WI is verified' in x for x in d['curriculum_audit']['unresolved_requirements'])
 assert any('CSCI-632' in x and 'CSCI-634' in x for x in d['curriculum_audit']['unresolved_requirements'])


def test_optional_reviewed_pdf_text():
 p=Path('/tmp/rit-ai-flow.txt')
 if not p.exists():pytest.skip('Optional public PDF extraction stays outside repository')
 assert len(a.parse_reviewed(p.read_text())['courses'])==7
