"""Conservative identity observations for directory-verified, unextracted programs.

This does not load or replay seed records. The calling adapter supplies an expected
identity and accepted source spellings; every returned identity field requires
matching visible program content. Changes queue for review rather than silently
updating curated data.
"""
from __future__ import annotations

import re
import unicodedata

from bs4 import BeautifulSoup


def normalized(value: str) -> str:
    value = unicodedata.normalize('NFKC', value).casefold().replace('&', ' and ')
    return ' '.join(re.sub(r'[^\w]+', ' ', value).split())


def _contains(text: str, value: str) -> bool:
    return f' {normalized(value)} ' in f' {normalized(text)} '


def _context(node) -> str:
    """Prefer a program card/list row; otherwise a bounded heading section."""
    for parent in node.parents:
        if parent.name in ('li', 'tr') or ('card' in ' '.join(parent.get('class', []))):
            text = parent.get_text(' ', strip=True)
            if len(text) <= 2000:
                return text
        if parent.name in ('main', 'article', 'body'):
            break
    parts = [node.get_text(' ', strip=True)]
    # Heading sections end at the next heading of equal or greater rank. This
    # avoids accidentally borrowing a different program's award from a directory.
    rank = int(node.name[1]) if re.fullmatch(r'h[1-6]', node.name or '') else 6
    for sibling in node.next_siblings:
        name = getattr(sibling, 'name', None)
        if name and re.fullmatch(r'h[1-6]', name) and int(name[1]) <= rank:
            break
        parts.append(sibling.get_text(' ', strip=True) if name else str(sibling))
        if sum(map(len, parts)) >= 2000:
            break
    return ' '.join(parts)[:2000]


def parse_identity(html: str, *, program_id: str, title: str, award: str,
                   kind: str, aliases: tuple[str, ...] = (),
                   award_terms: tuple[str, ...] = ()) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('input', {'type': 'password'}):
        raise ValueError('Password-protected content is not program evidence')
    page_heading = soup.find(['h1', 'title'])
    if page_heading and re.search(r'^(sign in|log ?in|access denied|just a moment|verify you)',
                                  page_heading.get_text(' ', strip=True), re.I):
        raise ValueError('Authentication or access page is not program evidence')
    for node in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']) + soup.find_all(attrs={'aria-hidden': 'true'}):
        node.decompose()
    # Catalogs may use #content instead of semantic main. Without a recognized
    # content root only explicit headings/links count, never arbitrary body text.
    root = (soup.find('main') or soup.find(attrs={'role': 'main'}) or soup.find('article')
            or soup.find(id='content') or soup.find(id='main-content') or soup)
    expected = (title,) + aliases
    candidates = [node for node in root.find_all(['h1','h2','h3','h4','h5','h6','a'])
                  if any(_contains(node.get_text(' ', strip=True), t) for t in expected)]
    if not candidates:
        raise ValueError('Expected program title missing from content headings or links')
    default_terms = {
        'BS': ('Bachelor of Science', 'BS', 'B.S.'),
        'BA': ('Bachelor of Arts', 'BA', 'B.A.'),
        'BSE': ('Bachelor of Science in Engineering', 'BS in Engineering', 'BSE'),
        'BSAI': ('Bachelor of Science in Artificial Intelligence', 'BSAI'),
        'minor': ('minor',), 'concentration': ('concentration',),
    }
    terms = award_terms or default_terms.get(award, ())
    if not terms:
        raise ValueError('Explicit source award terms required for nonstandard award')
    for node in candidates:
        context = _context(node)
        if not any(_contains(context, term) for term in terms):
            continue
        if kind in ('minor', 'concentration') and not _contains(context, kind):
            continue
        return {'id': program_id, 'title': title, 'award_level': award, 'program_kind': kind}
    raise ValueError('Program title found, but local award/kind evidence is missing')
