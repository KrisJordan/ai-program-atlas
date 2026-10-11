"""Current Boston BSChE catalog; no unverified family or college-policy inheritance."""
from atlas.adapters.northeastern_courseleaf import parse_catalog
PROGRAM_ID = 'northeastern-chemical-engineering-ai-bsche'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/engineering/chemical/chemical-engineering-artificial-intelligence-bsche-bos/',)
TITLE = 'Chemical Engineering and Artificial Intelligence, BSChE (Boston)'
SECTIONS = ['Universitywide Requirements', 'NUpath Requirements', 'Engineering Requirements', 'Artificial Intelligence Courses', 'Supporting Courses: Mathematics/Science', 'Professional Development', 'Writing Requirements', 'Integrative Course', 'Required General Electives', 'Major GPA Requirement', 'Program Requirement']
def parse(html):
    result = parse_catalog(html, program_id=PROGRAM_ID, title=TITLE, url=SOURCES[0], required_sections=SECTIONS, award_level='other', outcome_claims=[('development of predictive models, optimization of processes, and the design of experiments', 'The program aims to apply AI to chemical-engineering prediction, process optimization and experimental design.')])
    # This BSChE paragraph says co-op MAY satisfy EX; preserve its conditionality.
    from bs4 import BeautifulSoup
    from atlas.adapters.northeastern_courseleaf import clean
    panel = BeautifulSoup(html, 'html.parser').find(id='programrequirementstextcontainer')
    policy = next((clean(p) for p in panel.find_all('p') if 'not explicitly satisfied by required engineering coursework' in clean(p)), None)
    if not policy or not all(token in policy for token in ('(IC)', '(SI)', '(DD)', '(EX)', 'may fulfill the EX requirement')):
        raise ValueError('Changed BSChE NUpath applicability policy')
    for requirement in result['requirements']:
        if requirement['summary'] == 'Co-op fulfills the experiential NUpath category.':
            requirement['summary'] = 'Required engineering coursework does not explicitly satisfy NUpath IC, SI, DD or EX. A successful co-op may fulfill EX; students must cover remaining categories with general electives.'
    for outcome in result['outcomes']: outcome['statement_type'] = 'program_aim'
    return result
