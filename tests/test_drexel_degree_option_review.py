import hashlib,json
from pathlib import Path
import pytest
from atlas import db
from atlas.adapters import drexel_degree_option_review as m

@pytest.mark.parametrize('code',list(m.SPEC))
def test_current_exact_degree_option_when_local_source_present(code):
 p=Path('/tmp/atlas-national-degree-audit/drexel-'+code.replace(' ','').lower()+'.html')
 if not p.exists():pytest.skip('Local actual public course result unavailable')
 o=m.parse(p.read_text(),code);assert o['courses'][0]['code']==code
 assert 'category_review' not in o['courses'][0] and 'curriculum_audit' not in o


def test_exact_result_not_adjacent_course_and_singular_corequisite(monkeypatch):
 text='MATH 999 Example calculus 0.0-4.0 Credits Limits and integrals. Repeat Status: Not repeatable for credit Prerequisites: MATH 100 [Min Grade: C] or AP 4 Corequisite : EXAM 080'
 h='<article class="search-courseresult"><h3>MATH 999 Example calculus 0.0-4.0 Credits</h3><div class="courseblock">'+text.split('Credits ',1)[1]+'</div></article>'
 monkeypatch.setattr(m,'SPEC',{'MATH 999':dict(id='example',url='https://example.edu',source_id='example',digest=hashlib.sha256(text.encode()).hexdigest(),description='Example calculus.',category='mathematics')})
 o=m.parse(h.replace('MATH 999','MATH 998')+h,'MATH 999');c=o['courses'][0]
 assert c['credits'] is None and o['observed_credit_ranges']=={'MATH 999':'0.0-4.0'}
 assert c['prerequisites']=='Prerequisites: MATH 100 [Min Grade: C] or AP 4; Corequisites: EXAM 080'
 for bad in (h+h,h.replace('EXAM 080','EXAM 081'),h.replace('Limits and integrals','Different subject')):
  with pytest.raises(ValueError):m.parse(bad,'MATH 999')


def test_reviewed_degree_options_preserve_variable_credit_and_roles():
 p=json.loads(Path('data/programs',m.PID+'.json').read_text());db.validate_program(p)
 c={x['code']:x for x in p['courses']}
 assert len(m.SPEC)==47 and all(c[k].get('category_review') for k in m.SPEC)
 assert c['UNIV CI101']['credits'] is None and c['UNIV CI101']['category_review']['status']=='unclassified'
 assert c['ECE 413']['category_review']['candidate_categories']==['ai_ml','systems']
 assert all(c[k]['category_review']['status']=='mixed' for k in ('CI 101','CI 102','CI 103'))
 assert all(c[k]['category']=='mathematics' for k in ('ECE 231','ENGR 231','ECE 361'))
 assert c['ECE 492']['category_review']['source_ids']==[m.SPEC['ECE 492']['source_id'],m.SPEC['ECE 491']['source_id']]
 assert 'Corequisites: EXAM 080' in c['MATH 121']['prerequisites']
 assert 'MATH111 practicum' in c['MATH 116']['description']
 assert p.get('course_identity_groups',[])==[]
