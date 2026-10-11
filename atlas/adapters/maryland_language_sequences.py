"""Dated ARHU sequence observations from the ordinary public PDF viewer text.

Input must contain the visible page-one text, with its original row line breaks.
A Drive viewer shell without rendered document text fails closed. This parser
neither downloads the PDF nor turns its dated policy into a current audit.
"""
import re
from atlas.adapters.cmu_bs.common import course
from atlas.adapters.national_curriculum_common import rule

URL = 'https://drive.google.com/file/d/1Lk076FdbP8aXNku8kzuKZkkMnQeEZGkI/view?usp=sharing'
PREFIXES = ('ARAB', 'CHIN', 'FOLA', 'FREN', 'GERS', 'GREK', 'HEBR', 'ITAL',
            'JAPN', 'KORA', 'LATN', 'PERS', 'PORT', 'RUSS', 'SPAN', 'JWST')
# Course identities and terminal styling are tied to the visually reviewed edition.
# Credits are extracted, but any changed identity/order requires a fresh visual review.
REVIEWED = {
    'ARAB': ('106 107 206 207', '101 102'), 'CHIN': ('105', '101 102 103'),
    'FOLA': ('138_ 139_ 148_ 149_', '158_ 159_'), 'FREN': ('103 203',),
    'GERS': ('103 203',), 'GREK': ('101 102 201', '111 112 211 212'),
    'HEBR': ('106 107',), 'ITAL': ('103 203', '121 122'), 'JAPN': ('101 102',),
    'KORA': ('211 212', '101 102 201 202'), 'LATN': ('101 102 201', '120 201'),
    'PERS': ('101 102',), 'PORT': ('103 203',), 'RUSS': ('101 102', '111 112 102'),
    'SPAN': ('103 203',), 'JWST': ('281 282',),
}
QUALIFIERS = {('ARAB', 1): 'Egyptian Colloquial', ('ARAB', 2): 'Modern Standard Arabic',
              ('CHIN', 1): 'Heritage Speakers', ('CHIN', 2): 'Non-Heritage Speakers',
              ('GREK', 1): 'Ancient', ('GREK', 2): 'Modern'}
TOKENS = re.compile(r'(\d{3}\s*_?)\s*\((\d+)\)')


