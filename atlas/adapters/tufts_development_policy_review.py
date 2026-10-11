"""Observe only the AI Development section of Tufts department policy."""
import hashlib
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean
URL='https://engineering.tufts.edu/cs/current-students/policies-and-documentation'

def parse_policy(html,pid):
    soup=BeautifulSoup(html,'html.parser')
    if not any(clean(h.get_text())=='Policies and Documentation' for h in soup.find_all('h1')):raise ValueError('Tufts policy identity missing')
    h=next((h for h in soup.find_all('h2') if clean(h.get_text())=='Minor in AI Development'),None)
    if not h:raise ValueError('Tufts AI Development section missing')
    parts=[]
    for sibling in h.next_siblings:
        if getattr(sibling,'name',None)=='h2':break
        parts.append(sibling.get_text(' ',strip=True) if hasattr(sibling,'get_text') else str(sibling))
    value=clean(' '.join(parts))
    if len(value)<100:raise ValueError('Tufts policy body incomplete')
    return dict(id=pid,curriculum_status='partial',courses=[],requirements=[],observed_policy_sha256=hashlib.sha256(value.encode()).hexdigest(),notes=['Department policy observation does not establish precedence over the required checklist.'])
