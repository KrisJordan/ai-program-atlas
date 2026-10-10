"""Observe public RIT policy sections without recertifying a curriculum audit."""
import hashlib
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean

SPECS={
 'd015':('D01.5 University Writing Policy',['II. Writing Across the Curriculum Program Requirement for Undergraduate Programs']),
 'd011':('D01.1 Minors Policy',['I. Definition','II. Institutional parameters','III. Development / approval / administration processes']),
 'd020':('D02.0 Admission',['I. Undergraduate']),
 'd050':('D05.0 Grades',['II. Definitions','III. Pass / No Pass Option for Undergraduate Courses','VII. Repeating Courses to Raise Low Grades','VIII. Grade Point Average']),
 'd120':('D12.0 Graduation Requirements',['II. Associate and Baccalaureate Degrees','III. Catalog Requirements Under Which an Undergraduate Student Graduates']),
}


def parse_policy(html, *, pid, code):
    soup=BeautifulSoup(html,'html.parser');title,headings=SPECS[code]
    if not any(clean(h.get_text(' ',strip=True))==title for h in soup.find_all('h1')):
        raise ValueError('RIT policy identity missing or changed')
    sections={}
    for name in headings:
        found=[h for h in soup.find_all('h2') if clean(h.get_text(' ',strip=True))==name]
        if len(found)!=1:raise ValueError('RIT policy section missing or duplicated: '+name)
        # Drupal wraps each heading and policy content in its own section.
        h=found[0];container=h.parent
        while container and (len(container.find_all('h2'))!=1 or len(clean(container.get_text(' ',strip=True)))<=len(name)):
            container=container.parent
        if not container:raise ValueError('RIT policy body missing: '+name)
        value=clean(container.get_text(' ',strip=True))
        if len(value)<len(name)+40:raise ValueError('RIT policy section empty: '+name)
        sections[name]=hashlib.sha256(value.encode()).hexdigest()
    return dict(id=pid,curriculum_status='partial',courses=[],requirements=[],observed_policy_sections=sections,
                notes=['Observed policy-section content hashes only; changed policy text requires reviewer interpretation. No audit or inferred requirement is emitted.'])


def register(pid,sources,parsers, *, minor=False):
    for code in (['d011','d020','d050','d120'] if minor else ['d020','d050','d120','d015']):
        url='https://www.rit.edu/policies/'+code
        if url not in sources:sources.append(url)
        parsers[url]=lambda html,code=code:parse_policy(html,pid=pid,code=code)
