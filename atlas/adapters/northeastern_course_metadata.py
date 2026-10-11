"""Observed official subject-catalog metadata for explicitly reviewed course codes."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.northeastern_courseleaf import clean, slug, numeric, category

# Short editorial summaries of the linked official descriptions. Each has a
# source phrase guard; changed prose cannot silently replay an unsupported summary.
SUMMARIES = {
    'ENGW 1102': ('concerns of multilingual writers', 'Develops research, revision and writing practices with attention to multilingual writers.'),
    'ENGW 1111': ('writing in a workshop setting', 'Develops research and writing across audiences and genres through workshop practice.'),
    'ENGW 1114': ('writing projects meet specific community needs', 'Develops writing and research through community service projects.'),
    'ENGW 3302': ('relevant to technical professions and individual student goals', 'Develops research and communication in technical and professional genres.'),
    'ENGW 3303': ('complex environmental concern', 'Develops environmental research reports through staged writing and revision.'),
    'ENGW 3304': ('relevant for careers in business', 'Develops evidence-based writing and communication for business contexts.'),
    'ENGW 3306': ('protocols, and care instructions', 'Develops writing and research practices for health professions.'),
    'ENGW 3307': ('quantitative data and visual presentation of evidence', 'Develops scientific argument, evidence presentation and research-based writing.'),
    'ENGW 3308': ('ethical presentation of evidence', 'Develops research writing and ethical evidence presentation in social sciences.'),
    'ENGW 3309': ('framing of interpretive questions', 'Develops interpretive argument and textual evidence in humanities writing.'),
    'ENGW 3314': ('alphabetic, visual, musical, and sculptural', 'Develops writing across artistic, media and design contexts and literacies.'),
    'ENGW 3315': ('students interested in interdisciplinary study', 'Develops research, revision and writing across disciplinary contexts.'),
    'PHYS 1145': ('problems in the life and health sciences', 'Applies mechanics, fluids and thermal physics to life and health sciences.'),
    'PHYS 1146': ('Accompanies PHYS 1145', 'Investigates introductory life-science physics through laboratory experiments.'),
    'PHYS 1151': ('intended primarily for engineering students', 'Develops calculus-based mechanics and fluid physics for engineering.'),
    'PHYS 1152': ('Accompanies PHYS 1151', 'Investigates introductory engineering physics through laboratory experiments.'),
    'PHYS 1153': ('organized approaches and use of mathematical techniques', 'Practices mathematical problem solving in mechanics and fluids.'),
    'PHYS 1161': ('intended primarily for science students', 'Develops calculus-based mechanics and fluids with applications across sciences.'),
    'PHYS 1162': ('Accompanies PHYS 1161', 'Investigates introductory physics concepts through laboratory experiments.'),
    'PHYS 1163': ('interactive problem solving', 'Provides guided problem solving for introductory physics.'),
    'PHIL 1115': ('deductive and inductive logic', 'Develops formal logic and methods of deductive and probabilistic reasoning.'),
    'PHIL 1145': ('ethical issues raised by emerging technologies', 'Examines technology’s social dimensions and ethical implications.'),
    'PHIL 1300': ('normative frameworks from epistemology and ethics', 'Examines digital technology’s effects on knowledge through ethics and epistemology.'),
    'PHIL 3050': ('drawing conclusions from noisy data', 'Develops probabilistic inference and information theory for reasoning under uncertainty.'),
    'PHIL 4050': ('aligning these impacts with social and ethical values', 'Examines AI’s societal effects and approaches to aligning technologies with ethical values.'),
    'PHIL 4515': ('proof systems, decidability, computability, and metatheory', 'Develops first-order logic, proof methods and foundational metatheory.'),
    'PHIL 4516': ('Bayesian epistemology', 'Studies inductive inference, Bayesian belief revision and rational decision making.'),
    'PHIL 5005': ('avoiding bias, exploitation, and manipulation', 'Examines justice, rights and ethical responsibilities in information technologies.'),
    'PHIL 5010': ('philosophical and ethical questions', 'Examines AI ethics, including fairness, responsibility, privacy and effects on work.'),
    'BIOL 1107': ('evolutionary principles, cellular structure and function', 'Introduces biological systems through evolution, cells, inheritance, energy and physiology.'),
    'BIOL 1108': ('genetic transmission, energy pathways, and physiology', 'Uses laboratory experiments to investigate foundational biological processes.'),
    'BIOL 2301': ('bioinformatics, genomics, and proteomics', 'Examines inheritance and gene function through molecular and population approaches.'),
    'BIOL 2302': ('scientific investigation methods and data analysis', 'Investigates genetics through laboratory methods and analysis of experimental data.'),
    'BIOL 2407': ('sequence datasets generated by research labs', 'Applies computational workflows to biological sequence data in independent research projects.'),
    'BIOL 4701': ('development of an original research proposal', 'Integrates biology study and experience through scientific research, reflection and a proposal.'),
    'CHEM 1161': ('underlying molecular dynamics of living systems', 'Introduces chemical structure, reactions, kinetics and thermodynamics with biological applications.'),
    'CHEM 1162': ('qualitative and quantitative analysis', 'Develops laboratory techniques for studying chemical and physical processes.'),
    'CHEM 1163': ('work interactively with instructors', 'Provides guided practice applying concepts from general chemistry lectures.'),
    'CHEM 2311': ('mechanistic interpretation of organic reactions', 'Studies organic structures, stereochemistry, properties and reaction mechanisms.'),
    'CHEM 2312': ('microscale syntheses', 'Practices organic synthesis, purification and compound characterization in the laboratory.'),
    'ECON 1115': ('monetary and fiscal policies', 'Introduces macroeconomic growth, fluctuations, policy and distributional measurement.'),
    'ECON 1116': ('interaction of consumers, firms, and governments', 'Introduces markets, economic choices, efficiency, equity and market failures.'),
    'ECON 2315': ('rigorous mathematical tools', 'Uses mathematical models to analyze macroeconomic dynamics, policy and social justice.'),
    'ECON 2316': ('welfare and distributional impacts', 'Uses calculus-based models to examine market structures, policy and economic welfare.'),
    'ECON 2350': ('simple regression analysis', 'Applies statistical inference, regression and data visualization to economic and social questions.'),
    'ECON 2560': ('Writing an applied econometrics paper', 'Develops multivariate regression methods and applies them in an empirical research paper.'),
    'PSYC 1101': ('psychology as a method of inquiry', 'Surveys psychological research methods and major areas of behavioral science.'),
    'PSYC 2320': ('descriptive and inferential statistics', 'Develops statistical analysis and inference for psychological research.'),
    'PSYC 3450': ('operant and Pavlovian conditioning', 'Examines learning, motivation and conditioning through research and behavioral applications.'),
    'PSYC 3466': ('current theories of cognitive processing', 'Studies cognitive processes such as attention, memory, categorization and problem solving.'),
    'PSYC 4540': ('Emphasizes theory and modeling, not statistics', 'Explores mathematical and computational models of psychological and neural processes.'),
    'MATH 1231': ('realistic business and economics problems', 'Applies differential and integral calculus to business modeling and economic decisions.'),
    'MATH 1241': ('self-contained one-semester course', 'Introduces differentiation, integration and applications involving change and accumulation.'),
    'MATH 1245': ('differential equation and compares the solution with experiment', 'Applies calculus and differential equations to scientific models and a group investigation.'),
    'MATH 1340': ('strengthening of precalculus skills', 'Combines precalculus preparation with introductory differential and integral calculus.'),
    'MATH 1341': ('the derivative as a limit', 'Develops differentiation, its scientific applications, and introductory integration.'),
    'MATH 1342': ('convergence of sequences and series', 'Continues integration methods, series, and introductory vectors and spatial motion.'),
    'MATH 1365': ('logically sound mathematical arguments', 'Develops proof writing and mathematical reasoning using sets, relations and functions.'),
    'MATH 1465': ('countable and uncountable sets', 'Intensively develops proofs, mathematical structures, cardinality and introductory algebra.'),
    'MATH 2321': ('vector calculus in two and three dimensions', 'Develops multivariable differentiation, multiple integrals and vector calculus.'),
    'MATH 2331': ('Gauss-Jordan elimination algorithm', 'Studies linear transformations, matrix methods, orthogonality and spectral decompositions.'),
    'MATH 2341': ('Laplace transforms, and linear algebra', 'Combines differential-equation methods and linear algebra for engineering applications.'),
    'MATH 3081': ('confidence intervals, and hypothesis testing', 'Develops probability distributions and limit theory, then introduces statistical inference.'),
    'MATH 3175': ('structural properties of groups', 'Studies abstract groups, their structure, homomorphisms and applications.'),
    'MATH 3527': ('RSA encryption system', 'Studies integers, congruences and number-theoretic methods, including cryptographic applications.'),
    'CS 1200': ('academic and personal goal setting', 'Supports university transition, community connections and student planning.'),
    'CS 1210': ('professional behavior and ethical issues', 'Prepares students for co-op applications, interviews and workplace expectations.'),
    'CS 1800': ('inductive and recursive definitions', 'Develops discrete structures, logic, proofs and counting methods for computing.'),
    'CS 2000': ('no prior programming experience', 'Introduces programming, dataset analysis and ethical issues in software design.'),
    'CS 2001': ('Accompanies CS 2000', 'Provides experiments supporting introductory programming coursework.'),
    'CS 2100': ('abstraction, encapsulation, inheritance, and interfaces', 'Develops program design, object-oriented abstractions and software engineering practices.'),
    'CS 2101': ('Accompanies CS 2100', 'Provides experiments supporting program design coursework.'),
    'CS 2484': ('usability and accessibility', 'Introduces human-centered interface design, prototyping and usability evaluation.'),
    'CS 3200': ('fundamentals of concurrency and recovery', 'Develops relational database design, SQL and introductory database-system techniques.'),
    'CS 4100': ('heuristic search, decision making under uncertainty', 'Surveys AI representations, search, uncertainty and machine learning through programming.'),
    'CS 4120': ('computational modeling of human language', 'Studies computational language models and builds natural-language analysis programs.'),
    'CS 4520': ('professional-quality mobile application', 'Develops mobile applications with interfaces, data storage, networking and device features.'),
    'CS 4991': ('conduct research under faculty supervision', 'Provides faculty-supervised research.'),
    'CY 4170': ('automation, and intellectual property', 'Examines legal and ethical rules governing digital data, privacy and automated systems.'),
    'CY 5240': ('emerging technologies for management of digital rights', 'Examines cybersecurity law, privacy, digital rights and information-security ethics.'),
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

    'DS 1300': ('normative frameworks from epistemology and ethics', 'Examines how digital technologies shape knowledge and evaluates their effects through ethics and epistemology.'),
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
    metadata_notes = []
    for block in content.find_all('div', class_='courseblock'):
        header = block.find(class_='courseblocktitle')
        if not header: continue
        match = re.fullmatch(r'([A-Z]+ \d+[A-Z]?)\.\s+(.+?)\.\s+\((\d+(?:\s*[-,]\s*\d+)*) Hours?\)', clean(header))
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
            elif text.startswith('Corequisite(s):'):
                condition = text.removeprefix('Corequisite(s):').strip()
                if condition:
                    metadata_notes.append(f'{code} subject catalog corequisite(s): {condition}. These are concurrent conditions, not prerequisites.')
        additional = re.search(r'Requires prior completion of ([^.]+)\.', prose)
        if additional:
            condition = 'Additional course-description condition: ' + additional[1] + '.'
            prerequisites = (prerequisites + '; ' if prerequisites else '') + condition
        concurrent = re.search(r'Requires concurrent registration in ([^.]+)\.', prose)
        if concurrent:
            metadata_notes.append(f'{code} subject catalog concurrent-registration condition: {concurrent[1].strip()}. This is not prior-completion eligibility.')
        for recommendation in re.findall(r'[^.]*\b(?:recommended|recommended preparation)\b[^.]*\.', prose, re.I):
            metadata_notes.append(f'{code} subject catalog recommended preparation (not a prerequisite): {recommendation.strip()}')
        if code == 'PSYC 2320' and 'Should be taken before the end of the sophomore year.' in prose:
            metadata_notes.append('PSYC 2320 subject catalog timing advice: complete before the end of the sophomore year. This advice is separate from prerequisite eligibility.')
        if numeric(hours) is None:
            metadata_notes.append(f'{code} subject catalog credit options: {hours} semester hours. The scalar credit amount remains unknown; alternatives are not added together.')
        cid = program_id + '-' + slug(code)
        courses[code] = dict(id=cid, code=code, name=name, description=description, prerequisites=prerequisites,
            credits=numeric(hours), credit_unit='semester_hours', category=category(code,name),
            source_id=program_id+'-'+subject.lower()+'-courses', url=url, public_site=None, syllabus=None)
    missing = wanted - courses.keys()
    if missing: raise ValueError('Selected courses missing from official catalog: ' + ', '.join(sorted(missing)))
    return dict(id=program_id, courses=[courses[code] for code in codes], requirements=[],
                curriculum_status='partial', notes=['Subject-catalog metadata observation only; merge with program requirements after review. Credits are hours in the same semester catalog as the program. Missing prerequisite fields remain unknown.', *metadata_notes])


SUBJECT_HEADINGS = {
    'ENGW': 'English Writing (ENGW)',
    'PHYS': 'Physics (PHYS)',
    'PHIL': 'Philosophy (PHIL)',
    'DS': 'Data Science (DS)',
    'BIOL': 'Biology (BIOL)',
    'CHEM': 'Chemistry and Chemical Biology (CHEM)',
    'ECON': 'Economics (ECON)',
    'PSYC': 'Psychology (PSYC)',
    'MATH': 'Mathematics (MATH)',
    'CS': 'Computer Science (CS)',
    'CY': 'Cybersecurity (CY)',
}


def register_subject_sources(program_id, selections):
    """Bind explicitly reviewed code selections, without reading curated seeds."""
    parsers = {}
    for subject, codes in selections.items():
        heading = SUBJECT_HEADINGS[subject]
        url = f'https://catalog.northeastern.edu/course-descriptions/{subject.lower()}/'
        def observe(html, subject=subject, heading=heading, codes=tuple(codes), url=url):
            return parse_subject(html, program_id=program_id, subject=subject,
                                 heading=heading, codes=codes, url=url)
        parsers[url] = observe
    return parsers
