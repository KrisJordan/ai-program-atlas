"""Exact current WPI course content, separate from degree membership and reviews."""
import hashlib
import json
from fractions import Fraction
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import text

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html, *, program_id, code):
    entry = SPEC[code]
    if program_id not in entry['program_ids']:
        raise ValueError('WPI course outside reviewed program scope')
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('main')
    heading = main.find('h1') if main else None
    if not heading or text(heading) != entry.get('heading_code', code) + ': ' + entry['name']:
        raise ValueError('WPI reviewed identity changed')
    if entry.get('catalog_heading', 'Undergraduate Catalog 2026-2027') not in text(soup):
        raise ValueError('WPI reviewed catalog version changed')
    if entry.get('main_digest') and hashlib.sha256(text(main).encode()).hexdigest() != entry['main_digest']:
        raise ValueError('WPI complete reviewed course content changed')
    desc = main.find(class_='field--name-field-description')
    rec = main.find(class_='field--name-field-recommended')
    rec = rec.find(class_='field__item') if rec else None
    units = main.find(class_='field--name-field-credits')
    units = units.find(class_='field__item') if units else None
    for value, key in [(text(desc) if desc else None, 'description_digest'), (text(rec) if rec else None, 'recommended_digest')]:
        digest = hashlib.sha256(value.encode()).hexdigest() if value is not None else None
        if digest != entry[key]:
            raise ValueError('WPI reviewed content changed: ' + code)
    if not units or text(units) != entry['units_text']:
        raise ValueError('WPI reviewed unit amount changed')
    recommended = 'Recommended background (not a mandatory prerequisite): ' + text(rec) if rec else None
    prerequisite = main.find(class_='field--name-field-pr')
    prerequisite = prerequisite.find(class_='field__item') if prerequisite else None
    if entry.get('prerequisite_digest') is not None:
        if not prerequisite or hashlib.sha256(text(prerequisite).encode()).hexdigest() != entry['prerequisite_digest']:
            raise ValueError('WPI reviewed prerequisite field changed')
        recommended = (recommended + '; ' if recommended else '') + 'Source field labeled Prerequisites: ' + text(prerequisite)
    if entry.get('description_prerequisites'):
        recommended = (recommended + '; ' if recommended else '') + 'Course eligibility: ' + entry['description_prerequisites']
    notes = ['Course-description observation only; advisory background does not add fixed or elective degree obligations.']
    if entry.get('suggested_background'):
        recommended = (recommended + '; ' if recommended else '') + 'Suggested background (advisory): ' + entry['suggested_background']
    if entry.get('credit_restriction'):
        notes.append(code + ' credit restriction: ' + entry['credit_restriction'] + ' This does not establish a cross-listed identity.')
        if not recommended or 'credit' not in recommended.lower():
            recommended = (recommended + '; ' if recommended else '') + 'Credit limitation: ' + entry['credit_restriction']
    if entry.get('audience_note'):
        notes.append(code + ' ' + entry['audience_note'])
    if entry.get('eligibility_note'):
        notes.append(code + ' ' + entry['eligibility_note'])
    if entry.get('offering_note'):
        notes.append(code + ' ' + entry['offering_note'])
    if entry.get('credit_note'):
        notes.append(code + ' ' + entry['credit_note'])
    if entry.get('referral_note'):
        notes.append(code + ' ' + entry['referral_note'])
    key = entry.get('source_key', code.lower().replace(' ','-'))
    return {'id': program_id, 'courses': [dict(id=entry.get('course_id', 'wpi-'+key), code=code,
            name=entry['name'], description=entry['description'], prerequisites=recommended,
            credits=float(Fraction(text(units))), credit_unit=entry.get('credit_unit', 'units'), category=entry['category'],
            source_id=program_id+'-course-'+key, url=entry['url'])],
            'requirements': [], 'notes': notes}


def parse_referral(html, *, program_id, code):
    """Observe the source's explicit referral without duplicating the course."""
    entry = SPEC[code]
    if program_id not in entry['program_ids']:
        raise ValueError('WPI referral outside reviewed program scope')
    main = BeautifulSoup(html, 'html.parser').find('main')
    if not main or hashlib.sha256(text(main).encode()).hexdigest() != entry['referral_main_digest']:
        raise ValueError('WPI course-description referral changed')
    return {'id': program_id, 'courses': [], 'requirements': [],
            'notes': [entry['referral_note']]}


def attach(namespace):
    pid = namespace['PROGRAM_ID']
    for code, entry in SPEC.items():
        if pid not in entry['program_ids']:
            continue
        if entry['url'] not in namespace['SOURCES']:
            namespace['SOURCES'].append(entry['url'])
        namespace['SOURCE_PARSERS'][entry['url']] = partial(parse, program_id=pid, code=code)
        if entry.get('referral_url'):
            if entry['referral_url'] not in namespace['SOURCES']:
                namespace['SOURCES'].append(entry['referral_url'])
            namespace['SOURCE_PARSERS'][entry['referral_url']] = partial(parse_referral, program_id=pid, code=code)
