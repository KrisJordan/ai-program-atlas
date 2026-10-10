"""Reviewed MIT institute rules, scoped separately from the Course 6-4 chart."""
import re
from atlas.adapters.national_curriculum_common import content, clean, course, rule, require_phrases

PID = 'mit-ai-decision-making-bs'
GIR = 'https://catalog.mit.edu/mit/undergraduate-education/general-institute-requirements/'
GRADES = 'https://catalog.mit.edu/mit/procedures/academic-performance-grades/'
GRADUATION = 'https://catalog.mit.edu/mit/procedures/graduation/'

# Each reviewed paraphrase is guarded by the material source conditions it describes.
GIR_POLICIES = [
    ('attendance', None, 'Minimum attendance and approved program', ['not less than three regular academic terms', 'include the term of graduation', 'departmental permission', 'only by petition'], 'Attend at least three regular academic terms, ordinarily including the graduation term, and complete an approved GIR and departmental program. Departmental deviations need department permission; GIR substitutions require the appropriate faculty-committee petition.'),
    ('cohort', None, 'Transfer cohort requirements', ['Transfer students generally will graduate under the requirements that apply to the class they join'], 'Transfer students normally follow requirements for the class they join on entry; the source does not assign an entry year to this program record.'),
    ('accounting', None, 'Units beyond GIRs', ['minimum of 48 units of unrestricted electives', 'does not include ROTC subjects', 'will not be included in the "units beyond" calculation'], 'At least 48 unrestricted elective units belong within the program-specific units beyond GIRs. ROTC units are excluded. CI-M units generally count beyond GIRs, except when that subject also supplies one of the 17 GIR subjects. Use the Course 6-4 chart for its specific unit range.'),
    ('calculus-credit', 'sciencerequirementtextcontainer', 'Calculus advanced credit', ['lose it if they take 18.01', '3 units of elective credit if they take 18.01A'], 'Existing AP, advanced-standing or transfer credit for 18.01 is lost on taking 18.01; taking 18.01A instead earns three elective units. Placement and subject-specific calculus policies require the linked mathematics guidance.'),
    ('physics-order', 'sciencerequirementtextcontainer', 'Physics sequencing and advanced credit', ['without having first received credit for a Physics I', '6 units of elective credit in place of 8.01'], 'A Physics I GIR credit must precede enrollment in a Physics II GIR subject, even when mixing sequences. Students with AP or advanced-standing 8.01 credit who take 8.012 receive six elective units in place of 8.01.'),
    ('ci-pace', 'communicationrequirementtextcontainer', 'Communication totals and annual pace', ['two CI subjects in the humanities', 'two CI subjects in their major', 'one of their CI subjects by the end of the first year', 'two by the end of the second year', 'three by the end of the third year', 'four by graduation', 'Only one CI-H subject per term'], 'Complete two CI-H/HW and two major-specific CI-M subjects. Minimum cumulative progress is one by year one, two by year two, three by year three and four by graduation. Only one CI-H per term counts, while multiple CI-M or a concurrent CI-H and CI-M may count. Noncompliance is referred to academic-performance review.'),
    ('ci-placement', 'communicationrequirementtextcontainer', 'First communication subject placement', ['score of 5 on either', 'score of 7 on the English A or B Higher-Level', 'All other students must take', 'as their first CI subject'], 'The first CI subject must be CI-HW unless the First-year Essay Evaluation permits CI-H/CI-HW, AP English Language or Literature is 5, or higher-level IB English A/B is 7. An eligible student may still choose CI-HW. Pass the first CI-H/HW by the end of the second term.'),
    ('ci-double', 'communicationrequirementtextcontainer', 'Communication for double majors', ['Normally, these students will take four CI-M subjects', 'common to both departments'], 'Double majors must meet the CI-M component of each major plus two CI-H subjects. Four CI-M subjects are normal; a subject common to both departments may satisfy both when permitted.'),
    ('hass-distribution', 'hassrequirementtextcontainer', 'HASS minimum and distribution criteria', ['minimum of eight subjects', 'Three of the eight subjects', 'humanities, arts, and social sciences'], 'Complete eight HASS-designated subjects, including one from each distribution category: humanities, arts and social sciences. Two CI-H/HW subjects may simultaneously meet communication requirements. Eligibility is defined by official designation; this rule does not invent a fixed course list.'),
    ('hass-concentration', 'hassrequirementtextcontainer', 'HASS concentration and deadlines', ['either three or four subjects', 'second term of junior year', 'One of the subjects', 'permission of the concentration advisor', 'final term prior to graduation', 'special concentration may be arranged with advance approval'], 'Complete a field-specific three- or four-subject HASS concentration with its designated advisor. Submit the proposal by the end of the first week of the second junior-year term and completion form by the end of the first week of the final graduation term. One distribution subject may overlap with advisor permission. A special concentration needs advance approval; field-specific rules remain unreviewed.'),
    ('hass-electives', 'hassrequirementtextcontainer', 'Remaining HASS eligibility', ['remainder of the eight-subject requirement', 'any distribution category', 'designated as HASS electives'], 'After distribution and concentration, remaining slots in the eight-subject total may use subjects in any HASS distribution category or designated HASS electives.'),
    ('rest', 'restrequirementtextcontainer', 'REST selection and departmental restriction', ['two subjects from the list below', 'no more than one in their department', 'subjects designated with a J'], 'Complete two REST-designated subjects, ordinarily no more than one from the student’s department; jointly offered J subjects are exempt from that departmental limit. Departmental degree subjects may simultaneously satisfy REST. Course 6-4 identifies 6.1200[J] and 18.C06[J] as its normal route; substitutions require review.'),
    ('lab', 'laboratoryrequirementtextcontainer', 'Laboratory-designated credit', ['12 units in sum designated', 'beyond the 12 needed', 'counted as units beyond the GIRs'], 'Complete 12 units specifically designated as Institute Laboratory credit; subjects may be combined, and designated laboratory credit can differ from total subject units. Subject units above the 12 needed count beyond GIRs. Course 6-4 identifies 6.1010 as its normal route.'),
    ('pe', 'physicaleducationtextcontainer', 'PE, transfer and swimming paths', ['Transfer students need to complete four points (two courses)', 'passing the swim test', 'Four points are awarded', 'maximum of four points', 'by the end of their second year', 'submit a plan for a time extension'], 'First-year entrants complete four PE/wellness courses for eight points; transfer entrants complete two courses for four points. Both must satisfy swimming through a beginning swim class or test. Each varsity year earns four points; each ROTC year earns two, capped at four. Approved training/swim/exercise options may earn points. Finish by the end of year two or submit an extension plan. PE points are not academic units.'),
]


