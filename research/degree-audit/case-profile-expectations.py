"""Direct source-table roles, independent of adapters and requirement_profile traversal."""
import json,re,collections
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean
cats=['foundations','mathematics','ai_ml','systems','human_context','applications','electives','other']
uger=BeautifulSoup(Path('.cache/http/fc47400ef7eaca133224a9e1dba166ed2a973429506d39f7b0aaa9e9805aa436.body').read_text(),'html.parser').find(id='textcontainer').find_all('table',class_='sc_courselist')
def codes(t):
 return {clean(a.get_text(' ',strip=True)) for a in t.select('a.code') if re.fullmatch(r'[A-Z]{2,5} \d+[A-Z]?',clean(a.get_text(' ',strip=True)))}
assert len(uger)==13
option_uger=set().union(*(codes(uger[i]) for i in [0,1,2,3,4,9,10,11,12]));wellness=set().union(*(codes(uger[i]) for i in [5,6,7,8]))
ledger=Path('research/degree-audit/case-western.json');d=json.loads(ledger.read_text());result={}
for a in ['ba','bs']:
 p=json.loads(Path('data/programs',f'case-western-reserve-university-artificial-intelligence-{a}-degree.json').read_text());bycode={c['code']:c for c in p['courses']};byid={c['id']:c for c in p['courses']}
 panel=BeautifulSoup(Path('/tmp/case-audit-'+a+'.html').read_text(),'html.parser').find(id='programrequirementstextcontainer');major=set().union(*(codes(t) for t in panel.find_all('table',class_='sc_courselist')))
 fixed={'MATH 121','MATH 307','CSDS 233','CSDS 302','CSDS 310','CSDS 330','CSDS 340','CSDS 395A'}|({'ENGR 399'} if a=='bs' else set())
 expected_source=major|option_uger|wellness
 assert expected_source==set(bycode),(expected_source-set(bycode),set(bycode)-expected_source)
 aliases={c['id']:c['id'] for c in p['courses']}
 for g in p['course_identity_groups']:
  for cid in g['course_ids']:aliases[cid]=g['canonical_course_id']
 canonical=lambda cs:{aliases[bycode[c]['id']] for c in cs}
 required=canonical(fixed);options=canonical((major-fixed)|option_uger)-required;unresolved=canonical(wellness)-required-options
 assert required|options|unresolved==set(aliases.values())
 sets=dict(required=sorted(required),options=sorted(options),unresolved=sorted(unresolved));profiles={k:dict(count=len(v),categories={cat:sum(byid[c]['category']==cat for c in v) for cat in cats}) for k,v in sets.items()}
 result[a]=dict(source_course_count=len(bycode),source_option_codes=sorted((major-fixed)|option_uger),wellness_codes=sorted(wellness),expected_course_ids=sets,expected_profile=profiles)
 entry=next(e for e in d['programs'] if e['program_id']==p['id']);entry['expected_course_ids']=sets;entry['expected_profile']=profiles
 print(a,profiles)
print(json.dumps(result,indent=2))
