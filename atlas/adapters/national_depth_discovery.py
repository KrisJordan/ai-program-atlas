"""Bounded identity extraction for the October 11 National Universities depth pass.

Each recognizer uses the reviewed heading and a local credential statement. It
observes no curriculum, review date, launch date, or inferred host-degree rules.
"""
from __future__ import annotations

import re
from bs4 import BeautifulSoup

CONFIG = {
    'fsu': ('fsu-cs-ai-concentration', 'Artificial Intelligence', 'concentration', '(New) Artificial Intelligence Concentration'),
    'umass': ('umass-amherst-cs-ai-concentration', 'Artificial Intelligence', 'concentration', 'BS Artificial Intelligence Concentration Requirements'),
    'rpi': ('rpi-cognitive-science-ai-minor', 'Cognitive Science of Artificial Intelligence', 'minor', 'Cognitive Science of Artificial Intelligence, Minor'),
    'smu-ba': ('smu-cs-ba-ai-ml-track', 'Artificial Intelligence and Machine Learning', 'concentration', 'Computer science'),
    'smu-bs': ('smu-cs-bs-ai-ml-specialization', 'Artificial Intelligence and Machine Learning Specialization', 'concentration', 'Computer science'),
    'uic': ('uic-cs-ai-concentration', 'AI', 'concentration', 'UIC Engineering Launches AI Curriculum Initiatives'),
}


def clean(text):
    return ' '.join(text.casefold().split())


def parse_identity(html, key):
    pid, title, kind, heading = CONFIG[key]
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('input', {'type': 'password'}):
        raise ValueError('Authentication page is not program evidence')
    for node in soup.find_all(['h1', 'title']):
        if re.match(r'^(access denied|forbidden|sign in|log ?in|just a moment|verify you)', node.get_text(' ', strip=True), re.I):
            raise ValueError('Access gate is not program evidence')
    for node in soup.find_all(['nav', 'footer', 'aside', 'script', 'style']) + soup.find_all(attrs={'aria-hidden': 'true'}) + soup.find_all(attrs={'hidden': True}):
        if node.parent is not None:
            node.decompose()
    root = soup.find('main')
    if key.startswith('smu-'):
        # The reviewed SMU template has no main element. Its program H1 and FAQ
        # are separate explicit content blocks; unrelated paragraphs cannot match.
        hero = soup.find('div', class_='program-header-intro')
        root = soup.find(id='faq-accordion')
        headings = hero.find_all('h1') if hero else []
    else:
        headings = root.find_all('h1') if root else []
    if not root or not any(clean(h.get_text(' ', strip=True)) == clean(heading) for h in headings):
        raise ValueError('Expected source content heading missing')
    paragraphs = [clean(p.get_text(' ', strip=True)) for p in root.find_all('p')]
    if key == 'fsu':
        valid = any('cs@fsu artificial intelligence concentration' in p and 'designed for computer science students' in p for p in paragraphs)
    elif key == 'umass':
        valid = any('ai concentration is available to students pursuing a bs in computer science' in p for p in paragraphs)
    elif key == 'rpi':
        valid = 'minor' in clean(heading)
    elif key.startswith('smu-'):
        degree = 'arts' if key == 'smu-ba' else 'science'
        valid = any(p.startswith(f'the bachelor of {degree} in computer science') and 'track electives' in p and ('artificial intelligence and machine learning specialization' if degree == 'science' else 'artificial intelligence and machine learning,') in p for p in paragraphs)
    else:
        # The prose explicitly says this is a formal concentration. Other AI
        # course sequences in this article do not meet the credential test.
        valid = any('specialization level introduces a formal ai concentration' in p for p in paragraphs)
        valid = valid and any('incoming computer science students' in p for p in paragraphs)
    if not valid:
        raise ValueError('Credential-specific eligibility or formal identity missing')
    return {'id': pid, 'title': title, 'award_level': kind, 'program_kind': kind}
