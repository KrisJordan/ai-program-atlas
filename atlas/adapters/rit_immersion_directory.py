"""Observe the public RIT route directory without manufacturing branch rules."""
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean

URL = 'https://www.rit.edu/study/immersions-and-minors'
TITLE = 'Rochester Institute of Technology Immersions and Minors'

def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    if soup.select('input[type="password"]'):
        raise ValueError('Login page is not a route directory')
    main = soup.find('main')
    if not main or not any(clean(h.get_text(' ', strip=True)) == TITLE for h in main.find_all('h1')):
        raise ValueError('RIT directory identity missing')
    result = {}
    for a in main.select('a[href]'):
        url = urljoin(URL, a['href'])
        parts = urlsplit(url)
        if parts.netloc != 'www.rit.edu' or not parts.path.startswith('/study/') or not parts.path.endswith('-immersion') or parts.query or parts.fragment:
            continue
        title = clean(a.get_text(' ', strip=True))
        if not title.endswith(' Immersion'):
            raise ValueError('Immersion link title missing')
        if url in result and result[url]['title'] != title:
            raise ValueError('Conflicting directory identity')
        result[url] = {'id': parts.path.rsplit('/', 1)[1], 'title': title, 'url': url}
    if not result:
        raise ValueError('No actual immersion links')
    return {'observed_routes': list(result.values())}
