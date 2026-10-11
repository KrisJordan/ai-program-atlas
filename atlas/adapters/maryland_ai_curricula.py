"""Parse the two Maryland AI CourseLeaf curricula, preserving alternative tracks."""
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, requirement, slug, text
from atlas.adapters.national_curriculum_common import require_phrases


def learning_outcomes(soup, human, source):
    heading = next((h for h in soup.find_all(['h2','h3']) if text(h) == 'Program Learning Outcomes'), None)
    if heading is None:
        return []
    items = heading.find_next_sibling('ol')
    rows = items.find_all('li') if items else []
    specs = [
        ('human-facing disciplines', 'Use human-centered disciplines to evaluate emerging AI and its consequences.'),
        ('ethical, social, and cultural', 'Assess ethical, social and cultural implications of AI applications.'),
        ('biases, transparency, and accountability', 'Evaluate bias, transparency and accountability in AI systems.'),
        ('technical reports', 'Communicate AI implementation, challenges and results in technical reports.'),
        ('technical foundations', 'Contribute technically informed AI designs aligned with human and societal values.'),
    ] if human else [
        ('modern and classic AI', 'Apply foundational principles of both established and modern AI.'),
        ('efficient, scalable and effective', 'Build scalable algorithms and systems for practical AI applications.'),
        ('Configure, train and deploy', 'Configure, train and deploy existing models for practical use.'),
        ('reliability, efficiency, safety', 'Evaluate AI outputs and tools for reliability, efficiency, safety and goal alignment.'),
        ('ethics and social sciences', 'Use ethical and social perspectives to address AI risks and societal problems.'),
        ('multidisciplinary teams', 'Communicate and collaborate across disciplines when designing AI solutions.'),
    ]
    if len(rows) != len(specs):
        raise ValueError('Maryland learning-outcome inventory changed')
    result=[]
    for row,(marker,summary) in zip(rows,specs):
        require_phrases(row,[marker])
        result.append(dict(text=summary,kind='source_stated',statement_type='learning_outcome',source_id=source,locator='Program Learning Outcomes'))
    return result


def number(node):
    value = text(node) if node else ''
    return int(value) if value.isdigit() else None