def checked_notes(root, specs, sid):
    notes = []
    for suffix, pane_id, title, markers, summary in specs:
        scope = root.find(id=pane_id) if pane_id else root
        if scope is None:
            raise ValueError('Reviewed policy section missing: ' + str(pane_id))
        require_phrases(scope, markers)
        notes.append(rule('mit-ai-institute-' + suffix, title, sid, kind='note', summary=summary))
    return notes


def parse_gir(html):
    root = content(html, 'General Institute Requirements')
    sid = PID + '-gir'
    rules = checked_notes(root, GIR_POLICIES, sid)
    science = root.find(id='sciencerequirementtextcontainer')
    courses = []
    expected = ['Biology (GIR)', 'Chemistry (GIR)', 'Calculus I (GIR)', 'Calculus II (GIR)', 'Physics I (GIR)', 'Physics II (GIR)']
    headings = []
    group = None
    for table in science.find_all('table', class_='sc_courselist'):
        for row in table.find_all('tr'):
            if 'areaheader' in row.get('class', []):
                title = clean(row.find('td').get_text(' ', strip=True))
                headings.append(title)
                group = rule('mit-ai-gir-science-' + str(len(headings)), title, sid, kind='choose_courses', count=1, summary='Select one of the listed subjects for this science GIR slot.')
                rules.append(group)
                continue
            cell = row.find('td', class_='codecol')
            if cell is None:
                continue
            code = clean(cell.get_text())
            if group is None or not re.fullmatch(r'\d+\.\d+[A-Z]?', code):
                raise ValueError('Unrecognized science GIR code or section')
            credit = clean(row.find('td', class_='hourscol').get_text())
            c = course('mit-ai-gir', code, None, sid, GIR + '#sciencerequirementtext', credits=float(credit) if credit.isdigit() else None, unit='units', category='mathematics' if code.startswith('18.') else 'foundations')
            courses.append(c)
            group['course_ids'].append(c['id'])
    if headings != expected or any(not r['course_ids'] for r in rules if r['kind'] == 'choose_courses'):
        raise ValueError('Science GIR choice sections incomplete')
    return dict(id=PID, courses=courses, requirements=rules)


