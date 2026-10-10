"""Observed official subject-catalog metadata for explicitly reviewed course codes."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.northeastern_courseleaf import clean, slug, numeric, category

# Short editorial summaries of the linked official descriptions. Each has a
# source phrase guard; changed prose cannot silently replay an unsupported summary.
SUMMARIES = {
    'SLPA 1101': ('assessment and treatment of disorders', 'Introduces speech, language and hearing disorders, their assessment and treatment, and clinical observation.'),
    'SLPA 4500': ('children and adults with frequently referred language disorders', 'Studies language disorders across ages, their neurological bases and approaches to assessment and intervention.'),
    'SLPA 5107': ('functional analysis of behavior', 'Applies behavioral analysis and experimental methods to clinical assessment and communication-disorder treatment.'),
    'COMM 1101': ('major theories and methodological approaches', 'Introduces communication research, theoretical approaches and ethical questions in social contexts.'),
    'COMM 2625': ('design, use, and critical study of communication technologies', 'Examines communication technology through its design, history and relationships with social institutions.'),
    'COMM 4608': ('research and writing capstone project', 'Develops a sustained strategic-communication research project integrating theory, methods and professional writing.'),
    'JRNL 1101': ('fundamental reporting skills', 'Introduces news reporting and writing through interviews, observation, research and critical analysis.'),
    'JRNL 3700': ('data-driven storytelling projects', 'Develops data-journalism projects using analysis, visualization and tools for communicating quantitative evidence.'),
    'JRNL 5500': ('data-driven, multimodal, web-based storytelling', 'Develops coding skills for web and data storytelling through collaborative projects and analysis of published examples.'),
    'SOCL 3300': ('classical and contemporary sociology', 'Connects classical traditions of social thought with contemporary sociological theory.'),
    'SOCL 4600': ('conducting original research', 'Integrates sociology study through an original research paper and collaborative seminar feedback.'),
    'CRIM 3600': ('research design', 'Develops and critiques research questions, methods and designs in criminology and criminal justice.'),
    'CRIM 3700': ('computational social science techniques', 'Applies statistical and computational methods, existing datasets and visualization to crime and justice questions.'),
    'CRIM 4949': ('propose a policy solution', 'Investigates a crime or justice-system problem and develops a policy proposal in a capstone project.'),
    'INTL 2600': ('impact world politics', 'Examines AI in international relations, state policy, humanitarian activity, security and ethical/legal debates.'),
    'INTL 4700': ('final paper and presentation', 'Integrates international-affairs coursework and experience through research, reflection, writing and a final presentation.'),
    'CIVE 4765': ('design a civil engineering project', 'Develops an environmental engineering design in teams with faculty/practitioner guidance and presentations to stakeholders.'),
    'GE 1501': ('engineering design process and algorithmic thinking', 'Introduces engineering design and programming through projects, laboratories and an original design solution.'),
    'GE 1502': ('quantitative tools and ethical topics', 'Continues project-based engineering design with analysis, programming, ethical reasoning and working prototypes.'),

    'DS 3000': ('linear algebra and probability', 'Studies the mathematical basis of AI through linear algebra, probability and computational exercises.'),
    'DS 3500': ('data-centric pipelines', 'Develops robust software architectures and data pipelines using substantial datasets.'),
    'DS 4200': ('design and evaluation process of visualization', 'Studies how to design, implement and evaluate visual representations of data.'),
    'DS 4300': ('distributed databases', 'Studies scalable data storage, distributed databases and retrieval methods.'),
    'DS 4400': ('supervised and unsupervised', 'Introduces predictive modeling and major supervised and unsupervised learning methods.'),
    'DS 4420': ('mathematical and computational foundations', 'Studies advanced learning methods and their mathematical and computational foundations.'),
    'DS 4440': ('stochastic gradient descent and backpropagation', 'Introduces neural-network training, architectures and practical applications with modern software tools.'),
    'LING 1150': ('scientific study of language', 'Surveys language science, including speech sounds, word and sentence structure, and meaning.'),
    'LING 2350': ('semester-long analysis of a world language', 'Develops linguistic analysis through a sustained investigation of a language.'),
    'LING 3412': ('relationship between language and culture', 'Examines how language interacts with culture and social life.'),
    'LING 3420': ('articulatory, acoustic, and auditory phonetics', 'Studies speech production, speech acoustics and speech perception.'),
    'LING 3422': ('patterning of sounds in human language', 'Studies how languages organize and represent their sound systems.'),
    'LING 3424': ('structure, distributional behavior, and use of words', 'Analyzes word structure and morphological patterns and theories.'),
    'LING 3450': ('theory of sentence structure', 'Introduces syntactic theory and evidence-based analysis of sentence structure.'),
    'LING 3452': ('meaning and how it is expressed in language', 'Examines linguistic meaning in words, sentence structure and language use.'),
    'LING 4654': ('topic in current linguistics research', 'Explores a selected issue in contemporary linguistic research.'),
    'LING 4891': ('group meetings of students and the faculty member', 'Combines individual faculty-guided research with group discussion of methods and findings.'),
    'LING 4991': ('individualized research experience', 'Provides individual research under faculty supervision, with arrangements made before registration.'),
}


def parse_subject(html, *, program_id, subject, heading, codes, url):
    soup = BeautifulSoup(html, 'html.parser')
    title_area = soup.find(id='site-title')
    title = title_area.find('h1') if title_area else None
    if not title or clean(title) != heading:
        raise ValueError('Expected subject course-catalog heading missing')
    content = soup.find(id='textcontainer')
    if content is None:
        raise ValueError('Course-description content missing')
    wanted = set(codes)
    if any(not code.startswith(subject + ' ') for code in wanted):
        raise ValueError('Course selector does not belong to subject')
    courses = {}
    for block in content.find_all('div', class_='courseblock'):
        header = block.find(class_='courseblocktitle')
        if not header: continue
        match = re.fullmatch(r'([A-Z]+ \d+[A-Z]?)\.\s+(.+?)\.\s+\((\d+(?:-\d+)?) Hours?\)', clean(header))
        if not match or match[1] not in wanted: continue
        code, name, hours = match.groups()
        if code in courses: raise ValueError('Duplicate selected course block')
        body = block.find(class_='cb_desc')
        prose = clean(body) if body else ''
        guard, summary = SUMMARIES.get(code, ('', None))
        description = summary if guard and guard in prose else None
        prerequisites = None
        for extra in block.find_all(class_='courseblockextra'):
            text = clean(extra)
            if text.startswith('Prerequisite(s):'):
                prerequisites = text.removeprefix('Prerequisite(s):').strip() or None
        additional = re.search(r'Requires prior completion of ([^.]+)\.', prose)
        if additional:
            condition = 'Additional course-description condition: ' + additional[1] + '.'
            prerequisites = (prerequisites + '; ' if prerequisites else '') + condition
        cid = program_id + '-' + slug(code)
        courses[code] = dict(id=cid, code=code, name=name, description=description, prerequisites=prerequisites,
            credits=numeric(hours), credit_unit='semester_hours', category=category(code,name),
            source_id=program_id+'-'+subject.lower()+'-courses', url=url, public_site=None, syllabus=None)
    missing = wanted - courses.keys()
    if missing: raise ValueError('Selected courses missing from official catalog: ' + ', '.join(sorted(missing)))
    return dict(id=program_id, courses=[courses[code] for code in codes], requirements=[],
                curriculum_status='partial', notes=['Subject-catalog metadata observation only; merge with program requirements after review. Credits are hours in the same semester catalog as the program. Missing prerequisite fields remain unknown.'])
