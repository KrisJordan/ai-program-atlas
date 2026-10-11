"""Individually reviewed science concurrency; preserve each exact choice branch.

This is a finite source-specific profile, not recursive prerequisite expansion.
Degree and subject observations have independent applicability/evidence guards.
"""
import re
from bs4 import BeautifulSoup
from atlas.adapters.northeastern_courseleaf import clean
from atlas.adapters.northeastern_course_metadata import parse_subject, SUBJECT_HEADINGS

# Anchor suffix, existing course pair, direct parent suffix, direct parent kind,
# reviewed role, concurrent course codes. No new top-level obligations.
PROFILES = {
    'biology': [
        ('chem-1161-chem-1162',['CHEM 1161','CHEM 1162'],'chemistry','all','required',['CHEM 1163']),
        ('phys-1151',['PHYS 1151'],'phys-1145-phys-1146-alternatives','alternative','options',['PHYS 1152','PHYS 1153']),
        ('phys-1161',['PHYS 1161'],'phys-1145-phys-1146-alternatives','alternative','options',['PHYS 1162','PHYS 1163']),
    ],
    'biochemistry': [
        ('chem-1161-chem-1162',['CHEM 1161','CHEM 1162'],'chemistry-foundations','all','required',['CHEM 1163']),
    ],
    'chemistry': [
        ('chem-2161-chem-2162',['CHEM 2161','CHEM 2162'],'general-chemistry','all','required',['CHEM 2163']),
        ('chem-2321-chem-2322',['CHEM 2321','CHEM 2322'],'analytical-chemistry','all','required',['CHEM 2323']),
        ('chem-2315-chem-2316',['CHEM 2315','CHEM 2316'],'organic-chemistry-course-choice','alternative','options',['CHEM 2324']),
        ('chem-2317-chem-2318',['CHEM 2317','CHEM 2318'],'organic-chemistry-course-choice-2','alternative','options',['CHEM 2325']),
    ],
    'ecology-and-evolutionary-biology': [
        ('phys-1161-phys-1162',['PHYS 1161','PHYS 1162'],'physics-course-choice','alternative','options',['PHYS 1163']),
    ],
}
# Exact content statements reviewed in the current official subject catalogs.
CONDITIONS = {
    'CHEM 1161': 'Corequisite(s): CHEM 1162 , CHEM 1163',
    'CHEM 1163': 'Corequisite(s): CHEM 1161 , CHEM 1162',
    'CHEM 2161': 'Corequisite(s): CHEM 2162 , CHEM 2163',
    'CHEM 2163': 'Corequisite(s): CHEM 2161 , CHEM 2162',
    'CHEM 2321': 'Corequisite(s): CHEM 2322 , CHEM 2323',
    'CHEM 2323': 'Corequisite(s): CHEM 2321 , CHEM 2322',
    'CHEM 2315': 'Corequisite(s): CHEM 2316 , CHEM 2324',
    'CHEM 2324': 'Corequisite(s): CHEM 2315 , CHEM 2316',
    'CHEM 2317': 'Corequisite(s): CHEM 2318 , CHEM 2325',
    'CHEM 2325': 'Corequisite(s): CHEM 2317 , CHEM 2318',
    'PHYS 1151': 'Corequisite(s): PHYS 1153',
    'PHYS 1152': 'Requires concurrent registration in PHYS 1151 and PHYS 1153 .',
    'PHYS 1153': 'Requires concurrent registration in PHYS 1151 and PHYS 1152 .',
    'PHYS 1161': 'Corequisite(s): PHYS 1162 , PHYS 1163',
    'PHYS 1162': 'Corequisite(s): PHYS 1161 , PHYS 1163',
    'PHYS 1163': 'Corequisite(s): PHYS 1161 , PHYS 1162',
}
FACTS = {
    'CHEM 1163': ('Recitation for CHEM 1161',0),
    'CHEM 2163': ('Recitation for CHEM 2161',0),
    'CHEM 2323': ('Recitation for CHEM 2321',0),
    'CHEM 2324': ('Recitation for CHEM 2315',0),
    'CHEM 2325': ('Recitation for CHEM 2317',0),
    'PHYS 1152': ('Lab for PHYS 1151',1),
    'PHYS 1153': ('Interactive Learning Seminar for PHYS 1151',1),
    'PHYS 1162': ('Lab for PHYS 1161',1),
    'PHYS 1163': ('Recitation for PHYS 1161',0),
}

