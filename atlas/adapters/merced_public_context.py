"""Public program context; unavailable curricula are never synthesized from prose."""
from atlas.adapters.national_curriculum_common import content, require_phrases

AI_URL='https://www.ucmerced.edu/majors-and-minors/artificial-intelligence-bs'
CSE_URL='https://engineering.ucmerced.edu/academics/undergraduate-programs/computer-science-and-engineering-plo'
AI_AIMS=[
    'Study intelligent systems that perceive, reason, learn and make decisions.',
    'Develop mathematical and computational foundations for machine learning, language processing and robotics.',
    'Address societal questions involving algorithmic bias, privacy and responsible automation.',
]
CSE_OUTCOMES=[
    'Host CSE program: analyze computing problems and apply relevant disciplinary principles.',
    'Host CSE program: design, build and assess computing solutions against requirements.',
    'Host CSE program: communicate in professional settings.',
    'Host CSE program: make ethical and legally informed professional judgments.',
    'Host CSE program: collaborate and lead in appropriate team activities.',
    'Host CSE program: use computing theory and software-development foundations to construct solutions.',
]

def statement(text,kind,sid,locator):
    return dict(text=text,kind='source_stated',statement_type=kind,source_id=sid,locator=locator)


def parse_ai(html):
    root=content(html,'UC Merced Artificial Intelligence Program')
    require_phrases(root,['perceiving, reasoning, learning','algorithmic bias, data privacy','Artificial Intelligence is a new major, so there are no alumni yet','AI/Machine Learning Engineer','Data Scientist','Software Developer'])
    outcomes=[statement(t,'program_aim','uc-merced-ai-bs-context','Overview and UC Merced Artificial Intelligence Program') for t in AI_AIMS]
    outcomes.append(statement('Illustrative career pathways include AI/ML engineering, data science and software development; some roles may require further education. These are possibilities, not observed graduate outcomes.','career_pathway','uc-merced-ai-bs-context','Careers; no AI-major alumni yet; further-education caveat'))
    return dict(id='uc-merced-ai-bs',outcomes=outcomes)


def parse_cse(html):
    root=content(html,'Computer Science and Engineering Program Learning Outcomes')
    require_phrases(root,['Analyze a complex computing problem','Design, implement, and evaluate','Communicate effectively','legal and ethical principles','member or leader of a team','computer science theory and software development fundamentals'])
    outcomes=[statement(t,'learning_outcome','uc-merced-cse-ai-emphasis-host-outcomes','Six host CSE degree learning outcomes; not AI-emphasis-specific statements') for t in CSE_OUTCOMES]
    return dict(id='uc-merced-cse-ai-emphasis',outcomes=outcomes)
