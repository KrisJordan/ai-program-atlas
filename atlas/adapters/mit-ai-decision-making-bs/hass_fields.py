"""Public SHASS field plans, conditional on choosing that HASS concentration.

The listed subjects are observations, including explicitly nonexhaustive pools.
Source-specific policy guards reject changed selection rules; refreshes never
certify degree completeness or copy a reviewed seed.
"""
import re
from functools import partial
from atlas.adapters.national_curriculum_common import content, clean, course, rule, require_phrases

PID = 'mit-ai-decision-making-bs'
BASE = 'https://shass.mit.edu/for-students/undergraduate-study/'
FIELDS = {
 'african-and-african-diaspora-studies': dict(title='African and African Diaspora Studies', count=4,
  areas=['Historical Studies', 'Humanities and the Arts', 'Social Sciences'],
  markers=['take four subjects', 'consultation with the Concentration Advisor', 'This list is not exhaustive', 'not both', 'Must register for two semesters', 'combined by petition'],
  policies=[('selection', 'Advisor-approved four-subject plan', 'Choose four subjects with the concentration advisor. The published core list is not exhaustive: the advisor may count relevant former offerings and variable-topic subjects. At most one subject may also satisfy HASS Distribution.'),
   ('performance', 'Drum ensemble and shared-area restrictions', '21M.460 requires two semesters; the two six-unit classes may be combined by petition into one 12-unit HASS elective. The Black Matters subject can count as Historical Studies or Humanities and the Arts, never both.')]),
 'american-studies': dict(title='American Studies', count=4,
  areas=['Humanities and the Arts', 'Historical Studies', 'Literature', 'Science, Technology, and Society', 'Social Sciences'],
  markers=['taking four subjects', 'at least one of which must be in Historical Studies and one in Literature', 'variances are possible', 'partial listing', 'advisor’s discretion'],
  policies=[('selection', 'Four-subject interdisciplinary plan and exceptions', 'Choose four subjects with at least one Historical Studies and one Literature subject; the source permits variances. These two area minima are overlays within the four, not additional subjects. Plans may focus on a period, problem or theme. The listed pool is partial; other subjects, former offerings and variable topics require advisor discretion. At most one subject may also satisfy HASS Distribution.')]),
 'ancient-and-medieval-studies': dict(title='Ancient and Medieval Studies', count=4,
  areas=['Ancient and Medieval', 'Medieval', 'Ancient'],
  markers=['taking four subjects', 'at least one of which must be in the medieval period', 'one in the ancient period', 'At least two of the subjects', 'taken at MIT', 'up to two subjects in Greek or Latin or a medieval vernacular', 'Two 6-unit Greek subjects or two 6-unit Latin subjects', 'combined by petition', 'This list is not exhaustive'],
  policies=[('period', 'Opposite-period requirement and MIT attendance', 'An Ancient World focus requires at least one medieval-period subject; a Middle Ages focus requires at least one ancient-period subject. The Ancient and Medieval group can serve either period. At least two of the four subjects must be taken at MIT. At most one subject may also satisfy HASS Distribution.'),
   ('language', 'Language limit and six-unit combinations', 'At most two subjects in Greek, Latin or a medieval vernacular, at MIT or elsewhere, may count. Two six-unit Greek subjects or two six-unit Latin subjects may combine by petition for 12 HASS units; a single listed six-unit course does not by itself establish a full HASS subject.'),
   ('advisor', 'Advisor-approved additional subjects', 'Consult the concentration advisor. The published list is not exhaustive; relevant former offerings and variable-topic courses may count at the advisor’s discretion.')]),
 'archaeology-and-archaeological-science': dict(title='Archaeology and Archaeological Science', count=4, areas=[],
  markers=['completion of four courses', 'Two of these subjects must include', '3.986', '3.985J', 'choose two other HASS electives', 'other archaeologically-relevant courses', 'approval from the concentration Advisor'],
  policies=[('approval', 'Other archaeologically relevant coursework', 'The concentration advisor may approve other archaeologically relevant courses, including History subjects. This is an open approval route; the five named elective choices are not asserted to be exhaustive.')]),
 'asian-and-asian-diaspora-studies': dict(title='Asian and Asian Diaspora Studies', count=4,
  areas=['Language', 'Historical Studies', 'Humanities and the Arts', 'Social Sciences'],
  markers=['take four subjects', 'no more than three subjects from a single area', 'up to three introductory, intermediate, or advanced subjects', 'permission from the relevant transfer credit examiner', 'This list is not exhaustive'],
  policies=[('selection', 'Area limit and advisor-approved focus', 'Choose four subjects with no more than three in one published area. Consult the advisor about a subregional, diaspora or comparative focus. At most one subject may also satisfy HASS Distribution. The list is nonexhaustive; relevant former offerings and variable topics require advisor discretion.'),
   ('language', 'Language maximum and outside-credit approval', 'At most three introductory, intermediate or advanced Asian-language subjects may count. MIT teaches Chinese, Japanese and Korean; other languages may be studied at Harvard, Wellesley or during summer with permission from the appropriate transfer-credit examiner.')]),
 'latin-american-and-latino-a-studies': dict(title='Latin American and Latino/a Studies', count=4,
  areas=['Anthropology / Politics / Archaeology and Material Science / History', 'Language / Literature / Arts', 'Language / Literature / Arts (continued)'],
  markers=['take four subjects', 'no more than two from a single discipline', 'no more than one focused on the Iberian Peninsula', 'minimum of three of the four subjects must be MIT subjects', 'before registering for a class at another institution', 'This list is not exhaustive'],
  policies=[('selection', 'Discipline, regional and MIT-subject limits', 'Choose four subjects with no more than two in a single discipline and no more than one on the Iberian Peninsula; an Iberian subject is optional. At least three must be MIT subjects. The source’s multi-discipline display groups are not themselves single disciplines. At most one subject may also satisfy HASS Distribution.'),
   ('approval', 'External coursework and additional choices', 'Harvard or Wellesley coursework needs concentration-advisor permission before registration. The published list is nonexhaustive; relevant former offerings and variable topics may count at the advisor’s discretion.')]),
 'legal-studies': dict(title='Legal Studies', count=4,
  areas=['Theory and Philosophy of Law', 'Law and Social Science', 'Law and Policy'],
  markers=['take four subjects', 'at least two from the “Law and Social Science” subfield', 'consultation with the concentration advisor', 'Wellesley and Harvard with permission of the advisor', 'discretion of the advisor'],
  policies=[('selection', 'Advisor-selected plan and social-science overlay', 'Choose four subjects with the concentration advisor, including at least two from Law and Social Science. The two-subject subfield rule is within the four, not additional coursework. At most one subject may also satisfy HASS Distribution.'),
   ('approval', 'Approved external and variable-topic subjects', 'Harvard or Wellesley subjects require advisor permission; relevant former offerings and variable-topic subjects may count at the advisor’s discretion.')]),
 'middle-eastern-studies': dict(title='Middle Eastern Studies', count=4,
  areas=['Humanities and the Arts', 'Language', 'Social Sciences and Historical Studies'],
  markers=['take four subjects', 'no more than two subjects from a single area', 'one or two introductory, intermediate, or advanced subjects', 'Arabic, Hebrew, Persian, Turkish', 'Graduate subjects which are open to qualified undergraduates', 'permission of the instructor', 'This list is not exhaustive'],
  policies=[('selection', 'Area limits and graduate-subject permission', 'Choose four subjects with at most two in a single published area. At most one subject may also satisfy HASS Distribution. Entries marked graduate are open only to qualified undergraduates with instructor permission; listing is not permission or current-offering evidence.'),
   ('language', 'Advisor-approved language route', 'With the concentration advisor’s permission, one or two language subjects at introductory, intermediate or advanced level may come from Harvard or Wellesley in Arabic, Hebrew, Persian or Turkish; the advisor may approve other Middle Eastern languages.'),
   ('approval', 'Open approval for other relevant subjects', 'The list is not exhaustive. Relevant former offerings and variable-topic subjects may count at the concentration advisor’s discretion.')]),
 'religious-studies': dict(title='Religious Studies', count=3, areas=[],
  markers=['take three subjects', 'coherent course of study', 'partial listing', 'advisor’s discretion', 'cross-register for classes at Harvard or Wellesley', 'This list is not exhaustive'],
  policies=[('selection', 'Coherent advisor-approved plan and open pool', 'Choose three subjects forming a coherent plan with the concentration advisor. The list is expressly partial; other courses, relevant former offerings and variable topics require advisor discretion. Harvard/Wellesley cross-registration can broaden the topics. At most one subject may also satisfy HASS Distribution. Graduate-listed observations are retained as the source presents them, without assuming automatic undergraduate enrollment permission.')]),
 'russian-and-eurasian-studies': dict(title='Russian and Eurasian Studies', count=4, areas=[],
  markers=['choose four of the following MIT subjects', 'cross-register for classes at Harvard or Wellesley', 'languages of Eastern Europe and/or Russian'],
  policies=[('selection', 'Four-subject plan and cross-registration context', 'The page directs concentrators to choose four listed MIT subjects and separately permits cross-registration at Harvard or Wellesley in Eastern European/Russian languages, history, literature, government and related fields. The general registrar concentration-approval and external-credit rules still apply; this sentence alone does not create an automatic substitution. At most one subject may also satisfy HASS Distribution. Parenthetical term labels on course names are source annotations, not verified current scheduling.')]),
}

