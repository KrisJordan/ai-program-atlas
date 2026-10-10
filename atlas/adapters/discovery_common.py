"""Conservative, source-scoped identity observations; never replay curated records."""
from __future__ import annotations

import re
import unicodedata

from bs4 import BeautifulSoup, NavigableString, Tag


def normalized(value: str) -> str:
    value = unicodedata.normalize('NFKC', value).casefold().replace('&', ' and ')
    # Catalog award abbreviations are equivalent with or without periods.
    value = re.sub(r'\b(?:[a-z]\.){2,}', lambda m: m.group().replace('.', ''), value)
    return ' '.join(re.sub(r'[^\w]+', ' ', value).split())


def _contains(text: str, value: str) -> bool:
    return f' {normalized(value)} ' in f' {normalized(text)} '


def _context(node, *, inherit_section_award=False) -> str:
    """Read one entry, or a heading's DOM section even across layout wrappers."""
    entry = node if node.name in ('li', 'tr') else None
    if entry is None:
        for parent in node.parents:
            if parent.name in ('li', 'tr') or ('card' in ' '.join(parent.get('class', []))):
                if len(parent.get_text(' ', strip=True)) <= 2000:
                    entry = parent
                    break
            if parent.name in ('main', 'article', 'body'):
                break
    if entry is not None:
        text = entry.get_text(' ', strip=True)
        if inherit_section_award:
            # Opt-in for a verified directory: heading immediately preceding the
            # entry's list, never an unrelated earlier program's heading.
            listing = entry.find_parent(['ul', 'ol'])
            if listing:
                previous = listing.find_previous_sibling()
                if previous and re.fullmatch(r'h[1-6]', previous.name or ''):
                    text = previous.get_text(' ', strip=True) + ' ' + text
        return text[:2000]
    if not re.fullmatch(r'h[1-6]', node.name or ''):
        return node.get_text(' ', strip=True)[:2000]
    parts = []
    for element in node.next_elements:
        if isinstance(element, Tag) and re.fullmatch(r'h[1-6]', element.name or ''):
            break
        if isinstance(element, NavigableString):
            parts.append(str(element))
            if sum(map(len, parts)) >= 2000:
                break
    return ' '.join(parts)[:2000]


def parse_identity(html: str, *, program_id: str, title: str, award: str,
                   kind: str, aliases: tuple[str, ...] = (),
                   award_terms: tuple[str, ...] = (),
                   identity_scopes: tuple[str, ...] = (),
                   inherit_section_award: bool = False) -> dict:
    """Scopes are reviewed page-specific evidence blocks, not broad body fallbacks."""
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('input', {'type': 'password'}):
        raise ValueError('Password-protected content is not program evidence')
    page_heading = soup.find(['h1', 'title'])
    if page_heading and re.search(r'^(sign in|log ?in|access denied|just a moment|verify you)',
                                  page_heading.get_text(' ', strip=True), re.I):
        raise ValueError('Authentication or access page is not program evidence')
    # A header inside the content is commonly the program's own H1. Global
    # navigation, hidden elements and sidebars remain excluded, including inside
    # explicitly configured selectors.
    for node in soup.find_all(['script', 'style', 'nav', 'footer', 'aside']) + soup.find_all(attrs={'aria-hidden': 'true'}):
        if node.parent is not None:
            node.decompose()
    selected = []
    for scope in identity_scopes:
        if scope == 'courseleaf-title':
            block = soup.find(id='site-title')
            selected.extend(block.find_all('h1') if block else [])
        elif scope == 'miami-title':
            block = soup.find(id='content-container')
            selected.extend(block.find_all('h1') if block else [])
        elif scope == 'cornell-program-hero':
            for block in soup.find_all(class_='hero-banner--program-detail'):
                selected.extend(block.find_all(class_='hero-banner-content'))
        elif scope == 'stevens-program-hero':
            selected.extend(soup.find_all('div', class_=lambda c: c and '_slug__hero-wrapper' in c))
        elif scope == 'maryland-pathway-text':
            for pathway in soup.find_all('umd-element-pathway'):
                for block in pathway.find_all(attrs={'slot': 'text'}):
                    selected.extend(block.find_all('p'))
        else:
            raise ValueError(f'Unknown reviewed identity scope: {scope}')
    for node in list(soup.find_all('header')):
        if not node.find_parent(['main', 'article']) and not any(n is node or node in n.parents for n in selected):
            node.decompose()
    root = (soup.find('main') or soup.find(attrs={'role': 'main'}) or soup.find('article')
            or soup.find(id='content') or soup.find(id='main-content') or soup)
    expected = (title,) + aliases
    nodes = root.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'li']) + selected
    candidates = [node for node in nodes if node.parent is not None
                  and not (node.name == 'li' and node.find(['ul', 'ol']))
                  and any(_contains(node.get_text(' ', strip=True), t) for t in expected)]
    if not candidates:
        raise ValueError('Expected program title missing from scoped content headings or entries')
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
        contexts = [_context(node, inherit_section_award=inherit_section_award)]
        if node.name == 'p':
            # Explicitly selected prose can contain multiple degrees; the award
            # must occur in the same sentence as the expected program identity.
            contexts = [s for s in re.split(r'(?<=[.!?])\s+', contexts[0])
                        if any(_contains(s, t) for t in expected)]
        for context in contexts:
            if not any(_contains(context, term) for term in terms):
                continue
            if kind in ('minor', 'concentration') and not _contains(context, kind):
                continue
            return {'id': program_id, 'title': title, 'award_level': award, 'program_kind': kind}
    raise ValueError('Program title found, but local award/kind evidence is missing')
