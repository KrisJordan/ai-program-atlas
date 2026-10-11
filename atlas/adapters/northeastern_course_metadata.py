"""Observed official subject-catalog metadata for explicitly reviewed course codes."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.northeastern_courseleaf import clean, slug, numeric, category

# Short editorial summaries of the linked official descriptions. Each has a
# source phrase guard; changed prose cannot silently replay an unsupported summary.
SUMMARIES = {
    'CIVE 2221': ('stresses and deformations in solids', 'Applies statics and material mechanics to forces, stresses and deformation in structures.'),
    'CIVE 2222': ('Accompanies CIVE 2221', 'Provides guided problem solving in statics and solid mechanics.'),
    'CIVE 2300': ('water and air quality parameters', 'Develops environmental measurement, data analysis and reporting through field and laboratory work.'),
    'CIVE 2301': ('Accompanies CIVE 2300', 'Investigates environmental measurement through experiments and a project.'),
    'CIVE 2331': ('basic hydraulic engineering systems', 'Applies fluid mechanics and conservation principles to hydraulic systems and experiments.'),
    'CIVE 2334': ('engineering methods to control environmental quality problems', 'Introduces environmental assessment, treatment technologies, pollution control and waste management.'),
    'CIVE 3430': ('role of plants and microbes', 'Examines microorganisms and ecological processes in natural and engineered environmental systems.'),
    'CIVE 3435': ('Equilibrium modeling and reactive transport modeling', 'Models pollutant movement, transformation and persistence in water, soil and air.'),
    'CIVE 4534': ('water and wastewater treatment systems', 'Develops the design of physical, chemical and biological water-treatment processes.'),
    'CIVE 4535': ('Accompanies CIVE 4534', 'Investigates water-treatment concepts through laboratory experiments.'),
    'PHYS 1165': ('electrostatics; capacitors', 'Continues introductory physics through electricity, magnetism, circuits and waves.'),
    'PHYS 1166': ('Accompanies PHYS 1165', 'Investigates second-semester introductory physics through laboratory experiments.'),
    'PHYS 1167': ('interactive problem solving', 'Provides guided problem solving for second-semester introductory physics.'),
    'PHYS 1191': ('conceptual and mathematical foundations of theoretical physics', 'Introduces theoretical physics and its mathematical foundations, emphasizing classical mechanics.'),
    'PHYS 1192': ('Accompanies PHYS 1191', 'Investigates foundational physics concepts through laboratory experiments.'),
    'PHYS 1193': ('interactive problem solving', 'Provides guided problem solving for theoretical-physics foundations.'),
    'PHYS 2303': ('wave-particle duality', 'Introduces atomic, nuclear and particle physics, quantum phenomena and special relativity.'),
    'PHYS 3600': ('Data are taken to higher precision', 'Develops advanced physics experimentation, data analysis and scientific reporting.'),
    'PHYS 3601': ('Lagrange’s equations', 'Develops advanced classical mechanics, including oscillations, central forces and Lagrangian methods.'),
    'PHYS 3602': ('Maxwell’s equations', 'Studies electric and magnetic fields, materials, induction and electromagnetic theory.'),
    'PHYS 3603': ('electrodynamics and radiation', 'Continues electromagnetic theory through waves, radiation, field visualization and relativity.'),
    'PHYS 4115': ('Schrödinger wave theory', 'Develops quantum wave mechanics, probability amplitudes and atomic applications.'),
    'PHYS 4305': ('statistical interpretation of entropy', 'Connects thermodynamics and statistical mechanics, including quantum systems.'),
    'PHYS 5116': ('complex networks emerging in nature and technology', 'Develops analytical, computational and modeling methods for complex networks.'),
    'PHYS 5318': ('techniques of modern experimental physics', 'Examines modern experimental techniques in signals, detectors, materials and quantum optics.'),
    'CHEM 1151': ('electrochemical energy storage', 'Introduces matter, reactions, thermodynamics, equilibrium and electrochemistry for engineering.'),
    'CHEM 1153': ('emphasis on student participation', 'Provides guided discussion and practice for engineering chemistry.'),
    'CHEM 2161': ('in the context of modern materials', 'Studies thermodynamics, electrochemistry and chemical structure through modern materials.'),
    'CHEM 2162': ('hands-on exploration', 'Investigates electrochemical, nuclear, supramolecular and solid-state chemistry experimentally.'),
    'CHEM 2315': ('methodology of organic synthesis', 'Develops organic structure, stereochemistry, reactivity and introductory synthesis.'),
    'CHEM 2316': ('synthesis, purification, and characterization', 'Develops organic laboratory methods for synthesis, purification and product characterization.'),
    'CHEM 2317': ('multistep syntheses using the retrosynthesis approach', 'Extends organic reactions and spectroscopy to mechanisms and multistep synthesis.'),
    'CHEM 2318': ('characterization of products from microscale syntheses', 'Uses spectroscopy to characterize organic compounds produced by microscale synthesis.'),
    'CHEM 2321': ('quantitative understanding of homogeneous and heterogeneous equilibria', 'Develops quantitative chemical analysis using equilibrium, separations, spectroscopy and electrochemistry.'),
    'CHEM 2322': ('hands-on experience in the analytical methods', 'Applies analytical methods through titration, spectroscopy, electrochemistry and chromatography experiments.'),
    'CHEM 3331': ('biomolecular analysis by modern methods', 'Examines instrumental analysis of biomolecules, biosensors and genomic and proteomic applications.'),
    'CHEM 3332': ('modern analytical instrumentation', 'Applies analytical instruments to biotechnology and pharmaceutical research problems.'),
    'CHEM 3401': ('quantitative interpretation of physical measurements', 'Applies thermodynamic laws to reactions, phase equilibria and physical measurements.'),
    'CHEM 3402': ('experimental protocol and methods of data analysis', 'Measures physical-chemistry phenomena and develops experimental and data-analysis methods.'),
    'PSYC 3458': ('relation between brain function and human behavior', 'Connects neuronal systems and brain function with perception, action and psychological processes.'),
    'PSYC 4600': ('research project of their own creation', 'Develops an original psychology study from research design through analysis and communication.'),
    'PSYC 4612': ('conducting research on issues in human cognition', 'Develops cognitive-psychology research through experiments, data analysis and reports.'),
    'PSYC 4674': ('Specific topics vary by semester', 'Examines cognitive-neuroscience theories and methods through a seminar with varying topics.'),
    'BIOL 3405': ('organization of neurons into circuits', 'Introduces neural cells and circuits, information processing and motor control.'),
    'BIOL 3601': ('major experimental approaches and key concepts', 'Examines behavioral neurobiology through sensory processing, motor control and learning.'),
    'BIOL 3605': ('cellular, molecular, and genetic processes that guide neural development', 'Studies how neural cells develop, connect and change to support behavior.'),
    'BIOL 4709': ('synaptic mechanisms underlying neural plasticity', 'Examines learning and memory through synaptic, molecular and neural-system mechanisms.'),
    'BIOL 5595': ('molecular mechanisms that underlie biological networks', 'Studies molecular signaling in neural networks and its relevance to neurological disorders.'),
    'MKTG 4606': ('active participation in client-centric challenges', 'Applies analytics, digital technology and machine learning to client problems through a research practicum.'),
    'ENVR 2500': ('analyzing biological data', 'Develops probability, inference and experimental design for biological data analysis.'),
    'ENVR 2501': ('addressed in the R programming environment', 'Applies biostatistical methods through supervised R laboratory exercises.'),
    'SOCL 2485': ('control of nature', 'Examines relationships among environmental change, technology, institutions and social responses.'),
    'SOCL 4528': ('social and political context of technological change', 'Examines technological development and its effects on institutions and society.'),
    'SOCL 1280': ('the platform revolution', 'Examines changing work, organizational power, inequality and digital platforms.'),
    'AFCS 2600': ('communities of color in the United States and internationally', 'Examines how scientific and technological changes affect racialized communities and social inequality.'),
    'HIST 2220': ('global history of science and technology', 'Surveys scientific and technological change and its relationships with society, culture and ethics.'),
    'BINF 6310': ('exploratory data analysis of large-scale biological data', 'Develops computational workflows, sequence analysis and biological-data management for bioinformatics.'),
    'BIOL 2299': ('scientific practice and progress', 'Investigates contemporary biological developments through readings, discussion and projects.'),
    'CHEM 2313': ('spectroscopic methods for structural identification', 'Extends organic functional-group chemistry and introduces structural identification through spectroscopy.'),
    'CHEM 2314': ('infrared (IR) spectroscopy', 'Applies organic laboratory techniques and spectroscopy to reactions and molecular characterization.'),
    'COMM 3201': ('patient-provider communication', 'Examines interpersonal, organizational, cultural and media dimensions of health communication.'),
    'EEMB 2303': ('Accompanies EEMB 2302', 'Investigates ecology concepts through laboratory experiments.'),
    'EEMB 2400': ('mechanisms of evolutionary change', 'Examines evolutionary mechanisms, adaptation and the history of life using scientific evidence.'),
    'EEMB 3460': ('causes and consequences of biodiversity loss', 'Applies ecological and evolutionary principles to biodiversity conservation and restoration.'),
    'ENVR 3125': ('physical, biological, and chemical properties of the ocean', 'Examines ocean change across timescales and its environmental and social implications.'),
    'ENVR 3150': ('sustainable agriculture, fisheries, and aquaculture', 'Examines sustainable food production, climate pressures, nutrition and food security.'),
    'PHTH 2210': ('Introduces R programming language', 'Applies biostatistical reasoning and R to clinical and public-health questions.'),
    'PHTH 2515': ('analyze, prepare, and write policy briefs', 'Examines healthcare management, financing and policy through analysis and policy briefs.'),
    'PSYC 3404': ('change throughout the life span', 'Examines psychological development, environmental influences and individual and cultural differences.'),
    'BIOL 1111': ('seen through the lens of evolutionary theory', 'Introduces cells, heredity, energy and biological inquiry through evolutionary perspectives.'),
    'BIOL 1112': ('quantitative data through hands-on experimentation', 'Develops biological experimentation, quantitative analysis and written reporting.'),
    'BIOL 1113': ('ecological relationships at the population, community, and ecosystem levels', 'Examines organismal diversity, multicellular biology and ecological relationships.'),
    'BIOL 1114': ('Accompanies BIOL 1113', 'Investigates general biology concepts through laboratory experiments.'),
    'BIOL 2309': ('independent research projects', 'Develops independent cell and molecular biology research through intensive laboratory projects.'),
    'BIOL 3611': ('enzyme kinetics and regulation', 'Studies biomolecules, energetics, enzymes and metabolic pathways.'),
    'BIOL 3612': ('Accompanies BIOL 3611', 'Investigates biochemistry concepts through laboratory experiments.'),
    'BIOL 5591': ('whole genome analysis, functional genomics', 'Examines sequencing methods, genomic databases and functional and whole-genome analysis.'),
    'CHEM 4750': ('original experimental work', 'Develops an original chemistry investigation under faculty supervision.'),
    'ARTG 1270': ('case studies, activities in lecture and workshop', 'Introduces design practices through cases, workshops and practitioner presentations.'),
    'ARTG 1271': ('iterative process', 'Develops design inquiry and problem solving through iterative studio projects.'),
    'ARTG 1290': ('typography as a core element of graphic design', 'Studies typography’s history, principles, cultural meaning and design applications.'),
    'ARTG 1291': ('typographic grid and issues of hierarchy and legibility', 'Applies typographic organization, hierarchy and legibility through design projects.'),
    'ARTG 2242': ('data-rich information graphics', 'Develops visual systems for organizing and communicating complex information.'),
    'ARTG 2252': ('creating meaning within function, content, and context', 'Applies graphic form, composition, typography and imagery to visual communication.'),
    'ARTG 3400': ('Topics vary each semester', 'Investigates a selected interaction-design topic that varies by offering.'),
    'ARTG 4550': ('culmination to the undergraduate program', 'Develops and executes a culminating graphic, interaction or experience-design project.'),
    'ARTF 1200': ('rendering 3D objects and spaces', 'Develops observational drawing, perspective and representation of physical objects and spaces.'),
    'INSH 2102': ('geospatial mapping, data visualization, and network science', 'Integrates computational methods with cultural and social research using Boston case studies.'),
    'INSH 3101': ('develop a research design', 'Develops research questions, methods and critical analysis in the social sciences.'),
    'INSH 3102': ('display or visualize quantitative data', 'Develops statistical and computational methods for social-science research.'),
    'EESH 2000': ('develop job-search and career-management skills', 'Prepares students for co-op searches, interviewing, professional practice and career decisions.'),
    'EESC 2000': ('develop job-search and career-management skills', 'Prepares students for co-op searches, interviewing, professional practice and career decisions.'),
    'EEAM 2000': ('develop job-search and career-management skills', 'Prepares students for co-op searches, interviewing, professional practice and career decisions.'),
    'LANG 3600': ('institutional/systemic control of language use', 'Examines language policy, institutions and social effects through regional case studies.'),
    'MKTG 2201': ('evaluation of marketing efforts', 'Introduces marketing strategy, implementation and evaluation across organizational settings.'),
    'ACCT 1201': ('interpret, analyze, and evaluate published corporate financial reports', 'Develops financial-statement analysis and examines accounting principles and reporting ethics.'),
    'FINA 2201': ('time value of money', 'Develops financial analysis, valuation, financing and capital-management decisions.'),
    'ORGB 3201': ('individual, interpersonal, group, organizational, and cross-cultural', 'Examines behavior, teams, leadership, culture and change within organizations.'),
    'INNO 2301': ('transformed into commercial reality', 'Examines innovation processes and how ideas become products or services.'),
    'MISM 2301': ('strategic role of information systems', 'Examines enterprise information systems, digital technologies and business data analysis.'),
    'SCHM 2301': ('supply, inventory, and quality management', 'Studies supply chains, operations, logistics and the coordination of business processes.'),
    'STRT 4501': ('analyze, formulate, and implement business strategy', 'Integrates strategic analysis and implementation through a business capstone experience.'),
    'MGSC 2301': ('regression analysis in the context of business', 'Develops statistical inference and regression for analyzing business data.'),
    'ARTG 2400': ('low- to high-fidelity prototyping techniques', 'Develops interaction-design research, prototyping and usability testing for interfaces.'),
    'EECE 2160': ('controlling physical devices via software', 'Combines digital design, programming and embedded systems to control robotic devices.'),
    'EECE 2322': ('construction of a simple processor', 'Develops digital logic, computer architecture and hardware models for a simple processor.'),
    'EECE 2323': ('computer system on field-programmable logic', 'Designs, simulates and tests a computer system using programmable logic.'),
    'EECE 2560': ('algorithm complexity analysis', 'Develops data structures, algorithms and complexity analysis for engineering problems.'),
    'ENVR 1110': ('mitigation and adaptation options', 'Examines past and projected climate change, its impacts, mitigation and adaptation.'),
    'ENVR 1200': ('guiding paradigm in geology', 'Studies Earth materials, geological processes and landscapes through plate tectonics.'),
    'PHTH 1260': ('managing costs, increasing quality', 'Examines healthcare organization, financing, access, equity and reform in the United States.'),
    'PHTH 2300': ('communicating as a leader', 'Develops interpersonal communication and presentation skills for health professions.'),
    'EEMB 1101': ('designing and implementing independent field research', 'Introduces ecology and evolution through lectures, field investigation and independent research.'),
    'EEMB 2302': ('distribution and abundance of species', 'Studies ecological processes through research, experimentation and scientific communication.'),
    'INPR 1000': ('apply design and systems thinking practices', 'Explores global citizenship, university resources and interdisciplinary problem solving.'),
    'INSC 1000': ('Introduces first-year students with majors in the College of Science', 'Introduces science students to university study, academic skills and their college community.'),
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
        for pattern, prefix in [
            (r'Requires previous coursework in ([^.]+)\.', 'Previous coursework in '),
            (r'Requires ([^.]+) to register\.', 'Registration requires '),
            (r'Requires a working knowledge of ([^.]+)\.', 'Working knowledge of '),
            (r'Requires ([a-z]+ standing or above)\.', 'Academic standing: '),
        ]:
            condition_match = re.search(pattern, prose)
            if condition_match:
                condition = 'Additional course-description condition: ' + prefix + condition_match[1] + '.'
                prerequisites = (prerequisites + '; ' if prerequisites else '') + condition
        concurrent = re.search(r'Requires concurrent registration in ([^.]+)\.', prose)
        if concurrent:
            metadata_notes.append(f'{code} subject catalog concurrent-registration condition: {concurrent[1].strip()}. This is not prior-completion eligibility.')
        for recommendation in (sentence for sentence in re.split(r'(?<=[.!?])\s+(?=[A-Z])', prose)
                               if re.search(r'\brecommended\b', sentence, re.I)):
            metadata_notes.append(f'{code} subject catalog recommended preparation (not a prerequisite): {recommendation.strip()}')
        if code == 'PSYC 2320' and 'Should be taken before the end of the sophomore year.' in prose:
            metadata_notes.append('PSYC 2320 subject catalog timing advice: complete before the end of the sophomore year. This advice is separate from prerequisite eligibility.')
        scoped_conditions = {
            'POLS 3423': ('Permission of instructor required for students who do not meet prerequisite.', 'Instructor permission is required for students who do not meet the prerequisite; approval is not presumed.'),
            'ARTG 5330': ('Students who do not meet course restrictions may seek permission of instructor or program coordinator.', 'Students outside course restrictions may seek instructor or program-coordinator permission; permission is not guaranteed.'),
            'ENTR 3217': ('Required participation in spring break international field project.', 'Participation in a spring-break international field project is required. This is a course activity, not prior-completion eligibility.'),
            'ENVR 3300': ('Students who do not meet course prerequisites may seek permission of instructor.', 'Students who do not meet the prerequisites may seek instructor permission; permission is not guaranteed.'),
            'PHTH 5222': ('Requires permission of instructor for students outside designated programs.', 'Instructor permission is required outside designated programs. The description does not enumerate those programs; applicability remains conditional.'),
            'JRNL 5360': ('International students wishing to register need to speak to the International Student and Scholar Institute prior to registration.', 'International students must speak to the International Student and Scholar Institute before registering.'),
        }
        scoped = scoped_conditions.get(code)
        if scoped and scoped[0] in prose:
            metadata_notes.append(f'{code} source-stated registration condition: {scoped[1]}')
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
    'AFCS': 'Africana Studies (AFCS)',
    'ANTH': 'Anthropology (ANTH)',
    'ARAB': 'Arabic (ARAB)',
    'ASNS': 'Asian Studies (ASNS)',
    'BINF': 'Bioinformatics (BINF)',
    'BIOC': 'Biochemistry (BIOC)',
    'BNSC': 'Behavioral Neuroscience (BNSC)',
    'COOP': 'Cooperative Education (COOP)',
    'DEAF': 'Deaf Studies (DEAF)',
    'EEAM': 'Co-op/Experiential Education in Arts, Media, and Design (EEAM)',
    'EEBA': 'Co-op/Experiential Education in Business (EEBA)',
    'EESC': 'Co-op/Experiential Education in Science (EESC)',
    'EESH': 'Co-op/Experiential Education in Social Sciences and Humanities (EESH)',
    'ENCP': 'Engineering Cooperative Education (ENCP)',
    'ENGL': 'English (ENGL)',
    'FRNH': 'French (FRNH)',
    'HIST': 'History (HIST)',
    'HLTH': 'Health Science - Interdisciplinary (HLTH)',
    'HSCI': 'Health Science (HSCI)',
    'HUSV': 'Human Services (HUSV)',
    'IE': 'Industrial Engineering (IE)',
    'INSH': 'Interdisciplinary Studies in Social Sciences and Humanities (INSH)',
    'JPNS': 'Japanese (JPNS)',
    'LACS': 'Latin American and Caribbean Studies (LACS)',
    'LANG': 'Language - General (LANG)',
    'MSCR': 'Media and Screen Studies (MSCR)',
    'POLS': 'Political Science (POLS)',
    'PPUA': 'Public Policy and Urban Affairs (PPUA)',
    'PREL': 'Public Relations (PREL)',
    'PT': 'Physical Therapy (PT)',
    'SPNS': 'Spanish (SPNS)',
    'WMNS': 'Women’s, Gender, and Sexuality Studies (WMNS)',

    'MKTG': 'Marketing (MKTG)',
    'FINA': 'Finance and Insurance (FINA)',
    'MGMT': 'Management (MGMT)',
    'INNO': 'Corporate Innovation (INNO)',
    'ENTR': 'Entrepreneurship and Innovation (ENTR)',
    'INTB': 'International Business (INTB)',
    'ACCT': 'Accounting (ACCT)',
    'SCHM': 'Supply Chain Management (SCHM)',
    'BUSN': 'Business Administration (BUSN)',
    'MISM': 'Management Information Systems (MISM)',
    'ORGB': 'Organizational Behavior (ORGB)',
    'STRT': 'Strategy (STRT)',
    'MGSC': 'Management Science (MGSC)',
    'ARTG': 'Art - Design (ARTG)',
    'ARTF': 'Art - Fundamentals (ARTF)',
    'EECE': 'Electrical and Computer Engineering (EECE)',
    'ENVR': 'Earth and Environmental Sciences (ENVR)',
    'PHTH': 'Public Health (PHTH)',
    'EEMB': 'Ecology, Evolution, and Marine Biology (EEMB)',
    'INPR': 'Interdisciplinary Studies - Office of the Provost (INPR)',
    'INSC': 'Interdisciplinary Studies in Science (INSC)',
    'SOCL': 'Sociology (SOCL)',
    'JRNL': 'Journalism (JRNL)',
    'COMM': 'Communication Studies (COMM)',
    'CRIM': 'Criminal Justice (CRIM)',
    'INTL': 'International Affairs (INTL)',
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
