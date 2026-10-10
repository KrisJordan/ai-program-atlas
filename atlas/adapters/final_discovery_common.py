"""Validate source-specific identity claims on already reviewed official pages."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.discovery_common import normalized


def parse_claims(html, *, program_id, title, award, kind, heading, claims):
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('input', attrs={'type': 'password'}):
        raise ValueError('Password page is not program evidence')
    if any(re.search(r'^(log ?in|sign in|access denied|just a moment|javascript is disabled)',
                     n.get_text(' ', strip=True), re.I) for n in soup.find_all(['h1','title'])):
        raise ValueError('Access challenge is not program evidence')
    for node in soup.find_all(['nav','header','footer','aside','script','style']):
        node.decompose()
    root = (soup.find('main') or soup.find(attrs={'role':'main'}) or soup.find('article')
            or soup.find(id='content') or soup.find(id='main-content') or soup)
    if not any(normalized(heading) in normalized(n.get_text(' ', strip=True))
               for n in root.find_all(['h1','h2','h3','h4','h5','h6'])):
        raise ValueError('Expected source content heading missing')
    body = ' '+normalized(root.get_text(' ', strip=True))+' '
    for claim in claims:
        if ' '+normalized(claim)+' ' not in body:
            raise ValueError('Required program identity or formal classification claim missing')
    # Only identity fields are observed; there is no seed read or date generation.
    return dict(id=program_id,title=title,award_level=award,program_kind=kind)
