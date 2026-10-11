import hashlib
import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import case_uger_metadata as m
from atlas.curriculum_profile import requirement_profile


def test_explicit_conditions_and_no_inferred_absence():
 body='A course. Coreq: Placement. Prereq: Senior standing. Students cannot earn credit for both X and Y.'
 assert m.eligibility(body,'TEST 1')=='Coreq: Placement. Prereq: Senior standing. Students cannot earn credit for both X and Y.'
 assert m.eligibility('Ordinary description.','TEST 1') is None
 assert m.eligibility('Open to all students (no pre-requisites), with exercises.','PHIL 222')=='Open to all students (no pre-requisites)'


def test_source_change_drops_stale_editorial_claims(monkeypatch):
 body='Writing practice. Coreq: Placement.'
 monkeypatch.setattr(m,'REVIEWS',{'AIQS 999':dict(title='Synthetic inquiry',category='human_context',description='Writing practice.',description_sha256=hashlib.sha256(body.encode()).hexdigest(),course_ids={'BA':'test-aiqs-999'})})
 html='<h1>Academic Inquiry Seminar (AIQS)</h1><div class="courseblock"><p class="courseblocktitle">AIQS 999. Synthetic inquiry. 3 Units.</p><p class="courseblockdesc">'+body+'</p></div>'
 parse=lambda html:m.parse_descriptions(html,pid='test',award='BA',department='aiqs')
 assert parse(html)['courses'][0]['category']=='human_context'
 changed=parse(html.replace('Writing practice.','Entirely changed topic.'))
 assert changed['courses'][0]['category']=='other' and changed['courses'][0]['description'] is None
 assert 'category_review' not in changed['courses'][0] and 'curriculum_audit' not in changed
 with pytest.raises(ValueError,match='identity changed'):parse(html.replace('Synthetic inquiry','New inquiry'))


@pytest.mark.parametrize('award,n',[('BA',235),('BS',234)])
def test_reviewed_uger_semantics_and_reciprocal_identity(award,n):
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 p=json.loads(Path('data/programs',pid+'.json').read_text());cs={c['code']:c for c in p['courses']}
 selected=[cs[c] for c,r in m.REVIEWS.items() if award in r['course_ids']]
 assert len(selected)==n and all(c['category_review'] for c in selected)
 assert all(c['description']==m.REVIEWS[c['code']]['description'] for c in selected)
 assert cs['PHIL 210']['category']=='human_context'
 assert cs['PHIL 391']['category']=='human_context'
 assert cs['PHIL 201']['category']=='mathematics'
 assert cs['CSDS 101']['category']=='other'
 assert cs['PHIL 222']['prerequisites']=='Open to all students (no pre-requisites)'
 assert 'Capstone Advisor' in cs['MATH 352']['prerequisites']
 groups=p['course_identity_groups'];assert len(groups)==1
 assert groups[0]['course_ids']==[f'case-{award.lower()}-csds-132',f'case-{award.lower()}-uger-ecse-132']
 profile=requirement_profile(p)
 assert profile['identity']['crosslisted_aliases']==1
 assert profile['options']['source_record_count']==profile['options']['count']+1
 assert profile['required']['count']=={'BA':8,'BS':9}[award]


@pytest.mark.parametrize('award',['BA','BS'])
def test_optional_actual_combined_course_observations(award):
 if not Path('/tmp/case-uger-audit/records.json').exists():pytest.skip('Ignored actual source cache absent')
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 module=importlib.import_module('atlas.adapters.'+pid+'.adapter')
 for dep in ['csds','ecse','math','aiqs','phil']:
  data=module.SOURCE_PARSERS[m.BASE+dep+'/'](Path('/tmp/case-uger-audit',dep+'.html').read_text())
  assert len({c['id'] for c in data['courses']})==len(data['courses'])
  assert all(c['description'] and 'category_review' not in c for c in data['courses'])
  assert 'course_identity_groups' not in data


@pytest.mark.parametrize('award',['BA','BS'])
def test_history_and_wellness_review_is_precise_not_keyword_based(award):
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 p=json.loads(Path('data/programs',pid+'.json').read_text());cs={c['code']:c for c in p['courses']}
 assert cs['HSTY 301']['category']=='human_context' # early-modern identity theft, not computing security
 assert cs['HSTY 201']['category']=='human_context' # history of science, not scientific methods
 assert 'Recommended Preparation' in cs['HSTY 138']['prerequisites']
 assert cs['PHED 170']['credits']==0 and cs['PHED 170']['description'] is None
 assert 'Limited exact-title review' in cs['PHED 170']['category_review']['rationale']
 assert cs['PHED 222']['category']=='other'
 assert cs['PHED 332']['category']=='applications'
 assert cs['PHED 40B']['prerequisites'] is None # no copying the first-half restriction to the second-half course
 assert 'mastered intermediate swimming skills' in cs['PHED 30A']['prerequisites']
 for dep,count in [('hsty',50),('phed',73)]:
  path=Path('/tmp/case-uger-audit',dep+'.html')
  if path.exists():
   observed=m.parse_descriptions(path.read_text(),pid=pid,award=award,department=dep)
   assert len(observed['courses'])==count
   assert all('Changed description' not in n for n in observed['notes'])


@pytest.mark.parametrize('award',['BA','BS'])
def test_coordinator_religion_batch_source_guards(award):
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 p=json.loads(Path('data/programs',pid+'.json').read_text());cs={c['code']:c for c in p['courses']}
 assert cs['LING 333']['category']=='applications'
 assert cs['RLGN 250']['category']=='human_context'
 assert 'Senior student status and a declared major' in cs['ANEE 381']['prerequisites']
 for dep,count in [('rlgn',38),('anee',7),('jwst',6),('ling',2)]:
  path=Path('/tmp/case-uger-audit',dep+'.html')
  if path.exists():
   observed=m.parse_descriptions(path.read_text(),pid=pid,award=award,department=dep)
   assert len(observed['courses'])==count
   assert all('Changed description' not in n for n in observed['notes'])