def parse(text, *, pid):
    # AX captures are supported; UI chrome is excluded by the document heading.
    text = re.sub(r'^\s*\d+ text ', '', text, flags=re.M)
    start = text.find('COLLEGE OF ARTS AND HUMANITIES (ARHU) GLOBAL ENGAGEMENT REQUIREMENT')
    end = text.find('NATIVE/HERITAGE PROFICIENCY EXEMPTION', start)
    if start < 0 or end < 0:
        raise ValueError('Visible ARHU document text missing; viewer shell is insufficient')
    body = text[start:end]
    flat = ' '.join(body.split())
    for marker in ('September 2023', 'All students pursuing a B.A. degree',
                   'Credits are in parentheses', 'bold face and underlined',
                   'final sequence course cannot be taken Pass/Fail; minimum grade = D-',
                   'must take prior to course registration',
                   'American Sign Language', 'cannot guarantee course availability',
                   'must meet with an ARHU advisor'):
        if marker not in flat:
            raise ValueError('Dated language rule changed: ' + marker)
    sid = pid + '-language-sequences-2023'
    parent = sid + '-reference'
    rules = [rule(parent, 'September 2023 one-language sequence reference', sid,
                  parent=pid+'-policy-arhu-language', kind='note', category='human_context',
                  summary='Dated reference linked by the current ARHU page. These are placement-dependent alternative language paths, not courses all students must take. Bold/underlined terminal courses were visually reviewed. The PDF does not resolve the current two-language option or its conflict with current Pass-Fail wording.')]
    rules.append(rule(sid+'-conditions', 'Dated language grading, placement and ASL conditions', sid,
                      parent=parent, kind='note', category='human_context',
                      summary='September 2023 PDF requires D- or better and forbids Pass/Fail for the final sequence course; current college policy permits eligible language study Pass-Fail, so applicability needs clarification. Asterisked languages require online placement before registration; other languages require department consultation. ASL may qualify, but availability is not guaranteed and ARHU advising is required. No ASL course pool is published here.'))
    courses = {}
    seen = []
    prefix = None
    number = 0
    placement = False
    rows = body.split('Arabic (ARAB)', 1)
    if len(rows) != 2:
        raise ValueError('Language table start missing')
    table = 'Arabic (ARAB)' + rows[1].split('Please note:', 1)[0]
    for line in table.splitlines():
        line = line.strip()
        if not line or line.startswith('[Formerly'):
            continue  # Historical Arabic renumbering is not a current course pool.
        match = re.match(r'(\*?)([A-Za-z ]+)\s+\(([A-Z]+)\)\s*(.*)', line)
        if match:
            placement, language, prefix, line = match.groups()
            if prefix not in PREFIXES or prefix in seen:
                raise ValueError('Unexpected language row identity')
            seen.append(prefix)
            number = 0
        if prefix is None:
            raise ValueError('Unidentified language sequence')
        number += 1
        line = re.sub(r'\s+or$', '', line)
        qualifier = line.split(':', 1)[0] if ':' in line else ''
        if qualifier:
            line = line.split(':', 1)[1].strip()
        heritage = '{heritage speakers only}' in line
        line = line.replace('{heritage speakers only}', '').strip()
        tokens = TOKENS.findall(line)
        remainder = TOKENS.sub('', line)
        if not tokens or re.sub(r'(and|[\s→])', '', remainder):
            raise ValueError('Changed sequence grammar requires review: ' + line)
        signature = ' '.join(re.sub(r'\s', '', code) for code, _ in tokens)
        if number > len(REVIEWED[prefix]) or signature != REVIEWED[prefix][number-1]:
            raise ValueError('Sequence identities/order changed; visually review terminal styling')
        if qualifier != QUALIFIERS.get((prefix, number), '') or heritage != (prefix == 'KORA' and number == 1):
            raise ValueError('Sequence applicability changed')
        if bool(placement) != (prefix not in {'ARAB', 'FOLA', 'GREK', 'LATN', 'JWST'}):
            raise ValueError('Placement designation changed')
        if ('and' in line) != (prefix == 'CHIN' and number == 2):
            raise ValueError('Terminal conjunction changed')
        codes = [prefix + re.sub(r'\s', '', code) for code, _ in tokens]
        wildcard = any('_' in code for code in codes)
        ids = []
        if not wildcard:
            for code, (_, credits) in zip(codes, tokens):
                c = course(code, None, sid, URL, institution='umd', category='human_context',
                           credits=int(credits), unit='semester_hours')
                if c['id'] in courses and courses[c['id']]['credits'] != c['credits']:
                    raise ValueError('Conflicting sequence course credits')
                courses[c['id']] = c
                ids.append(c['id'])
        terminal = ' and '.join(codes[-2:]) if 'and' in line else codes[-1]
        chain = ' → '.join(f'{code} ({credits} credits)' for code, (_, credits) in zip(codes,tokens))
        if 'and' in line:
            chain = chain.rsplit(' → ', 1)[0] + ' and ' + f'{codes[-1]} ({tokens[-1][1]} credits)'
        summary = f'September 2023 reference: {chain}. Terminal requirement: {terminal}. Entry depends on placement; preceding courses are not universally required.'
        if placement:
            summary += ' Online placement is required before registration.'
        else:
            summary += ' Consult the department about registration/placement.'
        if heritage:
            summary += ' This path is for heritage speakers only.'
        if wildcard:
            summary += ' Underscores are source course-suffix placeholders; no concrete course identity or finite offering pool is inferred.'
        title = language.strip() + (': '+qualifier if qualifier else '') + f' — path {number} (September 2023)'
        rules.append(rule(sid+f'-{prefix.lower()}-{number}', title, sid, ids,
                          parent=parent, kind='note', summary=summary, category='human_context'))
    if tuple(seen) != PREFIXES or len(rules) != 2 + sum(map(len, REVIEWED.values())):
        raise ValueError('Language inventory changed or incomplete')
    return {'id': pid, 'requirements': rules, 'courses': list(courses.values())}
