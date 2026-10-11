"""Optional economics, philosophy/ethics and political-science HASS plans."""
import re
from atlas.adapters.national_curriculum_common import content, clean, course, rule, require_phrases

PID = 'mit-ai-decision-making-bs'
ECON = 'https://economics.mit.edu/academic-programs/undergraduate-program/studying-economics-mit/concentrating-economics'
PHIL = 'https://philosophy.mit.edu/undergraduate/'
POLITICS = 'https://polisci.mit.edu/undergraduate/concentration'


def optional(prefix, title, sid):
    return rule(prefix, 'Optional HASS field: ' + title, sid, kind='note', summary='This field plan applies only when selected for the degree’s HASS concentration. Generic registrar HASS/grading/overlap and advisor-approval policies remain applicable. These are not additional AI-major subjects.')


def _accordion(root, title):
    h = root.find(lambda n: n.name == 'h3' and clean(n.get_text(' ', strip=True)) == title)
    if h is None or 'accordion' not in h.parent.get('class', []):
        raise ValueError('Economics concentration accordion missing')
    return h.parent


def parse_economics(html):
    root = content(html, 'Minor and Concentrations')
    sid = PID + '-hass-economics'
    courses, rules = {}, []
    for key, name in [('economics', 'Economics'), ('development-economics', 'Development Economics')]:
        pane = _accordion(root, 'Concentration in ' + name)
        prefix = 'mit-ai-hass-' + key
        require_phrases(pane, ['three subjects', '14.01', '14.03 for 14.01', '5 on the AP Micro exam', 'primary major is Economics (14-1) or Mathematical Economics (14-2)', 'secondary major is Economics (14-1) or Mathematical Economics (14-2)', 'Computer Science, Economics, and Data Science (6-14)'])
        if key == 'economics':
            require_phrases(pane, ['and/or', 'One or two of:', 'not acceptable: 14.30, 14.32, 14.33, and 14.47', 'must take replacement subject(s) for 14.01/14.02'])
        else:
            require_phrases(pane, ['14.01 and two of 14.74, 14.75, and 14.76', 'Other advanced subjects in development economics will be considered as substitutes on request', 'can also be used toward the minor'])
        local = {}
        for li in pane.find_all('li'):
            if li.find('ul'):
                continue
            text = clean(li.get_text(' ', strip=True))
            match = re.fullmatch(r'(14\.[A-Z0-9]+(?:\[J\])?) (.+)', text)
            if match is None:
                raise ValueError('Economics subject-list format changed')
            code, tail = match.groups()
            name = re.split(r'\s*\(', tail)[0].replace('*', '').removesuffix(' and/or').strip()
            c = course(prefix, code, name, sid, ECON, unit='units', category='human_context')
            pre = re.search(r'\(Prereq\. ([^)]+)\)', tail)
            c['prerequisites'] = pre[1] if pre else None
            local[code] = c
        if key == 'economics' and not {'14.01', '14.02', '14.03'} <= local.keys():
            raise ValueError('Economics foundation/advanced structure changed')
        if key != 'economics' and not {'14.01', '14.73', '14.74', '14.75', '14.76'} <= local.keys():
            raise ValueError('Development economics route changed')
        courses.update({c['id']: c for c in local.values()})
        rules.append(optional(prefix, 'Economics' if key == 'economics' else 'Development Economics', sid))
        if key == 'economics':
            branch = prefix + '-routes'
            rules.append(rule(branch, 'Three-subject route: one or both principles subjects', sid, parent=prefix, kind='alternative', summary='Choose one complete three-subject route. Conditional AP substitution and higher-level replacement rules are below.'))
            advanced = [c['id'] for code, c in local.items() if code not in ('14.01', '14.02')]
            for count in [1, 2]:
                gid = prefix + '-route-' + str(count)
                rules.extend([
                    rule(gid, f'{count} principles and {3-count} advanced subjects', sid, parent=branch, kind='all'),
                    rule(gid + '-principles', f'Choose {count} principles subject(s)', sid, [local[c]['id'] for c in ('14.01', '14.02')], parent=gid, kind='choose_courses', count=count),
                    rule(gid + '-advanced', f'Choose {3-count} advanced subject(s)', sid, advanced, parent=gid, kind='choose_courses', count=3-count)])
            rules.append(rule(prefix + '-exclusions', 'Excluded subjects and replacement requirement', sid, parent=prefix, kind='note', summary='14.30, 14.32, 14.33 and 14.47 are not acceptable for this concentration. Department permission to skip 14.01 and/or 14.02 requires higher-level replacement subjects; it never reduces the three-subject requirement.'))
        else:
            branch = prefix + '-routes'
            rules.append(rule(branch, 'One complete three-subject development route', sid, parent=prefix, kind='alternative'))
            for usual in [True, False]:
                gid = prefix + ('-usual' if usual else '-alternative')
                rules.append(rule(gid, 'Principles, poverty and one advanced subject' if usual else 'Principles and two advanced subjects', sid, parent=branch, kind='all'))
                rules.append(rule(gid + '-required', 'Required subjects in this route', sid, [local[c]['id'] for c in (['14.01', '14.73'] if usual else ['14.01'])], parent=gid, kind='all'))
                rules.append(rule(gid + '-advanced', 'Development advanced choice', sid, [local[c]['id'] for c in ['14.74', '14.75', '14.76']], parent=gid, kind='choose_courses', count=1 if usual else 2))
            rules.append(rule(prefix + '-approval', 'Requested advanced substitutions', sid, parent=prefix, kind='note', summary='Other advanced development-economics subjects may be considered as substitutions on request. Subjects used for either economics concentration may also count toward the economics minor; the separate six-subject minor rules are not imposed on this concentration.'))
        rules.append(rule(prefix + '-ap-eligibility', 'AP substitution and primary-major eligibility', sid, parent=prefix, kind='note', summary='AP Microeconomics score 5 permits 14.03 in place of 14.01, without waiving the three-subject total. Primary majors 14-1 or 14-2 cannot select either economics concentration; secondary majors in those fields and majors in 6-14 may. No reuse of one subject to fill two concentration slots is implied.'))
        unavailable = []
        for li in pane.find_all('li'):
            if li.find('ul'):
                continue
            text = clean(li.get_text(' ', strip=True))
            if '(Not offered 26-27)' in text:
                unavailable.append(text.split(' ', 1)[0])
        if unavailable:
            rules.append(rule(prefix + '-offering-annotation', 'Published 2026–27 availability annotations', sid, parent=prefix, kind='note', summary='The concentration source marks these eligible-list entries not offered in 2026–27: ' + ', '.join(unavailable) + '. Eligibility-list inclusion does not establish a current offering.'))
    return dict(id=PID, courses=list(courses.values()), requirements=rules)


