"""Find unambiguous, institution-scoped titles for codes in source prose.

This annotates references; it does not parse prerequisite logic or infer identities.
"""
import re
from collections import defaultdict


def code_key(code):
    return re.sub(r'\s+', '', code or '').casefold()


def title_index(programs):
    candidates = defaultdict(list)
    for program in programs:
        for course in program.get('courses', []):
            if course.get('code') and course.get('name') and any(c.isdigit() for c in course['code']):
                record = dict(course, program_id=program['id'])
                key = code_key(course['code'])
                candidates[key].append(record)
                # MIT's explicit joint-subject suffix is notation, not a new guessed code.
                if key.endswith('[j]'):
                    candidates[key[:-3]].append(record)
    return {key: sorted(rows, key=lambda c: (c['program_id'], c['id']))[0]
            for key, rows in candidates.items()
            if len({c['name'].strip().casefold() for c in rows}) == 1}


def reference_matcher(program, institution_programs=()):
    index = title_index(institution_programs)
    # Current-program evidence wins; conflicting local names remain unresolved.
    local = title_index([program])
    local_keys = {code_key(c.get('code')) for c in program.get('courses', []) if c.get('code')}
    local_keys |= {key[:-3] for key in local_keys if key.endswith('[j]')}
    for key in local_keys:
        index.pop(key, None)
    index.update(local)
    if not index:
        return None, {}
    patterns = [r'\s*'.join(re.escape(ch) for ch in key) for key in sorted(index, key=lambda key: (-len(key), key))]
    return re.compile(r'(?<![\w.])(?:' + '|'.join(patterns) + r')(?![\w.])', re.I), index


def referenced_courses(text, matcher):
    pattern, index = matcher
    if not pattern or not text:
        return []
    found = []
    seen = set()
    for match in pattern.finditer(text):
        course = index[code_key(match.group())]
        identity = (course['program_id'], course['id'])
        if identity not in seen:
            found.append(course)
            seen.add(identity)
    return found
