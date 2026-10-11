"""Major pool evidence guards, source conflicts and role preservation."""
import hashlib
import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import case_degree_metadata as m


def synthetic(monkeypatch):
 body='Study algorithm construction. Prereq: Placement or permission.'
 monkeypatch.setattr(m,'REVIEWS',{'CSDS 999':dict(title='Synthetic methods',category='foundations',description='Algorithm construction.',rationale='Synthetic.',candidate_categories=[],description_sha256=hashlib.sha256(body.encode()).hexdigest(),awards=['BA'])})
 return '<h1>Computer and Data Sciences (CSDS)</h1><div class="courseblock"><p class="courseblocktitle">CSDS 999. Synthetic methods. 3 Units.</p><p class="courseblockdesc">'+body+'</p></div>'


def test_changed_description_never_reuses_review(monkeypatch):
 html=synthetic(monkeypatch)
 parse=lambda h:m.parse_descriptions(h,pid='test',award='BA',department='csds')
 good=parse(html);c=good['courses'][0]
 assert c['category']=='foundations' and c['prerequisites']=='Prereq: Placement or permission.'
 assert c['credit_unit']=='unknown' and c['credits']==3
 assert 'category_review' not in c and 'curriculum_audit' not in good
 changed=parse(html.replace('algorithm construction','cultural history'))
 assert changed['courses'][0]['category']=='other' and changed['courses'][0]['description'] is None
 assert changed['observed_description_digests']!=good['observed_description_digests']
 with pytest.raises(ValueError,match='title changed'):parse(html.replace('Synthetic methods','New methods'))
 with pytest.raises(ValueError,match='department identity'):parse(html.replace('Computer and Data Sciences (CSDS)','Wrong department'))
 with pytest.raises(ValueError,match='missing or duplicated'):parse(html+html.split('</h1>')[1])


def test_eligibility_preserves_non_prereq_restrictions_and_unknown():
 assert m.eligibility('Physics. Admission to this course is by invitation only. Students may earn credit for only one course.').startswith('Admission')
 assert m.eligibility('Mathematics. Credit for at most one course. Prereq: Placement.').endswith('Prereq: Placement.')
 assert m.eligibility('An ordinary description.') is None


@pytest.mark.parametrize('award,count',[('BA',59),('BS',72)])
def test_reviewed_named_major_counts_and_conflicts(award,count):
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 p=json.loads(Path('data/programs',pid+'.json').read_text())
 courses={c['code']:c for c in p['courses'] if c['id'].startswith('case-'+award.lower()+'-') and not c['id'].startswith('case-'+award.lower()+'-uger-')}
 reviewed=[c for c in courses.values() if c['code'] in m.REVIEWS and award in m.REVIEWS[c['code']]['awards']]
 assert len(reviewed)==count
 assert all(c['description'] and c['category_review'] for c in reviewed)
 assert courses['CSDS 102']['category']=='other'
 assert 'no current or previous enrollment' in courses['CSDS 102']['prerequisites']
 assert 'or Requisites Not Met permission' in courses['CSDS 499']['prerequisites']
 assert courses['CSDS 463']['code']=='CSDS 463' # inconsistent footer is not a rename
 if award=='BA':
  assert p['curriculum_status']=='complete'
  assert not p['curriculum_audit']['unresolved_requirements']
  assert any('Conditional requisite' in r['title'] for r in p['requirements'])
  for code in ['SCMG 462','SCMG 463']:
   assert 'Master of Supply Chain Management program' in courses[code]['prerequisites']
   assert courses[code]['credits']==1.5
  assert courses['SCMG 463']['category']=='applications' # digitization cases, not title-only AI
 else:
  assert 'invitation only' in courses['PHYS 123']['prerequisites']
 module=importlib.import_module('atlas.adapters.'+pid+'.adapter')
 assert m.BASE+'math/' in module.SOURCE_PARSERS
 assert m.BASE+'scmg/' in module.SOURCE_PARSERS if award=='BA' else m.BASE+'phys/' in module.SOURCE_PARSERS


@pytest.mark.parametrize('award',['BA','BS'])
def test_optional_actual_subject_pages(award):
 if not Path('/tmp/case-full-audit/fetch-index.json').exists():pytest.skip('Ignored actual source cache absent')
 count=0
 for dep in m.HEADINGS:
  expected=[c for c,r in m.REVIEWS.items() if c.startswith(dep.upper()+' ') and award in r['awards']]
  if not expected:continue
  result=m.parse_descriptions(Path('/tmp/case-full-audit',dep+'.html').read_text(),pid='test',award=award,department=dep)
  assert len(result['courses'])==len(expected)
  assert all(c['description'] is not None for c in result['courses'])
  assert all('category_review' not in c for c in result['courses'])
  count+=len(expected)
 assert count=={'BA':59,'BS':72}[award]