def parse_philosophy(html):
    root = content(html, 'Concentration in Philosophy')
    sid = PID + '-hass-philosophy-ethics'
    p, e = root.find(id='concentrate'), root.find(id='ethicsconcentration')
    if p is None or e is None:
        raise ValueError('Philosophy/ethics field section missing')
    require_phrases(p, ['total of three (9 or 12 unit) course 24 subjects', 'no more than two', '24.00 – 24.09', '24.C40', 'well-distributed', 'One philosophy subject taught at MIT’s Concourse Program', 'registers for them using the other department’s subject number', 'specific MIT philosophy subject', 'only if approved by the philosophy transfer credit examiner', 'Non-HASS subjects cannot be counted', 'Both forms are reviewed and approved'])
    pp, ep = 'mit-ai-hass-philosophy', 'mit-ai-hass-ethics'
    rules = [optional(pp, 'Philosophy', sid),
        rule(pp + '-three', 'Three nine- or twelve-unit philosophy subjects', sid, parent=pp, kind='choose_courses', count=3, summary='Select three HASS Course 24 philosophy subjects worth nine or twelve units each; this is an open subject criterion, not an absent finite pool. The advisor must judge the plan well distributed.'),
        rule(pp + '-intro', 'Introductory limit and Concourse route', sid, parent=pp, kind='note', summary='At most two subjects may be introductory, defined here as 24.00–24.09 or 24.C40; all three may instead be nonintroductory. One Concourse philosophy subject may serve as an introductory Course 24 subject.'),
        rule(pp + '-transfer', 'Cross-registration labels, transfer and approval', sid, parent=pp, kind='note', summary='A Course 24 philosophy subject may be registered under its cross-listed department. Transfer credit for a specific MIT philosophy subject counts; other external philosophy credit requires the philosophy transfer-credit examiner. Non-HASS subjects are excluded. Both proposal and completion forms require concentration-advisor approval.')]
    require_phrases(e, ['at least three subjects in ethics', 'at least two philosophy subjects in ethics', 'at least one of which must be at a non-introductory level', 'an elective subject in ethics', 'its number is at least 24.1', 'Full list of subjects in ethics', 'may petition the Ethics Concentration Advisor', 'Non-HASS subjects cannot be counted', 'Both forms are reviewed and approved'])
    pools = e.find_all('blockquote')
    if len(pools) != 2:
        raise ValueError('Ethics philosophy/full pool structure changed')
    courses, ids = {}, []
    printed_anomalies = []
    for pool in pools:
        pool_ids = []
        for br in pool.find_all('br'):
            br.replace_with('__ETHICS_BREAK__')
        for text in pool.get_text(' ', strip=True).split('__ETHICS_BREAK__'):
            text = clean(re.sub(r'/\s+', '/', text))
            if not text:
                continue
            match = re.fullmatch(r'([A-Z0-9./]+) (.+)', text)
            if not match or not any(char.isdigit() for char in match[1]):
                raise ValueError('Ethics subject row changed')
            code, name = match.groups()
            c = course(ep, code, name, sid, PHIL + '#ethicsconcentration', unit='units', category='human_context')
            courses[c['id']] = c
            pool_ids.append(c['id'])
            if any(re.fullmatch(r'[A-Z0-9]+\.[A-Z0-9]+', part) is None for part in code.split('/')):
                printed_anomalies.append(code)
        if not pool_ids:
            raise ValueError('Ethics option pool missing')
        ids.append(pool_ids)
    if not set(ids[0]) <= set(ids[1]):
        raise ValueError('Ethics philosophy subset missing from full list')
    nonintro = [cid for cid in ids[0] if any(re.match(r'^24\.[1-9]', code) for code in courses[cid]['code'].split('/'))]
    if not nonintro:
        raise ValueError('Ethics nonintroductory subset missing')
    rules.extend([optional(ep, 'Ethics', sid),
        rule(ep + '-philosophy', 'At least two philosophy ethics subjects', sid, ids[0], parent=ep, kind='choose_courses', count=2, summary='Select at least two listed or cross-listed philosophy ethics subjects. At least one of these must meet the nonintroductory overlay.'),
        rule(ep + '-nonintro', 'Nonintroductory philosophy ethics overlay', sid, nonintro, parent=ep, kind='choose_courses', count=1, summary='At least one of the philosophy selections must be numbered 24.1 or above, or cross-listed with such a Course 24 subject; this is within the two, not an additional fourth subject.'),
        rule(ep + '-elective', 'One additional ethics elective', sid, ids[1], parent=ep, kind='choose_courses', count=1, summary='Complete an additional ethics subject, which may but need not be philosophy. Total concentration coursework is at least three subjects.'),
        rule(ep + '-approval', 'HASS-only, petition and approved completion', sid, parent=ep, kind='note', summary='Non-HASS subjects cannot count. The Ethics Concentration Advisor must approve the proposal and may consider petitions for unlisted subjects as offerings change. The section repeats proposal/completion approval instructions using philosophy-advisor wording; it is not an independent certification of administrative clearance.')])
    if printed_anomalies:
        rules.append(rule(ep + '-printed-identities', 'Unrepaired printed registration labels', sid, parent=ep, kind='note', summary='The source prints these nonstandard labels: ' + ', '.join(dict.fromkeys(printed_anomalies)) + '. They are retained verbatim; missing punctuation or concatenated cross-list codes are not silently repaired. Advisor/catalog clarification is required before interpreting their exact registration identities.'))
    return dict(id=PID, courses=list(courses.values()), requirements=rules)


def parse_politics(html):
    root = content(html, 'Concentrate in Political Science')
    require_phrases(root, ['three-subject concentration', 'focused, cohesive grouping', 'cannot be comprised of three introductory-level subjects', 'One subject in a concentration may be taken outside', 'consult with the Concentration advisor', 'Two-digit subjects are introductory', 'recommended that it be taken first'])
    sid, prefix = PID + '-hass-political-science', 'mit-ai-hass-political-science'
    return dict(id=PID, requirements=[optional(prefix, 'Political Science', sid),
        rule(prefix + '-selection', 'Three-subject cohesive plan', sid, parent=prefix, kind='choose_courses', count=3, summary='Choose a focused, cohesive plan with the concentration advisor. It cannot consist of three introductory subjects; at most one subject may be outside Political Science. Two-digit subjects are introductory. If available in the chosen area, an introductory subject is recommended first, not required first.'),
        rule(prefix + '-subfields', 'Linked dated subfield reference', sid, parent=prefix, kind='note', summary='The department links a public subject-by-subfield PDF. Its dated reference observations are represented separately; they do not supersede this advisor-approved plan or certify current offerings.')])


SOURCE_PARSERS = {ECON: parse_economics, PHIL: parse_philosophy, POLITICS: parse_politics}
