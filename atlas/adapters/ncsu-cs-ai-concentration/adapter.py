"""Observe the concentration-local catalog rows, finite pools and grade policies."""
from atlas.adapters.national_curriculum_common import content, clean, require_phrases, rule
from atlas.adapters.degree_table_observations import Tables

PROGRAM_ID = 'ncsu-cs-ai-concentration'
SOURCES = ['https://catalog.ncsu.edu/undergraduate/engineering/computer-science/artificial-intelligence-concentration/', 'https://catalog.ncsu.edu/about/academic-calendar/']
SOURCE_ID = PROGRAM_ID + '-identity'


def parse(html):
    root = content(html, 'Computer Science (BS): Artificial Intelligence Concentration')
    require_phrases(root, ['21 credit hours of specialized coursework', 'only 3 hours may count in the AI Restricted Electives from this list', 'A grade of C or higher is required.', 'A grade of C- or higher is required.', 'major GPA, which consists of all CSC courses attempted at NCSU', 'no CSC course used to satisfy the major requirements has a grade below a C-', 'Change of Degree Application (CODA)', 'must be 2.0 or higher', 'developing intelligent and autonomous systems', 'applying machine learning to real-world datasets', 'incorporating intelligent behavior into diverse computing platforms'])
    plan = root.find(id='planrequirementstextcontainer')
    if plan is None:
        raise ValueError('Concentration plan section missing')
    main_table = plan.find('table', class_='sc_courselist')
    local_rows = []
    in_local = False
    for row in main_table.find_all('tr'):
        text = clean(row.get_text(' ', strip=True))
        if text == 'Concentration Courses/Groups/Electives':
            in_local = True
            continue
        if in_local and 'areaheader' in row.get('class', []):
            break
        if in_local:
            local_rows.append(row)
    if [clean(sup.get_text()) for row in local_rows for sup in row.find_all('sup')] != ['1', '1', '1']:
        raise ValueError('Concentration grade-footnote mapping changed')
    pool_heading = next((h for h in plan.find_all('h3') if 'CSC AI Restricted Electives' in h.get_text()), None)
    if pool_heading is None or not pool_heading.find('sup') or clean(pool_heading.find('sup').get_text()) != '2':
        raise ValueError('CSC AI pool grade-footnote conflict changed; review needed')
    for sup in plan.find_all('sup'):
        sup.decompose()
    tables = plan.find_all('table', class_='sc_courselist')
    if len(tables) != 5:
        raise ValueError('Reviewed elective-table structure changed')
    t = Tables('ncsu-ai', SOURCE_ID, SOURCES[0])
    rows = tables[0].find_all('tr')
    local = False
    core_ids, amounts = [], {}
    for row in rows:
        text = clean(row.get_text(' ', strip=True))
        if text == 'Concentration Courses/Groups/Electives':
            local = True
            continue
        if local and 'areaheader' in row.get('class', []):
            break
        if not local:
            continue
        observation = t.row(row)
        if observation:
            core_ids.extend(observation['ids'])
        else:
            cells = row.find_all('td', recursive=False)
            if len(cells) == 2:
                label = clean(cells[0].get_text(' ', strip=True))
                value = clean(cells[1].get_text())
                if label in ('CSC AI Restricted Electives', 'AI Restricted Electives') and value.isdigit():
                    amounts[label] = int(value)
    if len(core_ids) != 2 or set(amounts) != {'CSC AI Restricted Electives', 'AI Restricted Electives'}:
        raise ValueError('Concentration core or credit choices changed')
    pools = []
    for index, heading in [(1, 'AI Restricted Electives'), (2, 'CSC AI Restricted Electives')]:
        if clean(tables[index].find_previous('h3').get_text(' ', strip=True)) != heading:
            raise ValueError('Expected local elective heading absent')
        ids = []
        for row in tables[index].find_all('tr'):
            observation = t.row(row)
            if observation:
                ids.extend(observation['ids'])
        if not ids:
            raise ValueError('Finite elective pool missing')
        pools.append(ids)
    general, computing = pools
    root_rule = rule('ncsu-ai-total', 'AI concentration: 21 credit hours', SOURCE_ID, credits=21, summary='The concentration comprises two required courses, a CSC AI elective block, and a broader AI elective block. This inventory does not represent the entire host BS.')
    requirements = [root_rule,
        rule('ncsu-ai-required', 'Required AI courses', SOURCE_ID, core_ids, parent=root_rule['id']),
        rule('ncsu-ai-csc-electives', 'CSC AI restricted electives', SOURCE_ID, computing, parent=root_rule['id'], kind='note', credits=amounts['CSC AI Restricted Electives'], summary=f"Select {amounts['CSC AI Restricted Electives']} published credit hours from this finite pool. The source unit has not been normalized; this is a credit choice, not a course-count choice."),
        rule('ncsu-ai-electives', 'AI restricted electives', SOURCE_ID, general + computing, parent=root_rule['id'], kind='note', credits=amounts['AI Restricted Electives'], summary=f"Select {amounts['AI Restricted Electives']} published credit hours from this finite pool, with at most 3 from its CSC AI subset. The source unit has not been normalized; one-credit options mean this must not be reduced to three courses."),
        rule('ncsu-ai-csc-cap', 'Limit on CSC AI courses in the broader pool', SOURCE_ID, computing, parent='ncsu-ai-electives', kind='note', summary='At most 3 credit hours from the CSC AI restricted list may count in the broader AI restricted elective block.'),
        rule('ncsu-ai-grade', 'Concentration minimum grades', SOURCE_ID, core_ids + computing, kind='note', summary='The plan marks both required AI courses and the CSC AI restricted block with footnote 1, requiring a grade of C or higher. The broader AI block has no such marker. However, the CSC AI pool heading carries footnote 2 (C-minus), creating an unresolved source discrepancy; no single grade rule is certified for that pool.'),
        rule('ncsu-ai-host-gpa', 'Host CS major GPA condition', SOURCE_ID, kind='note', summary='Either earn at least a 2.0 major GPA over all CSC courses attempted at NC State, or, when that GPA is below 2.0, have no grade below C-minus in any CSC course used for major requirements.'),
        rule('ncsu-ai-host-entry', 'Host degree entry', SOURCE_ID, kind='note', summary='Students enter the CS degree after the Engineering First-Year curriculum through the college CODA process; detailed admission and concentration-declaration rules require separate review.')]
    return dict(id=PROGRAM_ID, title='Artificial Intelligence', award_level='concentration', program_kind='concentration', courses=list(t.courses.values()), requirements=requirements, outcomes=[dict(text='The concentration develops preparation in intelligent and autonomous systems, machine learning with real datasets, and intelligent computing platforms.', kind='source_stated', statement_type='program_aim', source_id=SOURCE_ID, locator='Artificial Intelligence Concentration overview')])
