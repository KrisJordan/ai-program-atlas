"""Guarded current descriptions; manual taxonomy judgments remain seed-only."""
import hashlib
import json
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean
from atlas.adapters.stevens_degree_course_review import PID, field

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html, code):
    entry = SPEC[code]
    root = BeautifulSoup(html, 'html.parser').select_one('article.flex-1')
    heading = root.find('h1') if root else None
    titles = [clean(h.get_text(' ', strip=True)) for h in root.select('h2')] if root else []
    if not heading or clean(heading.get_text(' ', strip=True)) != entry['source_heading'] or entry['name'] not in titles:
        raise ValueError('Stevens option course identity changed: ' + code)
    value = field(root, 'Course Description')
    if value is None or hashlib.sha256(value.encode()).hexdigest() != entry['description_digest']:
        raise ValueError('Stevens option description changed: ' + code)
    credits = field(root, 'Credits')
    if credits is None or not credits.isdigit() or int(credits) != entry['credits']:
        raise ValueError('Stevens option credits changed: ' + code)
    if entry['held']:
        # Current detail metadata cannot silently replace a conflicting GE version.
        return {'id': PID, 'courses': []}
    course = dict(id=entry['id'], code=code, name=entry['name'],
                  description=entry['description'], credits=entry['credits'],
                  credit_unit='unknown', category=entry['category'],
                  source_id=entry['source_id'], url=entry['url'])
    if entry.get('description_prerequisites'):
        course['prerequisites'] = entry['description_prerequisites']
    return {'id': PID, 'courses': [course]}


def combined(html, code, prior):
    """Keep the earlier school-of-offering rule while refining course content."""
    result = prior(html)
    observed = parse(html, code)
    updated = {c['id']: c for c in observed['courses']}
    result['courses'] = [updated.pop(c['id'], c) for c in result.get('courses', [])] + list(updated.values())
    return result


def register(sources, parsers):
    from atlas.adapters.stevens_ai_general_education import parse_graduate_course
    for code, entry in SPEC.items():
        url = entry['url']
        prior = parsers.get(url)
        if isinstance(prior, partial) and prior.func in (parse, combined) and prior.keywords.get('code') == code:
            continue
        if prior is not None:
            if not (code in ('MA 661', 'BIA 665') and isinstance(prior, partial)
                    and prior.func is parse_graduate_course and prior.keywords == {'code': code}):
                raise ValueError('Stevens option observer would replace an unknown parser: ' + url)
            parsers[url] = partial(combined, code=code, prior=prior)
        else:
            parsers[url] = partial(parse, code=code)
        if url not in sources:
            sources.append(url)