def parse(html, *, pid, title, award, url):
    soup = BeautifulSoup(html, 'html.parser')
    heading = soup.find('h1')
    section = soup.find(id='requirementstextcontainer')
    if not heading or text(heading) != title + ' Major' or section is None:
        raise ValueError('Maryland title or requirements section changed')
    tables = section.find_all('table', class_='sc_courselist')
    human = award == 'BA'
    if len(tables) != (1 if human else 6):
        raise ValueError('Maryland specialization table inventory changed')
    edition = soup.find(id='edition')
    match = re.search(r'(20\d{2}-20\d{2}) Catalog', text(edition)) if edition else None
    catalog_year = match[1] if match else None
    source = pid + '-catalog'
    courses, nodes = {}, []
    def req(key, label, **kw):
        node = requirement(pid, key, label, source, unit='semester_hours', **kw)
        nodes.append(node)
        return node
    root = req('major', 'Major requirements', summary='Published major requirements; linked university and college requirements remain outside this partial observation.')
    tracks = req('specializations', 'Choose one specialization', kind='alternative', count=1, parent=root['id'])
    notes = []
    for ti, table in enumerate(tables):
        if ti:
            label = text(table.find_previous(['h2','h3','h4']))
            base = req('track-' + slug(label), label, parent=tracks['id'])
        else:
            base = root
        group = base
        last = None
        for ri, row in enumerate(table.find_all('tr')):
            key = f't{ti}-r{ri}'
            if 'listsum' in row.get('class', []):
                raw = text(row.find('td', class_='hourscol'))
                req(key, 'Published total: ' + raw + ' credits', kind='note', parent=base['id'], credits=number(row.find('td', class_='hourscol')))
                continue
            comment = row.find(class_='courselistcomment')
            if comment:
                label = text(comment)
                if label.startswith('Specialization'):
                    group = tracks
                    if not human:
                        tracks['credits'] = number(row.find('td', class_='hourscol'))
                    continue
                if human and 'Specialization' in label:
                    base = req('track-' + slug(label.split(' (')[0]), label.split(' (')[0], parent=tracks['id'], summary=label)
                    group = req(key, 'Choose six specialization courses', parent=base['id'], kind='choose_courses', count=6)
                else:
                    if human:
                        base = root
                    m = re.search(r'(?:one of|take (two|three|five))', label, re.I)
                    count = {'two':2,'three':3,'five':5}.get(m.group(1),1) if m else None
                    group = req(key, label, parent=base['id'], kind='choose_courses' if count else 'all', count=count, credits=number(row.find('td',class_='hourscol')))
                last = None
                continue
            codecell = row.find('td', class_='codecol')
            if codecell is None:
                continue
            code = re.sub(r'^or\s*', '', text(codecell))
            if not re.fullmatch(r'[A-Z]{4}\d{3}[A-Z]?', code):
                raise ValueError('Unrecognized Maryland course code: ' + code)
            cells = row.find_all('td', recursive=False)
            namecell = BeautifulSoup(str(cells[1]), 'html.parser')
            approved = bool(namecell.find('sup'))
            for sup in namecell.find_all('sup'):
                sup.decompose()
            name = text(namecell).strip()
            if name.startswith('(') and name.endswith(')'):
                name = name[1:-1]
            topic = re.search(r'\b' + code + r'[A-Z]\b', name)
            item = course(code, name, source, urljoin(url, codecell.a['href']) if codecell.a else url, credits=number(row.find('td',class_='hourscol')), institution='umd',unit='semester_hours')
            if topic:
                item['id'] += '-' + topic.group().lower()
            existing = courses.get(item['id'])
            if not existing or (existing['credits'] is None and item['credits'] is not None):
                courses[item['id']] = item
            if 'orclass' in row.get('class', []):
                if last is None:
                    raise ValueError('Or row without preceding course')
                last.update(kind='choose_courses', count=1)
                if item['credits'] is None or item['credits'] != last['credits']:
                    last['credits'] = None
                last['title'] = 'Choose one: ' + last['title'] + ' or ' + code
                last['course_ids'].append(item['id'])
            elif human and code == 'GVPT170' and base['title'].startswith('Law, Policy'):
                req(key, 'Additional required American Government course', parent=base['id'], course_ids=[item['id']], summary='GVPT170 is additional to six specialization choices; this specialization totals 21 credits.')
            elif codecell.find(class_='blockindent'):
                group['course_ids'].append(item['id'])
            else:
                last = req(key, code, parent=(base if group['kind']=='choose_courses' else group)['id'], course_ids=[item['id']], credits=item['credits'])
            if approved:
                req(key+'-approval','Approved content required: '+code,kind='note',parent=base['id'],course_ids=[item['id']],summary='Catalog footnote requires approved content for this course.')
    if human:
        body = text(section)
        for trigger, label, summary in [
            ('MATH115','College requirements','ARHU college requirements also apply, including MATH115; linked college requirements are not fully reviewed.'),
            ('at least 2 courses must be from LING','Language and cognition distribution','Within six specialization choices, at least two courses must be LING and at least two PHIL.'),
        ]:
            if trigger not in body:
                raise ValueError('Maryland BA policy changed: '+trigger)
            req(slug(label),label,kind='note',parent=root['id'],summary=summary)
        math = course('MATH115',None,source,url,institution='umd',unit='semester_hours',category='mathematics')
        courses[math['id']] = math
        next(n for n in nodes if n['id']==pid+'-college-requirements')['course_ids']=[math['id']]
        # Introductory prose is deliberately not interpreted from table titles alone.
        intro = ' '.join(text(n) for n in section.find_all(['p','li']) if not n.find_parent('table'))
        if 'internship' in intro.lower():
            req('capstone-policy','Capstone and specialization timing',kind='note',parent=root['id'],summary='Select specialization by fall of junior year; capstone in final semester may be replaced by an internship. Additional prerequisites vary by specialization.')
        notes.append('Six-course specialization pools preserve the extra GVPT170 requirement and course-content approval footnotes.')
    else:
        notes.append('AI Algorithms specialization prints 12 total credits while the major specifies an 18-credit specialization and two electives. This source discrepancy requires clarification.')
    if not courses:
        raise ValueError('Maryland course rows missing')
    return dict(id=pid,title=title,award_level=award,program_kind='degree',catalog_year=catalog_year,curriculum_status='partial',courses=list(courses.values()),requirements=nodes,notes=notes,outcomes=learning_outcomes(soup,human,source))
