"""Source-specific observation of literacy minor declaration and university policy."""
import hashlib
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean
DECLARATION='https://advising.tulane.edu/resources/declarations'
UNIVERSITY='https://catalog.tulane.edu/university/'

def parse_declaration(html,pid):
    soup=BeautifulSoup(html,'html.parser')
    if not any(clean(h.get_text())=='Major or Minor Declarations' for h in soup.find_all('h1')):raise ValueError('Tulane declaration identity missing')
    button=next((b for b in soup.find_all('button') if clean(b.get_text())=='Declaring All Other Programs'),None)
    listing=button.parent.find('ol') if button else None
    if not listing or len(listing.find_all('li',recursive=False))!=3:raise ValueError('Tulane declaration steps changed')
    value=clean(listing.get_text(' ',strip=True))
    if len(value)<100:raise ValueError('Tulane declaration body incomplete')
    return dict(id=pid,curriculum_status='partial',courses=[],requirements=[],observed_policy_sha256=hashlib.sha256(value.encode()).hexdigest())

def parse_university(html,pid):
    soup=BeautifulSoup(html,'html.parser')
    if not any(clean(h.get_text())=='The University' for h in soup.find_all('h1')):raise ValueError('Tulane university identity missing')
    sections={}
    for name in ['Credit-Hour','Curriculum Effective Date']:
        h=next((h for h in soup.find_all('h2') if clean(h.get_text())==name),None)
        if not h:raise ValueError('Tulane university section missing: '+name)
        values=[]
        for sibling in h.next_siblings:
            if getattr(sibling,'name',None)=='h2':break
            values.append(sibling.get_text(' ',strip=True) if hasattr(sibling,'get_text') else str(sibling))
        value=clean(' '.join(values))
        if len(value)<50:raise ValueError('Tulane university section incomplete')
        sections[name]=hashlib.sha256(value.encode()).hexdigest()
    return dict(id=pid,curriculum_status='partial',courses=[],requirements=[],observed_policy_sections=sections)
