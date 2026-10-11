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


@pytest.mark.parametrize('award,n',[('BA',685),('BS',684)])
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
 groups=p['course_identity_groups'];assert len(groups)=={'BA':37,'BS':38}[award]
 java=next(g for g in groups if g['id'].endswith('java-crosslisting'))
 assert java['course_ids']==[f'case-{award.lower()}-csds-132',f'case-{award.lower()}-uger-ecse-132']
 profile=requirement_profile(p)
 aliases={'BA':54,'BS':55}[award]
 assert profile['identity']['crosslisted_aliases']==aliases
 assert profile['options']['source_record_count']==profile['options']['count']+aliases
 assert profile['required']['count']=={'BA':8,'BS':9}[award]
 byid={c['id']:c for c in p['courses']}
 codegroups=[{byid[c]['code'] for c in g['course_ids']} for g in groups]
 manifest=json.loads(Path('atlas/adapters/case_degree_crosslist_reviews.json').read_text())
 expected=manifest['groups']+(manifest['bs_only_groups'] if award=='BS' else [])
 assert {frozenset(g) for g in codegroups}=={frozenset(g) for g in expected}
 assert not any({'CHIN 350','CHIN 350D'}<=g for g in codegroups)
 assert not any('ENGL 364C' in g for g in codegroups)
 assert {'ENGL 364','HUMN 364'} in codegroups
 assert 'ANEE 107 and ANEE 316' in cs['ANEE 381']['prerequisites']


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
 for dep,count in [('hsty',69),('phed',73)]:
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


@pytest.mark.parametrize('award',['BA','BS'])
def test_cognitive_subjects_and_hyphenated_prerequisites(award):
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 p=json.loads(Path('data/programs',pid+'.json').read_text());cs={c['code']:c for c in p['courses']}
 assert cs['COSI 310']['category']=='applications'
 assert cs['COSI 310']['prerequisites']=='Pre-req: Academic Inquiry Seminar (AIQS) and COSI 109 .'
 assert cs['COGS 250']['category']=='human_context'
 for code in ['COGS 399H','COGS 397']:
  assert cs[code]['category']=='other' and cs[code]['category_review']['status']=='unclassified'
 for dep,count in [('cogs',15),('cosi',4)]:
  path=Path('/tmp/case-uger-audit',dep+'.html')
  if path.exists():
   observed=m.parse_descriptions(path.read_text(),pid=pid,award=award,department=dep)
   assert len(observed['courses'])==count
   assert all('Changed description' not in n for n in observed['notes'])


@pytest.mark.parametrize('award',['BA','BS'])
def test_science_conditions_and_variable_credit_range(award):
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 p=json.loads(Path('data/programs',pid+'.json').read_text());cs={c['code']:c for c in p['courses']}
 assert cs['BTEC 398']['category']=='applications'
 assert cs['BIOC 240']['category']=='human_context'
 assert cs['BIOC 277']['category']=='other' and cs['BIOC 277']['category_review']['status']=='mixed'
 assert 'Restricted to majors in Biochemistry' in cs['BIOC 373']['prerequisites']
 assert 'Instructor consent' in cs['BIOL 309']['prerequisites']
 assert cs['ASTR 351']['credits'] is None
 assert 'minimum of three credit hours' in cs['ASTR 351']['prerequisites']
 bundle=next(r for r in p['requirements'] if set(r['course_ids'])=={cs['EEPS 391']['id'],cs['EEPS 392']['id']})
 assert bundle['kind']=='all' and cs['EEPS 391']['credits']==cs['EEPS 392']['credits']==2
 path=Path('/tmp/case-uger-audit/astr.html')
 if path.exists():
  obs=m.parse_descriptions(path.read_text(),pid=pid,award=award,department='astr')
  assert obs['observed_credit_ranges']=={cs['ASTR 351']['id']:'1 - 3 Units'}
  assert not any('Changed description' in n for n in obs['notes'])


