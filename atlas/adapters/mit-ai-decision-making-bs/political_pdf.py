"""Offline parser for the explicitly linked, dated Political Science subfield PDF.

Input is text extracted from the public PDF, not a seed or hand-built subject
list. PDFKit's ti/tt ligature mapping is corrected only under the observed broken
heading fingerprint, and only in alphabetic words. The three rendered source
pages were visually checked. No network or degree-completeness side effects.
"""
import re
from atlas.adapters.national_curriculum_common import clean, course, rule

PID = 'mit-ai-decision-making-bs'
SID = PID + '-hass-political-subfields'
URL = 'https://polisci.mit.edu/files/ps/imce/undergraduate/concentration/classes_subfields%20Updated%20July%2010%202024.pdf'
AREAS = ['Political Philosophy - Social Theory', 'Political Economy', 'American Politics', 'Public Policy', 'International Relations - Security Studies', 'Comparative Politics - Political Development - Area Studies', 'Models and Methods']


def parse_text(text):
    if text.startswith('Poli%cal Science Classes in Subfields'):
        text = re.sub(r'(?<=[A-Za-z])[%4](?=[A-Za-z])', 'ti', text)
        text = re.sub(r'(?<=[A-Za-z])Z(?=[A-Za-z])', 'tt', text)
    lines = [clean(line) for line in text.splitlines() if clean(line)]
    if not lines or lines[0] != 'Political Science Classes in Subfields':
        raise ValueError('Political Science PDF heading changed')
    observed, groups, rows = [], {}, []
    area = None
    for line in lines[1:]:
        if line in AREAS:
            observed.append(line)
            area = line
            groups[area] = []
        else:
            match = re.fullmatch(r'(17\.[A-Z0-9]+)\s*-\s*(.+)', line)
            if match:
                if area is None:
                    raise ValueError('PDF subject before area')
                rows.append([area, match[1], match[2]])
            elif rows and rows[-1][2].count('(') > rows[-1][2].count(')'):
                rows[-1][2] += ' ' + line
            else:
                raise ValueError('Unrecognized PDF line: ' + line[:80])
    if observed != AREAS:
        raise ValueError('Political Science subfield structure changed')
    prefix = 'mit-ai-hass-political-subfields'
    courses = {}
    restrictions = []
    for area, code, tail in rows:
        annotation = re.search(r'\((.+)\)', tail)
        name = tail.split(' (')[0]
        credits = 9 if annotation and '9 unit IAP version' in annotation[1] else None
        c = course(prefix, code, name, SID, URL, credits=credits, unit='units', category='human_context')
        if c['id'] in courses and courses[c['id']]['name'] != name:
            raise ValueError('Conflicting PDF subject titles')
        courses[c['id']] = c
        groups[area].append(c['id'])
        if annotation:
            restrictions.append((c, annotation[1].rstrip(')')))
    if any(not pool for pool in groups.values()):
        raise ValueError('Empty Political Science subfield')
    rules = [rule(prefix, 'Dated Political Science subfield reference', SID, kind='note', summary='This public PDF is linked by the current concentration page. Its URL labels an update of July 10, 2024; the rendered document itself has no printed date. The seven groups are a dated planning reference, not seven mandatory areas or a guarantee of current offerings or enrollment permission. The conditional three-subject advisor-approved concentration rule remains controlling.')]
    for i, (area, pool) in enumerate(groups.items()):
        rules.append(rule(prefix + '-area-' + str(i + 1), area, SID, pool, parent=prefix, kind='note', summary='Dated subject-by-subfield reference; courses may appear in multiple subfields. This is not an additive all-course requirement.'))
    seen = set()
    for c, annotation in restrictions:
        if c['id'] in seen:
            continue
        seen.add(c['id'])
        if c['code'] == '17.307' and 'open only to students admitted to the MIT Washington Summer Internship Program' in annotation:
            summary = '17.307 is open only to students admitted to the MIT Washington Summer Internship Program.'
        elif c['code'] == '17.567' and '9 unit IAP version for students accepted into the MISTI Israel Program' in annotation:
            summary = 'The dated reference identifies 17.567 as a nine-unit IAP version for students accepted into the MISTI Israel Program. It does not establish a current IAP offering or permit every student to enroll.'
        else:
            raise ValueError('Unreviewed PDF enrollment restriction')
        rules.append(rule(prefix + '-condition-' + c['code'].replace('.', '-'), 'Conditional enrollment: ' + c['code'], SID, [c['id']], parent=prefix, kind='note', summary=summary))
    return dict(id=PID, courses=list(courses.values()), requirements=rules)