def parse_graduation(html):
    root = content(html, 'Graduation')
    specs = [('degree-application', None, 'Degree application and clearance', ['online SB degree application', 'by the deadline', 'all financial obligations', 'no pending disciplinary actions'], 'Submit the SB degree application by the relevant academic-calendar deadline. Award requires faculty approval following committee/department recommendation, cleared financial obligations and no pending disciplinary actions.')]
    return dict(id=PID, requirements=checked_notes(root, specs, PID + '-graduation'))


def parse_grades(html):
    root = content(html, 'Academic Performance and Grades')
    specs = [
        ('academic-standing', None, 'Undergraduate academic-performance review', ['does not establish rigid standards', 'at least 36 units of credit', 'term rating above 3.0', 'individual basis'], 'The CAP normally accepts at least 36 units per regular term with a term rating above 3.0/5, unless it has imposed a higher individual standard. Falling below this triggers individual review rather than an automatic graduation GPA cutoff. The cumulative 3.0 federal-aid criterion is a separate financial-aid rule.'),
        ('passing-grades', None, 'Passing and nonpassing grades', ['Minimally acceptable performance', 'retake the prerequisite', 'performance at the level A, B, or C', 'First-Year Pass/No Record'], 'D is generally passing, but a department may require additional work or repetition before the next subject. Authorized P corresponds to A–C performance; first-year DN/FN do not earn credit. Exact first-year and flexible P/NR eligibility remains subject to separate policy review.'),
        ('incomplete', None, 'Incomplete grades at graduation', ['All grades of Incomplete must be resolved prior to graduation', 'No grade of I can be assigned', 'IE does not carry credit but need not be resolved'], 'Resolve ordinary I grades before graduation, and no ordinary I can be assigned in the graduation term. The exceptional emergency IE notation carries no credit but need not be resolved before graduation; the source distinguishes these cases.'),
    ]
    return dict(id=PID, requirements=checked_notes(root, specs, PID + '-grades'))

DEPARTMENT = 'https://www.eecs.mit.edu/academics/undergraduate-programs/curriculum/6-4-artificial-intelligence-and-decision-making/'
PETITIONS = 'https://www.eecs.mit.edu/academics/undergraduate-programs/resources-for-current-students/degree-audits-and-departmental-petitions/'
# The public department page embeds this endpoint and adds a cache-busting timestamp.
# That parameter is a request detail, not a source date or curriculum version.
EMBEDDED = 'https://eecsis.mit.edu/degree_requirements.pcgi?program=6-4&plugin=1791675178996'


def parse_department(html):
    root = content(html, '6-4: Artificial Intelligence and Decision Making')
    require_phrases(root, ['Students can declare 6-4 starting in Fall 2022', 'analysis and synthesis of systems', 'learn, make decisions and adapt', 'Requirements for older versions'])
    sid = PID + '-department'
    return dict(id=PID, outcomes=[dict(text='The major develops techniques for systems that perceive, communicate and act, learning and adapting while making decisions in changing environments.', kind='source_stated', statement_type='program_aim', source_id=sid, locator='Course 6-4 program introduction')], requirements=[rule('mit-ai-declaration-date', 'Department declaration availability', sid, kind='note', summary='The department says students could declare Course 6-4 beginning Fall 2022. This is declaration evidence, not proof of the first instructional offering or of the applicable curriculum version.')])


def parse_petitions(html):
    root = content(html, 'Degree Audits and Departmental Petitions')
    specs = [('petitions', None, 'Departmental substitutions and petitions', ['talk to your advisor', 'submit a petition', 'case-by-case basis', 'There is no petition that is always approved', 'Do not wait until your final semester'], 'Discuss a proposed substitution with the advisor, then submit a departmental petition for advisor comments and department action. Decisions are individual, never automatically guaranteed by another student’s approval. Submit early, including before taking a proposed substitute, rather than waiting until the final semester. The student-specific audit is restricted to current EECS students and is not part of this public-source inventory.')]
    return dict(id=PID, requirements=checked_notes(root, specs, PID + '-petitions'))