@pytest.mark.parametrize('award',['BA','BS'])
def test_health_conditions_known_zero_and_unspecified_research(award):
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 p=json.loads(Path('data/programs',pid+'.json').read_text());cs={c['code']:c for c in p['courses']}
 assert cs['NURS 277']['credits']==0
 assert cs['NTRN 201']['prerequisites'] is None
 assert 'Nutrition major and Senior standing' in cs['NTRN 350']['prerequisites']
 assert 'Grade of C or better' in cs['NURS 373']['prerequisites'] and 'Coreq:' in cs['NURS 373']['prerequisites']
 assert cs['PSCL 282']['category']==cs['PSCL 375']['category']=='mathematics'
 assert cs['PSCL 395']['category_review']['status']=='unclassified'
 assert cs['NURS 343']['category']=='human_context'
 assert cs['NURS 293']['category_review']['status']=='mixed'
 for dep,count in [('ntrn',17),('nurs',13),('pscl',7)]:
  path=Path('/tmp/case-uger-audit',dep+'.html')
  if path.exists():
   obs=m.parse_descriptions(path.read_text(),pid=pid,award=award,department=dep)
   assert len(obs['courses'])==count
   assert not any('Changed description' in n for n in obs['notes'])


@pytest.mark.parametrize('award',['BA','BS'])
def test_social_science_subjects_and_conditional_capstone(award):
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 p=json.loads(Path('data/programs',pid+'.json').read_text());cs={c['code']:c for c in p['courses']}
 assert cs['SOCI 307']['category']=='mathematics'
 assert 'credit for only one' in cs['SOCI 307']['prerequisites']
 assert cs['SOCI 313']['category']=='applications'
 assert cs['SOCI 267']['category_review']['status']=='mixed'
 assert cs['POSC 221']['category']=='human_context'
 assert 'junior or senior year' in cs['POSC 396']['prerequisites']
 assert 'faculty project advisor' in cs['POSC 396']['prerequisites']
 assert cs['POSC 201']['prerequisites'] is None
 for dep,count in [('posc',36),('soci',32)]:
  path=Path('/tmp/case-uger-audit',dep+'.html')
  if path.exists():
   obs=m.parse_descriptions(path.read_text(),pid=pid,award=award,department=dep)
   assert len(obs['courses'])==count
   assert not any('Changed description' in n for n in obs['notes'])


@pytest.mark.parametrize('award',['BA','BS'])
def test_professional_course_evidence_preserves_sequence_and_section_rules(award):
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 p=json.loads(Path('data/programs',pid+'.json').read_text());cs={c['code']:c for c in p['courses']}
 assert cs['ACCT 100']['category']=='applications'
 assert cs['MGMT 206']['category']=='applications'
 assert cs['ORBH 330']['category_review']['status']=='mixed'
 assert cs['EMAE 398']['category_review']['status']=='unclassified'
 assert cs['MGMT 205']['credits']==cs['MGMT 206']['credits']==1.5
 assert cs['MGMT 395']['credits']==1 and 'No credit for repeating' in cs['MGMT 395']['prerequisites']
 assert 'three sections' in next(r['summary'] for r in p['requirements'] if r['title']=='Disciplinary Communication approved options')
 assert 'only in combination with EBME 370' in cs['EBME 356']['prerequisites']
 assert 'Recommended corequisite: EMSE 372' in cs['EMSE 320']['prerequisites']
 for dep,count in [('ebme',2),('eche',1),('eciv',5),('emac',1),('emae',2),('emse',2),('acct',1),('entp',5),('mgmt',11),('orbh',10)]:
  path=Path('/tmp/case-uger-audit',dep+'.html')
  if path.exists():
   obs=m.parse_descriptions(path.read_text(),pid=pid,award=award,department=dep)
   assert len(obs['courses'])==count
   assert not any('Changed description' in n for n in obs['notes'])


@pytest.mark.parametrize('award',['BA','BS'])
def test_experience_unknowns_and_anthropology_methods(award):
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 p=json.loads(Path('data/programs',pid+'.json').read_text());cs={c['code']:c for c in p['courses']}
 assert cs['DESN 210']['category']=='foundations'
 assert 'No programming experience is required' in cs['DESN 210']['prerequisites']
 assert cs['ANTH 319']['category']=='mathematics'
 assert cs['ANTH 103']['category']=='applications'
 assert cs['EDAB 21']['description'] is None
 for code in ['COOP 1','COOP 10','EDAB 1','EDAB 3','EDAB 11','EDAB 21','PRAC 1','PRAC 4','PRAC 10','PRAC 11']:
  assert cs[code]['credits']==0 and cs[code]['category_review']['status']=='unclassified'
 assert cs['EDUC 394']['credits'] is None
 assert 'No previous or current enrollment' in cs['ANTH 359C']['prerequisites']
 assert 'at least one semester prior' in cs['ANTH 398']['prerequisites']
 assert 'Veale Snyder Fellowship' in cs['VEAL 334']['prerequisites']
 for dep,count in [('coop',2),('desn',1),('edab',4),('educ',2),('prac',4),('sass',2),('univ',1),('veal',1),('anth',19)]:
  path=Path('/tmp/case-uger-audit',dep+'.html')
  if path.exists():
   obs=m.parse_descriptions(path.read_text(),pid=pid,award=award,department=dep)
   assert len(obs['courses'])==count
   assert not any('Changed description' in n for n in obs['notes'])


