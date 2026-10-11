"""Revelle's current public component pages, conditional on college and admit cohort."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, slug, text
from atlas.adapters.ucsd_college_context import requirement
from atlas.adapters.ucsd_degree_policies import PID, guarded
BASE = 'https://revelle.ucsd.edu/academics/general-education/'
PAGES = ('humanities', 'mathematics', 'nat-science', 'soc-science', 'fine-arts', 'language')


def section(html, heading):
    s = BeautifulSoup(html, 'html.parser')
    if not any(text(h) == heading for h in s.find_all('h1')):
        raise ValueError('Revelle component heading changed')
    return s.find('section', class_='main-section') or s.find('main') or s


def node(page, key, title, **kw):
    return requirement(PID, 'revelle-' + page + '-' + key, title,
                       PID + '-revelle-' + page, unit='quarter_hours', category='human_context', **kw)


def record(page, code, name=None, credits=None):
    return course(code, name, PID + '-revelle-' + page, BASE + page + '.html',
                  institution='ucsd', unit='quarter_hours', credits=credits, category='human_context')


def normal(code):
    m = re.fullmatch(r'([A-Z]+)-0*(\d+)([A-Z]*)', code)
    if not m:
        return None
    return m[1] + ' ' + str(int(m[2])) + m[3]


def output(courses, nodes):
    return dict(id=PID, curriculum_status='partial', courses=courses, requirements=nodes)


def parse_science(html):
    page = 'nat-science'; s = section(html, 'Natural Science Requirement'); v = text(s)
    guarded(v, ['Five courses to include', 'Fall 2026 and after', 'Three courses to include',
                'different disciplines', 'labs are not required', 'Course and lab must be taken concurrently'])
    tables = s.find_all('table')
    labels = ['Biology', 'Chemistry', 'Physics', 'Environmental sciences', 'Scientific reasoning', 'Astronomy in science fiction']
    if len(tables) != len(labels):
        raise ValueError('Revelle science table boundaries changed')
    nodes = [node(page, 'scope', 'Revelle science cohort and discipline rules', kind='note', summary='Conditional Revelle route. First-year entrants take five courses: one each in biology, chemistry and physics, plus two approved science options. Transfers from Fall 2026 take three: two different disciplines among biology/chemistry/physics, plus one approved option. Pre-Fall-2024 transfers follow five courses. This page does not resolve Fall 2024/2025 transfers; the separately cited catalog describes four courses. Do not merge these cohort rules.'),
             node(page, 'policy', 'Revelle science grading and laboratories', kind='note', summary='Approved R versions count. Science/engineering/mathematics majors are advised to use letter grades unless their major does not require them. Revelle itself does not require labs; departmental rules still apply, and the listed PHYS 1 lecture/lab pairs require concurrent enrollment. Table subheadings advise different preparations/majors, not a separate AI-specific science pool.')]
    courses = {}
    for table, label in zip(tables, labels):
        root = node(page, slug(label), label + ' approved Revelle pool', kind='note', summary='Approved option pool under the cohort/distribution rule; not an additional requirement.')
        nodes.append(root); found = 0
        for tr in table.find_all('tr'):
            cells = [text(x) for x in tr.find_all(['td', 'th'])]
            if len(cells) != 2 or cells[0] == 'Course No.': continue
            raw, detail = cells; code = normal(raw); ids = []
            if code:
                name = re.split(r'\s*\(| Prior to FA24| - prep for', detail, maxsplit=1)[0].strip()
                c = record(page, code, name); courses[c['id']] = c; ids = [c['id']]
            elif not re.match(r'[A-Z]+[- ]', raw):
                raise ValueError('Unrecognized science option row')
            # Compound/cross-listed rows stay one printed option; no guessed credit split.
            summary = 'Published option ' + raw + ': ' + detail + '.'
            if not ids: summary += ' Retained as one literal compound/extension option, without inferred independent alternatives.'
            nodes.append(node(page, slug(raw), raw + ' option', parent=root['id'], kind='note', course_ids=ids, summary=summary)); found += 1
        if not found: raise ValueError('Empty science discipline pool')
    return output(list(courses.values()), nodes)


def parse_math(html):
    page = 'mathematics'; s = section(html, 'Mathematics Requirements'); v = text(s)
    guarded(v, ['one course in calculus and two additional', 'Only one of MATH-011, PSYC-060, or AP Statistics', 'Effective Fall 2024', 'Letter Grade', 'AP Calculus (AB or BC) scores of 2 or higher', 'grade C- or better'])
    first = s.find('p', string=re.compile('Calculus course:'))
    approved = s.find('p', string=re.compile('Approved list of mathematics courses:'))
    if not first or not approved: raise ValueError('Math list boundary changed')
    courses = {}; nodes = []
    for key, parent, count in [('calculus', first, 1), ('additional', approved, 2)]:
        root = node(page, key, 'Revelle ' + key + ' mathematics', kind='choose_courses', count=count, summary='Conditional current Revelle three-course route; alternatives on one published row are not independent extra requirements.')
        nodes.append(root)
        for li in parent.find_next('ul').find_all('li', recursive=False):
            raw = text(li); stripped = re.sub(r'\(formerly [^)]*\)', '', raw)
            ids = []
            for value in re.findall(r'[A-Z]+-\d+[A-Z]*', stripped):
                code = normal(value); c = record(page, code); courses[c['id']] = c; ids.append(c['id'])
            nodes.append(node(page, key+'-'+str(len(nodes)), raw.split(' – ')[0], kind='note', parent=root['id'], course_ids=ids, summary='Published selection row: '+raw+'.'))
    nodes.append(node(page, 'policy', 'Revelle mathematics equivalence, grading and placement', kind='note', summary='Letter grading required. At most one of MATH 11, PSYC 60 and AP Statistics (score at least 3) counts. Fall-2024 rules apply to all admit types; older first-year entrants before Fall 2024 and transfers before Fall 2023 had two calculus courses plus one additional option and need advising to change their audit. Placement-test exemptions: AP Calculus AB/BC at least 2, IB Mathematics Analyses & Approaches HL at least 5, or prior college calculus at C− or better. Credit is not awarded below AP/IB placement. Former MATH 20F is an alias, not an extra current choice.'))
    return output(list(courses.values()), nodes)


def parse_humanities(html):
    page = 'humanities'; s = section(html, 'Humanities Requirements'); v = text(s)
    guarded(v, ['D grade or better', 'regardless of transfer type', 'first year at UC San Diego', 'HUM-001 or -002', 'Entry Level Writing Requirement'])
    courses = []
    for tr in s.find_all('table')[0].find_all('tr'):
        cells = [text(c) for c in tr.find_all('td')]
        if len(cells) != 2: continue
        m = re.fullmatch(r'Humanities ([\d ]+):', cells[0]); n = re.match(r'(.*?) (\d+) units,', cells[1])
        if not m or not n: raise ValueError('Humanities course row changed')
        courses.append(record(page, 'HUM '+str(int(m[1].replace(' ',''))), n[1], int(n[2])))
    if {c['code'] for c in courses} != {'HUM 1','HUM 2','HUM 3','HUM 4','HUM 5','HUM 100'}: raise ValueError('Humanities inventory changed')
    return output(courses, [node(page,'first','Revelle first-year humanities sequence',kind='all',course_ids=[c['id']for c in courses if c['code']!='HUM 100'],summary='Only the first-year entrant route: HUM 1–5. Satisfy ELWR before the sequence, then HUM 1 or 2 before HUM 3/4/5. Letter grade D or better; approved R versions accepted.'),node(page,'transfer','Revelle transfer humanities route',kind='note',course_ids=[courses[-1]['id']],summary='All new transfers from Fall 2024 take HUM 100 in their first UCSD year, regardless of transfer certification. IGETC waives HUM 1–5; other transfers need HUM 3–5 unless prior coursework satisfies them. HUM 1/2 are usually unnecessary, but advising determines individual transfer credit. Letter grade D or better; limited transfer-course substitutions require the separately linked policy.')])


def parse_language(html):
    page = 'language'; s = section(html, 'Language Requirement'); v = text(s)
    guarded(v, ['Course Needed for First Year Students','Course Needed for Transfer Students','at least one year of high school abroad','Pass/Not Pass'])
    tables=[t for t in s.find_all('table') if 'Course Needed for First Year Students' in text(t)]
    if len(tables)!=1: raise ValueError('Language endpoint table missing')
    nodes=[node(page,'scope','Revelle language proficiency alternatives',kind='note',summary='First-year entrants need fourth-quarter/third-semester proficiency; transfers need second-quarter/second-semester proficiency. Course endpoints below depend on entry type, not all preceding courses as universal requirements. P/NP is permitted. Alternatives include the college proficiency examination, qualifying AP/IB or SAT II (700), a qualifying heritage course, or non-English native language plus at least one year of high school abroad taught in another language, with transcript/advising review. Placement alone is not an award of course credit.')]
    for tr in tables[0].find_all('tr')[1:]:
        cells=[text(c)for c in tr.find_all(['th','td'])]
        if len(cells)!=4:raise ValueError('Language endpoint columns changed')
        name, _, first, transfer=cells
        nodes.append(node(page,slug(name),name+' language endpoints',kind='note',summary='Published required endpoint for first-year entrants: '+first+'; for transfers: '+transfer+'. Printed slash/sequence notation is preserved without guessing independent alternatives. The beginner placement column is not a required endpoint.'))
    return output([],nodes)


def parse_arts(html):
    page='fine-arts'; s=section(html,'The Fine Arts Requirement');v=text(s)
    guarded(v,['One course (2 - 4 units)','Pass/Not Pass','Upper division major courses may not overlap','LTWR courses only','Dance','FILM-071, FILM-072, FILM-073 only','Music','Theater','Visual Arts'])
    return output([], [node(page,'pool','Revelle fine-arts approved department predicates',kind='choose_courses',count=1,summary='One 2–4-unit course from Dance, Music, Theater or Visual Arts, or LTWR literature, or FILM 71/72/73. These open department predicates do not require a finite catalog inventory. Approved R versions and P/NP are accepted; an upper-division major course cannot also fulfill GE.')])


PARSERS = dict(zip(PAGES, [parse_humanities, parse_math, parse_science, None, parse_arts, parse_language]))


def parse_social(html):
    page='soc-science'; s=section(html,'Social Science Requirement'); v=text(s)
    guarded(v,['Two courses (4 units each','Letter Grade','Special Studies courses will not be accepted','Upper division major courses may not overlap'])
    heading=next((h for h in s.find_all('h2')if text(h)=='Approved Social Science Departments'),None)
    if not heading:raise ValueError('Social-science pool boundary missing')
    listing=heading.find_next('ul'); nodes=[node(page,'scope','Revelle social-science distribution',kind='choose_courses',count=2,credits=8,summary='Only the Revelle route: two approved four-unit courses, letter graded. Approved R versions count. Special studies and upper-division courses already counted in the major are excluded.')]; courses={}
    for li in listing.find_all('li',recursive=False):
        raw=text(li); raw=re.sub(r'(?<=-0) (?=\d)','',raw)
        label=raw.split('[')[0].strip(); ids=[]
        if 'only]' in raw and 'courses only]' not in raw:
            for value in re.findall(r'[A-Z]+-\d+[A-Z]*',raw):
                c=record(page,normal(value));courses[c['id']]=c;ids.append(c['id'])
        nodes.append(node(page,slug(label),label+' eligibility',kind='note',parent=nodes[0]['id'],course_ids=ids,summary='Source-approved department/selection predicate: '+raw+'. A department or course-number range is an open predicate, not an enumerated list of all current courses.'))
    p=listing.find_next('p'); m=re.fullmatch(r'\* COGS-(.*)',text(p))
    if not m:raise ValueError('Cognitive-science finite list missing')
    ids=[]
    for value in m[1].replace('and ','').split(','):
        code=normal('COGS-'+value.strip())
        if not code:raise ValueError('Cognitive-science option changed')
        c=record(page,code);courses[c['id']]=c;ids.append(c['id'])
    nodes.append(node(page,'cogs-list','Revelle finite cognitive-science options',kind='note',parent=nodes[0]['id'],course_ids=ids,summary='These are the explicit cognitive-science options, not permission to choose any COGS course.'))
    return output(list(courses.values()),nodes)


PARSERS['soc-science']=parse_social
