"""Independent actual-source code pools and manual role sets; no graph traversal."""
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

PID='northwestern-university-artificial-intelligence-major-bs-in-engineering-bse-degree'

def clean(s): return re.sub(r'\s+', ' ', s).strip()

def calculate():
    p=json.loads(Path('data/programs',PID+'.json').read_text())
    major=BeautifulSoup(Path('/tmp/nw-audit-major.html').read_text(),'html.parser').find(id='textcontainer')
    college=BeautifulSoup(Path('/tmp/nw-audit-college.html').read_text(),'html.parser').find(id='requirementstextcontainer')
    tables=major.find_all('table',class_='sc_courselist')+college.find_all('table',class_='sc_courselist')
    codes={clean(a.get_text(' ',strip=True)) for t in tables for tr in t.find_all('tr') if tr.find('td') for a in tr.find('td').select('a.code')}
    # Exact current prose/footnote additions, read independently from source tables.
    intro=re.search(r'introductory courses that directly support computer science \((.*?)\)',clean(major.get_text(' ',strip=True)))[1]
    codes.update(re.findall(r'\b[A-Z]+(?:_[A-Z]+)* \d+[A-Z]*(?:-\d+)?\b',intro))
    codes.update(['GEN_ENG 212-0','ES_APPM 252-1','ES_APPM 252-2'])
    theme={'BUS_INST 303-0','GEOG 240','GEOG 312','GEOG 313','GEOG 328','MMSS 211-1','MMSS 211-3','MMSS 311-2','NAV_SCI 120-0','NAV_SCI 230-0','NAV_SCI 341-0','TEACH_ED 329-0','TRANS 310-0'}
    codes.update(theme)
    assert codes=={c['code']for c in p['courses']},(codes-{c['code']for c in p['courses']},{c['code']for c in p['courses']}-codes)
    fixed={'MATH 220-1','MATH 220-2','COMP_SCI 212-0','COMP_SCI 208-0','COMP_SCI 211-0','COMP_SCI 348-0','COMP_SCI 349-0','GEN_ENG 231-0','GEN_ENG 241-0','DSGN 106-1','DSGN 106-2','ENGLISH 106-1','ENGLISH 106-2'}
    context={'ES_APPM 252-2'}
    aliases={cid:g['canonical_course_id']for g in p.get('course_identity_groups',[])for cid in g['course_ids']}
    required={c['id']for c in p['courses']if c['code']in fixed}
    unresolved={c['id']for c in p['courses']if c['code']in context}
    options={aliases.get(c['id'],c['id'])for c in p['courses']}-required-unresolved
    sets=dict(required=sorted(required),options=sorted(options),unresolved=sorted(unresolved))
    cats=['foundations','mathematics','ai_ml','systems','human_context','applications','electives','other'];byid={c['id']:c for c in p['courses']}
    profiles={role:dict(count=len(ids),categories={cat:sum(byid[c]['category']==cat for c in ids)for cat in cats})for role,ids in sets.items()}
    # Independently tallied current reviewed categories, not copied from graph output.
    totals={'required':[2,5,2,0,2,0,0,2],'options':[8,8,24,29,16,61,0,29],'unresolved':[0,1,0,0,0,0,0,0]}
    for role in totals: assert list(profiles[role]['categories'].values())==totals[role]
    return dict(expected_profile=profiles,expected_course_ids=sets)

if __name__=='__main__': print(json.dumps(calculate(),indent=2))