@pytest.mark.parametrize('award',['BA','BS'])
def test_arts_subjects_hyphenated_corequisite_and_ranges(award):
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 p=json.loads(Path('data/programs',pid+'.json').read_text());cs={c['code']:c for c in p['courses']}
 assert cs['DANC 101']['category']=='applications' and cs['DANC 121']['category']=='human_context'
 assert cs['MUED 343']['category']=='applications'
 assert 'Co-req: MUED 396A' in cs['MUED 396B']['prerequisites']
 assert 'both the fall and spring semesters' in cs['THTR 395']['prerequisites']
 assert 'only through applications' in cs['THTR 395']['prerequisites']
 assert cs['MUHI 317']['category_review']['status']=='mixed'
 for code in ['MUHI 395A','MUHI 395B','THTR 395']:assert cs[code]['category_review']['status']=='unclassified'
 for code in ['MUHI 395B','THTR 395','MUEN 384']:assert cs[code]['credits'] is None
 for dep,count in [('mude',2),('mued',10),('muen',2),('mugn',1),('muhi',15),('danc',6),('thtr',12)]:
  path=Path('/tmp/case-uger-audit',dep+'.html')
  if path.exists():
   obs=m.parse_descriptions(path.read_text(),pid=pid,award=award,department=dep)
   assert len(obs['courses'])==count
   assert not any('Changed description' in n for n in obs['notes'])


@pytest.mark.parametrize('award',['BA','BS'])
def test_coordinator_english_art_review_and_source_unknown(award):
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 p=json.loads(Path('data/programs',pid+'.json').read_text());cs={c['code']:c for c in p['courses']}
 assert cs['ENGL 390C']['category_review']['status']=='unclassified'
 assert cs['ENGL 390C']['credits'] is None
 assert cs['ARTH 101']['category']=='human_context'
 for dep,count in [('engl',31),('arth',23)]:
  path=Path('/tmp/case-uger-audit',dep+'.html')
  if path.exists():
   obs=m.parse_descriptions(path.read_text(),pid=pid,award=award,department=dep)
   assert len(obs['courses'])==count
   assert not any('Changed description' in n for n in obs['notes'])


@pytest.mark.parametrize('award',['BA','BS'])
def test_all_mapped_course_content_has_explicit_review(award):
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 p=json.loads(Path('data/programs',pid+'.json').read_text());cs={c['code']:c for c in p['courses']}
 assert len(cs)=={'BA':744,'BS':756}[award]
 assert all(c.get('category_review') for c in cs.values())
 assert cs['FRCH 377']['category_review']['status']=='unclassified'
 assert cs['HTEC 399B']['category_review']['status']=='unclassified'
 assert cs['WRIT 230']['category']=='human_context'
 assert cs['WGST 391']['category']=='applications'
 assert cs['CLSC 318']['category']=='applications'
 assert cs['GRMN 314']['category_review']['status']=='mixed'
 assert cs['WLIT 382']['category_review']['status']=='mixed' and cs['WLIT 382']['credits']==4
 assert cs['CHIN 350D']['prerequisites'] and 'native' in cs['CHIN 350D']['prerequisites']
 assert 'There are no prerequisites' in cs['WGST 227']['prerequisites']
 for dep in ['beth','chst','hpsc','htec','estd','eths','intl','sjus','writ','afst','wgst','chin','frch','kore','span','grmn','japn','wlit','clsc']:
  path=Path('/tmp/case-uger-audit',dep+'.html')
  if path.exists():
   obs=m.parse_descriptions(path.read_text(),pid=pid,award=award,department=dep)
   assert obs['courses']
   assert not any('Changed description' in n for n in obs['notes'])
