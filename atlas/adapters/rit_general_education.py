"""Observe public RIT general-education and announcement pages for review."""
import hashlib
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean

SPECS={
 'https://www.rit.edu/policies/d014':('D01.4 General Education Framework',['II. Policy Statement on Requirements']),
 'https://www.rit.edu/generaleducation/general-education-degree-requirements':('General Education Degree Requirements',['General Education Guidelines for Bachelor of Science (BS)','Use of Program Courses for General Education Requirements']),
 'https://www.rit.edu/generaleducation/immersions':('Immersions',[]),
 'https://www.rit.edu/study/undergraduate-graduation-requirements':('Rochester Institute of Technology Undergraduate Graduation Requirements',['General Requirements','Wellness Education Requirement']),
 'https://www.rit.edu/news/rit-launches-hands-bachelor-science-degree-artificial-intelligence':('RIT launches hands-on Bachelor of Science degree in artificial intelligence',[]),
}


def parse_page(html, *, pid, url):
    soup=BeautifulSoup(html,'html.parser');title,headings=SPECS[url]
    if not any(clean(h.get_text(' ',strip=True))==title for h in soup.find_all('h1')):
        raise ValueError('RIT source identity missing or changed')
    main=soup.find('main')
    if not main:raise ValueError('RIT main body missing')
    for nav in main.find_all('nav'):nav.decompose()
    for name in headings:
        if not any(clean(h.get_text(' ',strip=True))==name for h in main.find_all(['h2','h3'])):
            raise ValueError('RIT source section missing: '+name)
    value=clean(main.get_text(' ',strip=True))
    if len(value)<len(title)+100:raise ValueError('RIT source body incomplete')
    return dict(id=pid,curriculum_status='partial',courses=[],requirements=[],observed_source_content_sha256=hashlib.sha256(value.encode()).hexdigest(),
                notes=['Source body observation only; review required for requirement applicability, dates and operational status.'])


def register(pid,sources,parsers):
    for url in SPECS:
        if url not in sources:sources.append(url)
        parsers[url]=lambda html,url=url:parse_page(html,pid=pid,url=url)