CODE = r'[A-Z0-9]+\.[A-Z0-9]+(?:\[J\])?'
ROW = re.compile(r'^(' + CODE + r'(?:\s*/\s*' + CODE + r')*)\s*[/,:]?\s+(.+)$')


def _section(html, spec):
    root = content(html, spec['title'] + ' Concentration')
    h = root.find(lambda n: n.name in ('h2', 'h3') and clean(n.get_text(' ', strip=True)).lower() == 'subject requirements')
    if h is None or h.parent.find(class_='body-content') is None:
        raise ValueError('SHASS subject-requirements section missing')
    section = h.parent
    require_phrases(section, spec['markers'])
    if spec['title'] != 'Archaeology and Archaeological Science':
        require_phrases(section, ['one subject that also counts toward the HASS Distribution'])
    heads = [clean(n.get_text(' ', strip=True)) for n in section.find_all('h3') if clean(n.get_text(' ', strip=True))]
    if heads != spec['areas']:
        raise ValueError('HASS field area structure changed')
    return section


def parse_field(key, html):
    spec = FIELDS[key]
    section = _section(html, spec)
    sid, prefix = PID + '-hass-' + key, 'mit-ai-hass-' + key
    url = BASE + key + '-concentration/'
    courses, groups = {}, {name: [] for name in spec['areas']}
    current = None
    for n in section.find_all(['h3', 'p']):
        if n.name == 'h3':
            heading = clean(n.get_text(' ', strip=True))
            if heading:
                current = heading
            continue
        # Course rows are separated by HTML breaks, not text-node boundaries.
        for br in n.find_all('br'):
            br.replace_with('__SHASS_ROW_BREAK__')
        for raw in n.get_text(' ', strip=True).split('__SHASS_ROW_BREAK__'):
            text = clean(raw.replace('\u200b', ''))
            m = ROW.match(text)
            if not m:
                if re.match(r'^' + CODE + r'\b', text):
                    raise ValueError('Unrecognized SHASS subject row: ' + text[:80])
                continue
            code, tail = m.groups()
            code = re.sub(r'\s*/\s*', '/', code)
            primary_code = code
            aliases = re.search(r'\[([^]]+)\]', tail)
            if aliases and 'unit' not in aliases[1]:
                code += ' [' + clean(aliases[1]) + ']'
            # Keep the observation ID keyed to its leading source registration label.
            # Titles and cross-list aliases are factual labels; descriptions stay null.
            title = re.split(r',?\s*(?:\[|\(HASS-|\(G\)|[,;]\s*(?:HASS-|CI-H)|\(6 units\))', tail, maxsplit=1)[0].strip(' ,;')
            credits = 6 if re.search(r'(?:6-unit course|\(6 units\))', tail) else None
            c = course(prefix, code, title, sid, url, credits=credits, unit='units', category='human_context')
            c['id'] = course(prefix, primary_code, title, sid, url)['id']
            if c['id'] in courses and courses[c['id']]['name'] != title:
                raise ValueError('Conflicting same-field subject labels')
            courses[c['id']] = c
            if current and c['id'] not in groups[current]:
                groups[current].append(c['id'])
    if not courses or any(not ids for ids in groups.values()):
        raise ValueError('HASS field subject inventory missing')
    parent = prefix + '-option'
    rules = [rule(parent, 'Optional HASS field: ' + spec['title'], sid, kind='note', summary='Apply this branch only if this HASS concentration is selected. It is not an additional AI-major requirement. Generic registrar HASS, advisor-approval, grading and external-credit policies remain applicable. Repeated/cross-listed labels are not additional required subjects.')]
    if key == 'archaeology-and-archaeological-science':
        required = [c['id'] for c in courses.values() if c['code'].split(' [')[0] in ('3.986', '3.985J')]
        if len(required) != 2:
            raise ValueError('Archaeology required-subject structure changed')
        rules.extend([
            rule(prefix + '-required', 'Two required archaeology subjects', sid, required, parent=parent, kind='all'),
            rule(prefix + '-electives', 'Two other HASS archaeology electives', sid, [cid for cid in courses if cid not in required], parent=parent, kind='choose_courses', count=2, summary='Choose two other HASS electives from the published options or the separately stated advisor-approved route.')])
    else:
        rules.append(rule(prefix + '-selection', str(spec['count']) + ' subjects within this optional field', sid, list(courses), parent=parent, kind='choose_courses', count=spec['count'], summary='Apply all field-specific area, approval and exception rules below. Where the source allows other approved subjects, this observed pool is not exhaustive.'))
    for i, (name, ids) in enumerate(groups.items()):
        rules.append(rule(prefix + '-area-' + str(i + 1), name + ': source option group', sid, ids, parent=parent, kind='note', summary='Source grouping for the selection rules; this group is not a separate all-course requirement.'))
    for suffix, title, summary in spec['policies']:
        rules.append(rule(prefix + '-policy-' + suffix, title, sid, parent=parent, kind='note', summary=summary))
    if key == 'american-studies':
        for name in ['Historical Studies', 'Literature']:
            rules.append(rule(prefix + '-overlay-' + name.lower().replace(' ', '-'), 'At least one ' + name + ' subject within the four', sid, groups[name], parent=parent, kind='choose_courses', count=1, summary='Overlay within the four-subject plan, subject to the source’s permitted variances and advisor-approved additional subjects.'))
    elif key == 'legal-studies':
        rules.append(rule(prefix + '-overlay-social-science', 'At least two Law and Social Science subjects within the four', sid, groups['Law and Social Science'], parent=parent, kind='choose_courses', count=2, summary='Subfield overlay within the four-subject advisor-approved plan; not two additional courses.'))
    return dict(id=PID, courses=list(courses.values()), requirements=rules)


SOURCE_PARSERS = {BASE + key + '-concentration/': partial(parse_field, key) for key in FIELDS}
