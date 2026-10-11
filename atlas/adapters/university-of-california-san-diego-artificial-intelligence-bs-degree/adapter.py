"""UCSD catalog AI-major sections; college graduation requirements remain unreviewed."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, requirement, text, slug
PROGRAM_ID = 'university-of-california-san-diego-artificial-intelligence-bs-degree'
SOURCES = ('https://catalog.ucsd.edu/curric/CSE-ug.html','https://cse.ucsd.edu/undergraduate/bs-artificial-intelligence-cse-bs-004','https://today.ucsd.edu/story/uc-san-diegos-new-ai-major-is-here')


def codes(value):
    found=[]
    for m in re.finditer(r'\b(CSE|MATH|PHYS|CHEM|BILD|BICD|BIMM|COGS|ESYS|HDS|SIO|ECE|ECON|DSC|PHIL|POLI|MAE|ENG|NANO|CENG|EDS|LIGN)\s+(\d+[A-Z]*)(?:[-–]([A-Z](?:-[A-Z])*|\d+[A-Z]*))?', value):
        dept,first,end=m.groups(); values=[first]
        if end:
            if end.isdigit() and first.isdigit() and int(end)-int(first)<15:
                values=[str(i) for i in range(int(first),int(end)+1)]
            elif first[-1].isalpha() and re.fullmatch(r'[A-Z](?:-[A-Z])*',end):
                stem=re.match(r'\d+',first).group(); last=end[-1]
                values=[stem+chr(i) for i in range(ord(first[-1]),ord(last)+1)]
            else:
                # Broad course-number ranges describe eligibility, not an enumerated inventory.
                continue
        found.extend(dept+' '+v for v in values)
    return list(dict.fromkeys(found))


def parse(html):
    soup=BeautifulSoup(html,'html.parser')
    h=next((h for h in soup.find_all('h3') if text(h)=='BS Artificial Intelligence Program'),None)
    if h is None: raise ValueError('UCSD AI major heading missing')
    parts=[]
    for n in h.next_siblings:
        if getattr(n,'name',None)=='h3': break
        if getattr(n,'name',None): parts.append(text(n))
    body='\n'.join(parts)
    def between(a,b):
        if a not in body or b not in body: raise ValueError('UCSD section changed: '+a)
        return body.split(a,1)[1].split(b,1)[0]
    if '124 units' not in body or 'sixty-four upper-division' not in body: raise ValueError('UCSD degree totals changed')
    sid=PROGRAM_ID+'-catalog'; records={}; nodes=[]
    def add(key,label,value='',kind='all',count=None,credits=None,parent=None,category='ai_ml',summary=None):
        ids=[]
        for code in codes(value):
            c=course(code,None,sid,SOURCES[0],category=category,institution='ucsd',unit='quarter_hours');records.setdefault(c['id'],c);ids.append(c['id'])
        node=requirement(PROGRAM_ID,key,label,sid,category=category,kind=kind,count=count,credits=credits,parent=parent,course_ids=ids,summary=summary,unit='quarter_hours');nodes.append(node);return node['id']
    root=add('major','AI major: 124 units excluding college general education',credits=124)
    lower=add('lower','Lower division',credits=60,parent=root)
    core=between('Computer Science and Engineering:', 'minimum of four units')
    # Required sequence with local alternatives stays grouped, never flattened into all courses.
    for i,entry in enumerate(re.split(r',\s*(?![^()]*\))',core.split('(twenty-two')[0].replace('Computer Science and Engineering:',''))):
        if codes(entry):add('lower-core-'+str(i),'Computing core choice' if bool(re.search(r'\bor\b', entry)) else 'Computing core',entry,kind='choose_courses' if bool(re.search(r'\bor\b', entry)) else 'all',count=1 if bool(re.search(r'\bor\b', entry)) else None,parent=lower,category='foundations')
    add('lower-elective','Lower-division computing elective',between('minimum of four units','Artificial Intelligence:'),kind='choose_credits',credits=4,parent=lower,category='electives',summary='At least four units from the named pool or an unused upper-division CSE course.')
    add('ai-foundations','AI foundations',between('Artificial Intelligence:','Mathematics:'),credits=8,parent=lower)
    math=between('Mathematics:','General Science:')
    for i,entry in enumerate(re.split(r',\s*|\band\b',math)):
        if codes(entry):add('math-'+str(i),'Mathematics choice' if bool(re.search(r'\bor\b', entry)) else 'Mathematics',entry,kind='choose_courses' if bool(re.search(r'\bor\b', entry)) else 'all',count=1 if bool(re.search(r'\bor\b', entry)) else None,parent=lower,category='mathematics')
    add('science','General science: one course',between('General Science:','Probability and Statistics:'),kind='choose_courses',count=1,credits=4,parent=lower,category='other')
    add('probability','Probability and statistics: one course',between('Probability and Statistics:','2. Upper-Division Requirements'),kind='choose_courses',count=1,credits=4,parent=lower,category='mathematics')
    upper=add('upper','Upper division',credits=64,parent=root)
    core=between('Core Courses','Ethics: Four units')
    for i,(a,b) in enumerate([('Data structures and programming:','Algorithms:'),('Algorithms:','Artificial Intelligence:'),('Artificial Intelligence:','Machine Learning:')]):
        entry=core.split(a,1)[1].split(b,1)[0];add('upper-core-'+str(i),a.rstrip(':'),entry,kind='choose_courses' if bool(re.search(r'\bor\b', entry)) else 'all',count=1 if bool(re.search(r'\bor\b', entry)) else None,parent=upper)
    add('ml','Machine learning',core.split('Machine Learning:',1)[1],parent=upper)
    add('ethics','Ethics',between('Ethics: Four units','AI Electives:'),kind='choose_credits',credits=4,parent=upper,category='human_context')
    add('ai-electives','AI electives',between('AI Electives:','Electives: Thirty-two'),kind='choose_credits',credits=12,parent=upper,summary='Twelve units from this pool, not used for other core or breadth requirements.')
    elective=add('cse-electives','CSE electives',kind='choose_credits',credits=32,parent=upper,category='electives')
    for tag in ['Systems','Theory/Abstraction','Applications of Computing']:
        add('breadth-'+slug(tag),tag+' breadth',kind='choose_credits',credits=8,parent=elective,category='electives',summary='At least eight units carrying this approved tag. Full CSE tag mapping remains unreviewed.')
    add('open-electives','Additional CSE or tagged electives',kind='choose_credits',credits=8,parent=elective,category='electives',summary='Unused upper-division or graduate CSE courses, or non-CSE courses with an approved breadth tag.')
    external=between('Cognitive Science','A maximum of twelve units of P/NP')
    for i,entry in enumerate(external.split('\n')):
        entry = re.sub(r'CSE \d+[A-Z]*', '', entry)
        if codes(entry):add('external-'+str(i),'Approved non-CSE elective pool',entry,kind='note',parent=elective,category='electives',summary='Eligibility is subject to the tag and overlap rules in the cited catalog section; this row is an option pool.')
    for key,label,trigger,summary in [
        ('elective-limit','CSE elective eligibility','CSE 100–194','CSE 100–194 may count if unused elsewhere; CSE 180, 180R and 191 are excluded. Graduate coursework needs a petition.'),
        ('topics','Topics-course limit','maximum of three times','CSE 190 and graduate analogue CSE 291 share a maximum of twelve units / three distinct topics.'),
        ('pnp','P/NP and special studies','maximum of two units of CSE 109','At most twelve P/NP units: up to eight in CSE 198/199/199H, four in CSE 197, and two in CSE 109. Exceeding the special-studies limit requires faculty-reviewed petition.'),
        ('global-ties','Global Ties limit','only take ENG 100D once','Up to eight ENG 100D/L units within the special-studies maximum; ENG 100D may count only once.'),
        ('grades','Letter grades','All courses must be taken for a letter grade','All courses require letter grades except courses offered only P/NP.'),
        ('graduate-overlap','Graduate degree reuse','may not be reused for a graduate degree','Graduate coursework counted in the undergraduate degree cannot also count in a graduate degree.')]:
        if trigger not in body:raise ValueError('UCSD policy changed: '+key)
        add(key,label,kind='note',parent=root,summary=summary)
    return dict(id=PROGRAM_ID,title='Artificial Intelligence',award_level='BS',program_kind='degree',catalog_year=None,curriculum_status='partial',courses=list(records.values()),requirements=nodes,notes=['Catalog major inventory only; college/university requirements and full approved CSE tag mapping remain unreviewed. Department page is explicitly tentative and its 2026 elective list differs from this catalog; no silent union of editions. Course titles/credits not supplied in this catalog section remain unknown.'])

from .course_metadata import parse as parse_course_metadata, URL as COURSE_URL
SOURCES = SOURCES + (COURSE_URL,)
SOURCE_PARSERS = {SOURCES[0]: parse, COURSE_URL: parse_course_metadata}

from atlas.adapters import ucsd_degree_policies as policies

def parse_course_catalog(html):
    metadata = parse_course_metadata(html)
    tags = policies.parse_tags(html)
    records = {c['id']: c for c in tags['courses']}
    for c in metadata['courses']:
        records.setdefault(c['id'], {}).update(c)
    return {'id': PROGRAM_ID, 'curriculum_status': 'partial',
            'courses': list(records.values()), 'requirements': tags['requirements']}

SOURCES += (policies.DEGREE_URL,) + tuple(policies.COLLEGE_BASE + k + '/index.html' for k in policies.COLLEGES)
SOURCE_PARSERS.update({COURSE_URL: parse_course_catalog, policies.DEGREE_URL: policies.parse_degree,
                      policies.DEPARTMENT_URL: policies.parse_department})
SOURCE_PARSERS.update({policies.COLLEGE_BASE + k + '/index.html': (lambda html, k=k: policies.parse_college(html, k)) for k in policies.COLLEGES})

from atlas.adapters import ucsd_shared_requirements as shared

def parse_degree_with_ahi(html):
    r = policies.parse_degree(html)
    extra = shared.parse_ahi(html)
    r['courses'] = extra['courses']
    r['requirements'].extend(extra['requirements'])
    return r

SOURCES += (shared.UC_WRITING_URL, shared.SENATE_URL, shared.CLIMATE_URL, shared.DEI_PDF, shared.CLIMATE_PDF)
SOURCE_PARSERS.update({shared.UC_WRITING_URL: shared.parse_uc_writing,
                      shared.SENATE_URL: shared.parse_senate,
                      shared.CLIMATE_URL: shared.parse_climate,
                      shared.DEGREE_URL: parse_degree_with_ahi})

from atlas.adapters import ucsd_revelle_pools as revelle
SOURCES += tuple(revelle.BASE + page + '.html' for page in revelle.PAGES)
SOURCE_PARSERS.update({revelle.BASE + page + '.html': parser for page, parser in revelle.PARSERS.items()})

from atlas.adapters import ucsd_muir_pools as muir
SOURCES += (muir.URL, muir.POLICY_URL)
SOURCE_PARSERS.update({muir.URL: muir.parse, muir.POLICY_URL: muir.parse_policy})

from atlas.adapters import ucsd_warren_pools as warren
SOURCES += (warren.AREA_URL, warren.TRANSFER_URL) + tuple(warren.TABLE_URLS.values())
SOURCE_PARSERS.update({warren.AREA_URL: warren.parse_area, warren.TRANSFER_URL: warren.parse_transfer})
SOURCE_PARSERS.update({url: (lambda html, key=key: warren.parse_table(html, key)) for key, url in warren.TABLE_URLS.items()})

from atlas.adapters import ucsd_marshall_pools as marshall
SOURCES += (marshall.FIRST_URL, marshall.TRANSFER_URL, marshall.WRITING_URL, marshall.SELECTOR_URL)
SOURCE_PARSERS.update({marshall.FIRST_URL: marshall.parse_first, marshall.TRANSFER_URL: marshall.parse_transfer})

from atlas.adapters import ucsd_sixth_pools as sixth
SOURCES += (sixth.PDF_URL, sixth.TRANSFER_URL, sixth.ELR_URL, sixth.PROPOSAL_URL, sixth.CAT90_URL, sixth.CAT125_URL) + tuple(sixth.TRACK_BASE + k + '.html' for k in sixth.TRACKS)
SOURCE_PARSERS.update({sixth.TRANSFER_URL: sixth.parse_transfer, sixth.ELR_URL: sixth.parse_elr_table,
                      sixth.PROPOSAL_URL: sixth.parse_proposal, sixth.CAT90_URL: sixth.parse_cat90,
                      sixth.CAT125_URL: sixth.parse_cat125})
SOURCE_PARSERS.update({sixth.TRACK_BASE + key + '.html': (lambda html, key=key: sixth.parse_track(html, key)) for key in sixth.TRACKS})

from atlas.adapters import ucsd_roosevelt_pools as roosevelt
SOURCES += (roosevelt.GE_URL, roosevelt.GRAD_URL, roosevelt.WRITING_URL) + tuple(roosevelt.REGION_URLS.values())
SOURCE_PARSERS.update({roosevelt.GE_URL: roosevelt.parse_ge, roosevelt.GRAD_URL: roosevelt.parse_graduation,
                      roosevelt.WRITING_URL: roosevelt.parse_writing})
SOURCE_PARSERS.update({url: (lambda html, key=key: roosevelt.parse_region(html, key)) for key, url in roosevelt.REGION_URLS.items()})

from atlas.adapters import ucsd_eighth_pools as eighth
SOURCES += (eighth.FIRST_URL, eighth.TRANSFER_URL, eighth.TABLE_URL)
SOURCE_PARSERS.update({eighth.FIRST_URL: eighth.parse_first, eighth.TRANSFER_URL: eighth.parse_transfer,
                      eighth.TABLE_URL: eighth.parse_table})

from atlas.adapters import ucsd_seventh_pools as seventh
SOURCES += (seventh.FIRST_URL, seventh.TRANSFER_URL)
SOURCE_PARSERS.update({seventh.FIRST_URL: seventh.parse_first, seventh.TRANSFER_URL: seventh.parse_transfer})

from atlas.adapters import ucsd_transfer_options as transfer_options
SOURCES += (transfer_options.HUM_URL, transfer_options.REVELLE_URL, transfer_options.MARSHALL_URL)
SOURCE_PARSERS.update({transfer_options.HUM_URL: transfer_options.parse_humanities,
                      transfer_options.REVELLE_URL: transfer_options.parse_revelle_transfer,
                      transfer_options.MARSHALL_URL: transfer_options.parse_marshall_service})

from atlas.adapters import ucsd_exam_credit as exam_credit
SOURCES += (exam_credit.AP_URL, exam_credit.IB_URL, exam_credit.WARREN_URL)
SOURCE_PARSERS.update({exam_credit.WARREN_URL: exam_credit.parse_warren})

from atlas.adapters import ucsd_warren_disciplines as warren_disciplines
SOURCES += tuple(warren_disciplines.URLS.values())
SOURCE_PARSERS.update({url: (lambda html, key=key: warren_disciplines.parse(html, key))
                      for key, url in warren_disciplines.URLS.items()})

from atlas.adapters import ucsd_warren_languages as warren_languages
SOURCES += (warren_languages.CHIN_URL, warren_languages.JAPN_URL, warren_languages.CLX_URL)
SOURCE_PARSERS.update({warren_languages.CHIN_URL: warren_languages.parse_chinese,
                      warren_languages.JAPN_URL: warren_languages.parse_japanese,
                      warren_languages.CLX_URL: warren_languages.parse_chicanx})

from atlas.adapters import uc_policy_closure as policy_closure
SOURCES += (policy_closure.PETITION_URL, policy_closure.LANGUAGE_URL, policy_closure.CALGETC_URL)
SOURCE_PARSERS.update({policy_closure.PETITION_URL: policy_closure.parse_petition,
                      policy_closure.LANGUAGE_URL: policy_closure.parse_language,
                      policy_closure.CALGETC_URL: policy_closure.parse_calgetc})

from .course_metadata import parse_math, MATH_URL
SOURCES += (MATH_URL,)
SOURCE_PARSERS[MATH_URL] = parse_math

# Subject observations are independent of requirement/pool membership.
from atlas.adapters.west_degree_subjects import observe as observe_subjects
parse = observe_subjects(parse, PROGRAM_ID)
SOURCE_PARSERS = {url: observe_subjects(parser, PROGRAM_ID) for url, parser in SOURCE_PARSERS.items()}

# Add the separately reviewed remaining CSE descriptions after the legacy subject
# wrapper, retaining core metadata and all source tag/choice observations.
from atlas.adapters import ucsd_cse_remaining_reviews as remaining_cse
_previous_cse_parser = SOURCE_PARSERS[COURSE_URL]

def parse_all_reviewed_cse(html):
    original = _previous_cse_parser(html)
    extra = remaining_cse.parse_observations(html)
    records = {c['id']: dict(c) for c in original['courses']}
    if len(records) != len(original['courses']):
        raise ValueError('Duplicate original UCSD course identities')
    seen = set()
    for c in extra['courses']:
        if c['id'] in seen:
            raise ValueError('Duplicate reviewed UCSD course identity')
        seen.add(c['id'])
        # The handoff excludes the eight previously reviewed core codes.
        if c['code'] in {'CSE 12','CSE 30','CSE 25','CSE 55','CSE 100','CSE 101','CSE 150A','CSE 151A'}:
            raise ValueError('Remaining CSE observer overlaps core ownership')
        records.setdefault(c['id'], {}).update(c)
    return {**original, 'courses': list(records.values())}

SOURCE_PARSERS[COURSE_URL] = parse_all_reviewed_cse

# Independent current PHIL/ECON blocks have no pre-existing same-URL observer.
# Keep held/missing identities as dispositions; never replay manual reviews.
from atlas.adapters import ucsd_phil_econ_reviews as phil_econ_reviews
for _review_url, _review_parser in phil_econ_reviews.SOURCE_PARSERS.items():
    if _review_url in SOURCE_PARSERS:
        raise ValueError('UCSD PHIL/ECON source needs explicit parser composition')
    SOURCES += (_review_url,)
    SOURCE_PARSERS[_review_url] = _review_parser

# Delegated current social-science descriptions preserve conditional college
# membership; these observers emit facts and dispositions, never manual audits.
from atlas.adapters import ucsd_soci_reviews as soci_reviews
from atlas.adapters import ucsd_anth_ansc_reviews as anth_ansc_reviews
for _review_module in (soci_reviews, anth_ansc_reviews):
    for _review_url, _review_parser in _review_module.SOURCE_PARSERS.items():
        if _review_url in SOURCE_PARSERS:
            raise ValueError('UCSD social-science source needs explicit parser composition')
        SOURCES += (_review_url,)
        SOURCE_PARSERS[_review_url] = _review_parser

from atlas.adapters import ucsd_ethn_reviews as ethn_reviews
for _review_url, _review_parser in ethn_reviews.SOURCE_PARSERS.items():
    if _review_url in SOURCE_PARSERS:
        raise ValueError('UCSD ETHN source needs explicit parser composition')
    SOURCES += (_review_url,)
    SOURCE_PARSERS[_review_url] = _review_parser

from atlas.adapters import ucsd_vis_reviews as vis_reviews
for _review_url, _review_parser in vis_reviews.SOURCE_PARSERS.items():
    if _review_url in SOURCE_PARSERS:
        raise ValueError('UCSD VIS source needs explicit parser composition')
    SOURCES += (_review_url,)
    SOURCE_PARSERS[_review_url] = _review_parser

from atlas.adapters import ucsd_poli_reviews as poli_reviews
for _review_url, _review_parser in poli_reviews.SOURCE_PARSERS.items():
    if _review_url in SOURCE_PARSERS:
        raise ValueError('UCSD POLI source needs explicit parser composition')
    SOURCES += (_review_url,)
    SOURCE_PARSERS[_review_url] = _review_parser

from atlas.adapters import ucsd_hieu_reviews as hieu_reviews
for _review_url, _review_parser in hieu_reviews.SOURCE_PARSERS.items():
    if _review_url in SOURCE_PARSERS:
        raise ValueError('UCSD History source needs explicit subject-parser composition')
    SOURCES += (_review_url,)
    SOURCE_PARSERS[_review_url] = _review_parser

from atlas.adapters import ucsd_usp_reviews as usp_reviews
for _review_url, _review_parser in usp_reviews.SOURCE_PARSERS.items():
    if _review_url in SOURCE_PARSERS:
        raise ValueError('UCSD USP source needs explicit parser composition')
    SOURCES += (_review_url,)
    SOURCE_PARSERS[_review_url] = _review_parser

from atlas.adapters import ucsd_comm_reviews as comm_reviews
for _review_url, _review_parser in comm_reviews.SOURCE_PARSERS.items():
    if _review_url in SOURCE_PARSERS:
        raise ValueError('UCSD COMM source needs explicit parser composition')
    SOURCES += (_review_url,)
    SOURCE_PARSERS[_review_url] = _review_parser

from atlas.adapters import ucsd_chin_reviews as chin_reviews
_CHIN_URL = chin_reviews.SPEC['sources']['CHIN']['url']
_CHIN_MEMBERSHIP_PARSER = SOURCE_PARSERS[_CHIN_URL]

def parse_reviewed_chinese(html):
    result = _CHIN_MEMBERSHIP_PARSER(html)
    content = chin_reviews.parse_observations(html)
    courses = {c['id']: c for c in result['courses']}
    for observation in content['courses']:
        if observation['id'] not in courses:
            raise ValueError('Reviewed Chinese content has no observed membership')
        courses[observation['id']].update(observation)
    return {**result, 'courses': list(courses.values()),
            'source_dispositions': content['source_dispositions']}

SOURCE_PARSERS[_CHIN_URL] = parse_reviewed_chinese

# Anthropology's shared URL must retain the earlier ANTH/ANSC observations.
from atlas.adapters import ucsd_anar_reviews as anar_reviews

def parse_reviewed_anthropology(html):
    outputs = [anth_ansc_reviews.parse_observations(html), anar_reviews.parse_observations(html)]
    courses = [c for result in outputs for c in result['courses']]
    if len({c['id'] for c in courses}) != len(courses):
        raise ValueError('Duplicate reviewed Anthropology course ID')
    return {'id': PROGRAM_ID, 'courses': courses,
            'source_dispositions': [d for result in outputs for d in result['source_dispositions']]}

_ANTHROPOLOGY_URL = anar_reviews.SPEC['sources']['ANAR']['url']
if _ANTHROPOLOGY_URL not in SOURCE_PARSERS:
    raise ValueError('Expected existing Anthropology source observer')
SOURCE_PARSERS[_ANTHROPOLOGY_URL] = parse_reviewed_anthropology

# One History chapter supplies disjoint bounded subject inventories. Preserve
# every prior observer and guard each subject's actual section-level rules.
from atlas.adapters import ucsd_hila_reviews as hila_reviews
from atlas.adapters import ucsd_hius_hiea_reviews as hius_hiea_reviews

def parse_reviewed_history(html):
    outputs = [module.parse_observations(html) for module in
               (hieu_reviews, hila_reviews, hius_hiea_reviews)]
    courses = [course for output in outputs for course in output['courses']]
    if len({course['id'] for course in courses}) != len(courses):
        raise ValueError('Duplicate reviewed History course ID')
    return {'id': PROGRAM_ID, 'courses': courses,
            'source_dispositions': [item for output in outputs for item in output['source_dispositions']]}

_HISTORY_URL = hieu_reviews.SPEC['sources']['HIEU']['url']
SOURCE_PARSERS[_HISTORY_URL] = parse_reviewed_history

from atlas.adapters import ucsd_sio_reviews as sio_reviews
for _review_url, _review_parser in sio_reviews.SOURCE_PARSERS.items():
    if _review_url in SOURCE_PARSERS:
        raise ValueError('UCSD SIO source needs explicit parser composition')
    SOURCES += (_review_url,)
    SOURCE_PARSERS[_review_url] = _review_parser

from atlas.adapters import ucsd_eds_reviews as eds_reviews
for _review_url, _review_parser in eds_reviews.SOURCE_PARSERS.items():
    if _review_url in SOURCE_PARSERS:
        raise ValueError('UCSD EDS source needs explicit parser composition')
    SOURCES += (_review_url,)
    SOURCE_PARSERS[_review_url] = _review_parser

from atlas.adapters import ucsd_cgs_reviews as cgs_reviews
from atlas.adapters import ucsd_mus_reviews as mus_reviews
for _review_module in (cgs_reviews, mus_reviews):
    for _review_url, _review_parser in _review_module.SOURCE_PARSERS.items():
        if _review_url in SOURCE_PARSERS:
            raise ValueError('UCSD CGS/MUS source needs explicit parser composition')
        SOURCES += (_review_url,)
        SOURCE_PARSERS[_review_url] = _review_parser

from atlas.adapters import ucsd_biology_reviews as biology_reviews
from atlas.adapters import ucsd_glbh_reviews as glbh_reviews
for _review_module in (biology_reviews, glbh_reviews):
    for _review_url, _review_parser in _review_module.SOURCE_PARSERS.items():
        if _review_url in SOURCE_PARSERS:
            raise ValueError('UCSD Biology/GLBH source needs explicit parser composition')
        SOURCES += (_review_url,)
        SOURCE_PARSERS[_review_url] = _review_parser

# Two legacy core-option records were outside the remaining-CSE handoff and
# lacked manual content decisions. Overlay guarded facts without losing tags.
from atlas.adapters import ucsd_cse_core_options_reviews as core_option_reviews
_PREVIOUS_COMPLETE_CSE_PARSER = SOURCE_PARSERS[COURSE_URL]

def parse_cse_with_reviewed_core_options(html):
    result = _PREVIOUS_COMPLETE_CSE_PARSER(html)
    courses = {course['id']: course for course in result['courses']}
    for observation in core_option_reviews.parse_observations(html)['courses']:
        if observation['id'] not in courses:
            raise ValueError('Reviewed CSE core option lacks existing source identity')
        courses[observation['id']].update(observation)
    return {**result, 'courses': list(courses.values())}

SOURCE_PARSERS[COURSE_URL] = parse_cse_with_reviewed_core_options

from atlas.adapters import ucsd_psyc_reviews as psyc_reviews
for _review_url, _review_parser in psyc_reviews.SOURCE_PARSERS.items():
    if _review_url in SOURCE_PARSERS:
        raise ValueError('UCSD Psychology source needs explicit parser composition')
    SOURCES += (_review_url,)
    SOURCE_PARSERS[_review_url] = _review_parser

from atlas.adapters import ucsd_history_remaining_reviews as history_remaining_reviews
_PREVIOUS_HISTORY_PARSER = SOURCE_PARSERS[_HISTORY_URL]

def parse_all_reviewed_history(html):
    outputs = [_PREVIOUS_HISTORY_PARSER(html), history_remaining_reviews.parse_observations(html)]
    courses = [course for result in outputs for course in result['courses']]
    if len({course['id'] for course in courses}) != len(courses):
        raise ValueError('Duplicate complete History course ID')
    return {'id': PROGRAM_ID, 'courses': courses,
            'source_dispositions': [item for result in outputs for item in result['source_dispositions']]}

SOURCE_PARSERS[_HISTORY_URL] = parse_all_reviewed_history

from atlas.adapters import ucsd_linguistics_reviews as linguistics_reviews
from atlas.adapters import ucsd_physics_astronomy_reviews as physics_astronomy_reviews
for _review_module in (linguistics_reviews, physics_astronomy_reviews):
    for _review_url, _review_parser in _review_module.SOURCE_PARSERS.items():
        if _review_url in SOURCE_PARSERS:
            raise ValueError('UCSD Linguistics/Physics/Astronomy source needs explicit parser composition')
        SOURCES += (_review_url,)
        SOURCE_PARSERS[_review_url] = _review_parser

from atlas.adapters import ucsd_chem_reviews as chem_reviews
for _review_url, _review_parser in chem_reviews.SOURCE_PARSERS.items():
    if _review_url in SOURCE_PARSERS:
        raise ValueError('UCSD Chemistry source needs explicit parser composition')
    SOURCES += (_review_url,)
    SOURCE_PARSERS[_review_url] = _review_parser