# Preserve pre-existing stable course IDs for catalog entries bearing a joint marker.
CIM2_JOINT = {'6.2600', '6.4200', '6.4590', '6.4860', '6.4880', '6.UAR'}


def parse_versioned(html):
    root = content(html, 'Degree Requirements for 6-4_2025')
    require_phrases(root, ['if you entered MIT in Fall 2025 or later', 'Includes subjects as of Fall 2026', 'at most one required subject', 'multiple additional constraints', 'At least two of your completed subjects', 'must be on the CIM2 list'])
    lists = root.find(id='subject_lists')
    if lists is None:
        raise ValueError('Versioned subject lists missing')
    anchor = lists.find('a', attrs={'name': 'CIM2'})
    table = anchor.find_next('table') if anchor else None
    if table is None or table.find_parent(id='subject_lists') is None:
        raise ValueError('Versioned CIM2 list missing')
    sid = PID + '-versioned'
    courses = []
    for link in table.find_all('a', class_='annotated-link'):
        code_node = link.find('nobr')
        annotation = link.find('div', class_='annotation')
        if code_node is None:
            raise ValueError('CIM2 course code missing')
        code = clean(' '.join(code_node.find_all(string=True, recursive=False)))
        if not re.fullmatch(r'6\.[A-Z]?\d+[A-Z]?|6\.UAR|6\.UAT', code):
            raise ValueError('Unrecognized CIM2 course code')
        name, prerequisites = None, None
        if annotation is not None and annotation.find('b') is not None:
            title = clean(annotation.find('b').get_text())
            if not title.startswith(code + ' '):
                raise ValueError('CIM2 annotation identity mismatch')
            name = title[len(code) + 1:]
            text = clean(annotation.get_text(' ', strip=True))
            prerequisites = re.search(r'(Prereqs(?:/\[Coreqs\])?:.*?)\s+Units:', text)
        c = course('mit-ai', code, name, sid, EMBEDDED + '#CIM2', unit='units')
        if code in CIM2_JOINT:
            c['id'] += '-j'
        c['prerequisites'] = prerequisites[1] if prerequisites else None
        courses.append(c)
    if not courses:
        raise ValueError('Versioned CIM2 list empty')
    math = lists.find('a', attrs={'name': 'MATH'})
    if math is None:
        raise ValueError('Open MATH eligibility criterion missing')
    # Inspect just the MATH section, stopping before the next named list.
    pieces = []
    for sibling in math.next_siblings:
        if getattr(sibling, 'name', None) == 'a' and sibling.get('name'):
            break
        pieces.append(str(sibling))
    from bs4 import BeautifulSoup
    require_phrases(BeautifulSoup(''.join(pieces), 'html.parser'), ['Any non-calculus subject', 'Math (course 18) SB requirement', 'does not have essentially similar content'])
    specs = [
        rule('mit-ai-version-eligibility', 'Version 6-4_2025 applicability', sid, kind='note', summary='The public department source labels this version 6-4_2025, requires it for students entering MIT in Fall 2025 or later, and says subject lists are current as of Fall 2026. Those labels are curriculum applicability evidence, not a first-offered date or an inferred catalog edition.'),
        rule('mit-ai-version-cim2', 'Version 6-4_2025: CIM2 overlay', sid, [c['id'] for c in courses], kind='note', summary='For this stated version, at least two completed subjects must belong to the listed CIM2 pool. This is an additional constraint across the program, not two extra required subject slots. It differs from the unversioned catalog reference inventory; version reconciliation remains explicit.'),
        rule('mit-ai-version-reuse', 'Version 6-4_2025: subject reuse', sid, kind='note', summary='Each completed subject may fill at most one required subject slot but may satisfy multiple additional constraints, including center, SERC and CIM2 designations. Do not impose separate unique subjects for every overlay.'),
        rule('mit-ai-version-math', 'Version 6-4_2025: open mathematics elective criterion', sid, kind='note', summary='The MATH option permits any non-calculus subject satisfying a Course 18 SB requirement, provided its content is not essentially similar to other subjects counted toward this degree. This is an eligibility criterion, not a fabricated finite list.'),
    ]
    return dict(id=PID, courses=courses, requirements=specs)
