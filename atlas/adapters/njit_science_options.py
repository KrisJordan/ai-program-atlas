"""NJIT's published science option relationships, not an exhaustive GER audit."""
import re
from functools import partial
from atlas.adapters.national_curriculum_common import content, clean, course, rule, require_phrases
from atlas.adapters.njit_degree_policies import PID, observed

BASE = 'https://catalog.njit.edu/undergraduate/science-liberal-arts/'
SOURCES_BY_KIND = {
    'physics': (BASE + 'physics/', 'Physics', [f'PHYS {n}' for n in ('102', '102A', '103', '103A', '111', '111A', '121', '121A', '202', '202A', '203', '203A')]),
    'chemistry': (BASE + 'chemistry-environmental-science/', 'Chemistry and Environmental Science', ['CHEM 121', 'CHEM 122', 'CHEM 125', 'CHEM 125A', 'CHEM 126', 'CHEM 126A']),
    'biology': (BASE + 'biology/', 'Biological Sciences', ['BIOL 150']),
}
# Conditions are attached to selected options, never added as universal degree requirements.
RELATIONSHIPS = {
    'PHYS 102A': (['PHYS 102'], ['Corequisite: PHYS 102', 'must be taken concurrently'], 'Take PHYS 102 concurrently with its PHYS 102A laboratory.'),
    'PHYS 103A': (['PHYS 103'], ['Corequisite: PHYS 103', 'must be taken concurrently'], 'Take PHYS 103 concurrently with PHYS 103A; its separately stated prerequisite sequence and grade condition also apply.'),
    'PHYS 111A': (['PHYS 111'], ['Corequisite: PHYS 111', 'must be taken concurrently'], 'Take PHYS 111 concurrently with PHYS 111A; the lecture also names MATH 111 as a corequisite.'),
    'PHYS 121A': (['PHYS 121'], ['Corequisites: PHYS 121 or PHYS 122', 'must be taken concurrently'], 'PHYS 121A requires concurrent PHYS 121 or PHYS 122 and its stated prerequisites. PHYS 121 is in the reviewed GER pool; this course-description alternative does not add PHYS 122 to that pool.'),
    'PHYS 202A': (['PHYS 202'], ['Optional laboratory course associated with PHYS 202'], 'PHYS 202A is an optional lab associated with PHYS 202. The description does not state a concurrent-enrollment requirement; none is invented.'),
    'PHYS 203A': (['PHYS 203'], ['Corequisite: PHYS 203', 'Optional laboratory course associated with PHYS 203'], 'The optional PHYS 203A laboratory has PHYS 203 as a corequisite.'),
    'CHEM 125A': (['CHEM 125', 'CHEM 121'], ['Corequisites: CHEM 125 or CHEM 121'], 'CHEM 125A permits either CHEM 125 or CHEM 121 as its corequisite lecture, not both.'),
    'CHEM 126A': (['CHEM 126', 'CHEM 122'], ['CHEM 125A with a grade of C or better', 'Corequisites: CHEM 126 or CHEM 122'], 'CHEM 126A requires CHEM 125A with C or better and either CHEM 126 or CHEM 122 concurrently.'),
    'BIOL 150': ([], ['This laboratory course'], 'BIOL 150 is explicitly described as a laboratory course, with lecture and laboratory contact hours in its catalog heading.'),
}


def parse_science(html, kind):
    url, heading, wanted = SOURCES_BY_KIND[kind]
    root = content(html, heading)
    sid = PID + '-science-' + kind
    found = {}
    for block in root.find_all(class_='courseblock'):
        title = block.find(class_='courseblocktitle')
        if title is None:
            continue
        text = clean(title.get_text(' ', strip=True))
        match = re.match(r'^([A-Z]+\d* \d+[A-Z]?)\.\s+(.+?)\.\s+(\d+) credits?,', text)
        code = text.split('.')[0]
        if code not in wanted:
            continue
        if not match or code in found:
            raise ValueError('Changed or duplicate NJIT science course header: ' + code)
        desc_node = block.find(class_='courseblockdesc')
        if desc_node is None:
            raise ValueError('Missing NJIT science course description: ' + code)
        desc = clean(desc_node.get_text(' ', strip=True))
        c = course('njit', code, match[2], sid, url, credits=int(match[3]),unit='semester_hours')
        # Only explicit preparation clauses; absence remains null, not "none".
        clauses = re.findall(r'((?:Pre|Co-?)requisites?:\s*.*?)(?:\.\s|\.$|$)', desc, re.I)
        c['prerequisites'] = '; '.join(clean(clause) for clause in clauses) or None
        found[code] = (c, block)
    if set(found) != set(wanted):
        raise ValueError('Missing reviewed NJIT science option: ' + ', '.join(sorted(set(wanted) - set(found))))
    rules = []
    for lab, (lectures, phrases, summary) in RELATIONSHIPS.items():
        if lab not in found:
            continue
        require_phrases(found[lab][1], phrases)
        ids = [found[code][0]['id'] for code in [lab, *lectures]]
        rules.append(rule(PID + '-science-option-' + lab.lower().replace(' ', '-'), lab + ' laboratory relationship', sid, ids, kind='note', summary='Conditional when selecting this GER option; not an additional required course group. ' + summary))
    return observed(rules, [found[code][0] for code in wanted])


SOURCE_PARSERS = {url: partial(parse_science, kind=kind) for kind, (url, _, _) in SOURCES_BY_KIND.items()}