def course_id(pid, code):
    return pid+'-'+code.lower().replace(' ','-')


def guard_degree(parse, pid, profiles):
    def observe(html):
        result=parse(html)
        panel=BeautifulSoup(html,'html.parser').find(id='programrequirementstextcontainer')
        if panel is None or 'Also complete any corequisite labs, recitations, clinicals, or tools courses where specified' not in clean(panel):
            raise ValueError('Science degree corequisite policy changed')
        groups={r['id']:r for r in result['requirements']}
        for anchor,codes,parent,parent_kind,role,targets in profiles:
            node=groups.get(pid+'-req-'+anchor)
            if not node or node['kind']!='all' or node['course_ids']!=[course_id(pid,c) for c in codes] or node['parent_id']!=pid+'-req-'+parent:
                raise ValueError('Reviewed science lecture/bundle identity changed')
            if groups[node['parent_id']]['kind']!=parent_kind:
                raise ValueError('Science choice-parent role changed')
            kinds=[]
            while node:
                kinds.append(node['kind']);node=groups.get(node['parent_id']) if node.get('parent_id') else None
            observed='unresolved' if 'note' in kinds else 'options' if any(k in {'alternative','choose_courses','choose_credits'} for k in kinds) else 'required'
            if observed!=role:raise ValueError('Science concurrent ancestry changed')
        return result
    return observe


def observe_subject(html, pid, subject, profiles, existing):
    result=existing(html)
    soup=BeautifulSoup(html,'html.parser')
    blocks={clean(b.find(class_='courseblocktitle')).split('.',1)[0]:b for b in soup.select('#textcontainer .courseblock') if b.find(class_='courseblocktitle')}
    compact=lambda value: re.sub(r'\s+','',value)
    selected=list(dict.fromkeys(c for p in profiles for c in p[5]))
    for anchor,codes,parent,parent_kind,role,targets in profiles:
        for code in [codes[0],*targets]:
            block=blocks.get(code)
            if block is None:raise ValueError('Science concurrent evidence block missing')
            expected=CONDITIONS[code]
            if expected.startswith('Corequisite(s):'):
                actual=[clean(x) for x in block.find_all(class_='courseblockextra')]
                valid=compact(expected) in [compact(x) for x in actual]
            else:
                valid=compact(expected) in compact(clean(block.find(class_='cb_desc')))
            if not valid:raise ValueError('Science concurrent evidence changed')
    extra=parse_subject(html,program_id=pid,subject=subject,heading=SUBJECT_HEADINGS[subject],codes=selected,url=f'https://catalog.northeastern.edu/course-descriptions/{subject.lower()}/')
    for course in extra['courses']:
        if (course['name'],course['credits'])!=FACTS[course['code']]:raise ValueError('Science concurrent course identity/hours changed')
        if course['id'] in {c['id'] for c in result['courses']}:raise ValueError('Duplicate concurrent course observation')
    result['courses']+=extra['courses'];result['notes']+=extra['notes']
    for anchor,codes,parent,parent_kind,role,targets in profiles:
        result['requirements'].append(dict(id=pid+'-req-'+anchor+'-concurrent',parent_id=pid+'-req-'+anchor,
            title='Concurrent courses for '+', '.join(codes),kind='all',count=None,credits=None,
            credit_unit='semester_hours',category='other',source_id=pid+'-'+subject.lower()+'-courses',source_text=None,
            summary='Explicit subject-catalog concurrency applies when this lecture/pair is taken. The degree requires specified corequisite labs/recitations; these courses inherit this exact branch and are not unrelated prerequisite obligations.',
            course_ids=[course_id(pid,c) for c in targets]))
    return result


def register_science_corequisites(parse, parsers, pid, partner):
    profiles=PROFILES[partner];result=dict(parsers)
    for subject in {p[1][0].split()[0] for p in profiles}:
        url=f'https://catalog.northeastern.edu/course-descriptions/{subject.lower()}/'
        selected=[p for p in profiles if p[1][0].split()[0]==subject];existing=parsers[url]
        def observe(html,subject=subject,profiles=selected,existing=existing):
            return observe_subject(html,pid,subject,profiles,existing)
        result[url]=observe
    return guard_degree(parse,pid,profiles),result
