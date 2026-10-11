"""Source-specific, guarded metadata observations for the second six-record review.

Credit amounts retain unknown units unless a source explicitly says semester credits.
These observations never certify curriculum completeness or a launch date.
"""

import re
from bs4 import BeautifulSoup

CONFIG = {
    "rochester-fall": {
        "pid": "rochester-ai-concentration",
        "parser": "rochester",
        "courses": [
            {
                "id": "rochester-csc-239",
                "code": "CSC 239",
                "guard": "This course provides a theoretical foundation for analyzing and u",
                "summary": "Examines approximation, optimization and generalization in "
                "classical learning and deep neural networks.",
            },
            {
                "id": "rochester-csc-240",
                "code": "CSC 240",
                "guard": "Fundamental concepts and techniques of data mining, including dat",
                "summary": "Covers data preparation, pattern discovery, "
                "classification, clustering and advanced data-mining "
                "applications.",
            },
            {
                "id": "rochester-csc-245",
                "code": "CSC 245",
                "guard": "Much of the recent advances in machine learning and artificial in",
                "summary": "Connects deep-learning theory with practical image and "
                "language applications.",
            },
            {
                "id": "rochester-csc-246",
                "code": "CSC 246",
                "guard": "Mathematical foundations of classification, regression, and decis",
                "summary": "Studies mathematical foundations and algorithms for "
                "classification, regression and decision making through "
                "programming projects.",
            },
            {
                "id": "rochester-csc-277",
                "code": "CSC 277",
                "guard": "Deep learning systems are now being widely productionized at larg",
                "summary": "Studies deployment, data management, fairness, monitoring "
                "and operational management of deep-learning systems.",
            },
            {
                "id": "rochester-csc-290",
                "code": "CSC 290",
                "guard": "This advanced course is aimed at students who wish to build and u",
                "summary": "Studies programming, compilation, parallelization and "
                "hardware for efficient large-scale AI systems.",
            },
        ],
        "term": "Fall 2026",
        "url": "https://www.cs.rochester.edu/courses/fall.php",
        "source_id": "rochester-fall-metadata",
    },
    "rochester-spring": {
        "pid": "rochester-ai-concentration",
        "parser": "rochester",
        "courses": [
            {
                "id": "rochester-csc-247",
                "code": "CSC 247",
                "guard": "This introductory course in Natural Language Processing (NLP) exp",
                "summary": "Surveys statistical and neural language processing, "
                "foundation models and language-understanding "
                "applications.",
            },
            {
                "id": "rochester-csc-249",
                "code": "CSC 249",
                "guard": "Introduction to computer vision, including camera models, basic i",
                "summary": "Introduces image formation and processing, object "
                "recognition and geometric and statistical vision "
                "models.",
            },
        ],
        "term": "Spring 2026",
        "url": "https://www.cs.rochester.edu/courses/spring.php",
        "source_id": "rochester-spring-metadata",
    },
    "georgia-csci-3360": {
        "pid": "georgia-ai-emphasis",
        "parser": "uga",
        "courses": [
            {
                "id": "georgia-csci-3360",
                "code": "CSCI 3360",
                "guard": "A rigorous overview of methods for text mining, image processing,",
                "summary": "Applies supervised and unsupervised analysis, "
                "dimensionality reduction and visualization to text, "
                "images and scientific data.",
            }
        ],
        "url": "https://bulletin.uga.edu/Course/Details/32623",
        "source_id": "georgia-csci-3360-metadata",
    },
    "georgia-csci-4360-6360": {
        "pid": "georgia-ai-emphasis",
        "parser": "uga",
        "courses": [
            {
                "id": "georgia-csci-4360-6360",
                "code": "CSCI 4360/6360",
                "guard": "An introduction to advanced analytics techniques in data science,",
                "summary": "Studies advanced learning methods, randomized "
                "computation and scalable data analysis.",
            }
        ],
        "url": "https://bulletin.uga.edu/Course/Details/32634",
        "source_id": "georgia-csci-4360-6360-metadata",
    },
    "georgia-csci-phil-4550-6550": {
        "pid": "georgia-ai-emphasis",
        "parser": "uga",
        "courses": [
            {
                "id": "georgia-csci-phil-4550-6550",
                "code": "CSCI(PHIL) 4550/6550",
                "guard": "An introduction to the theory and techniques underlying the desig",
                "summary": "Introduces agents, search, knowledge "
                "representation, reasoning, planning and "
                "machine learning.",
            }
        ],
        "url": "https://bulletin.uga.edu/Course/Details/4947",
        "source_id": "georgia-csci-phil-4550-6550-metadata",
    },
    "georgia-csci-4170-6170": {
        "pid": "georgia-ai-emphasis",
        "parser": "uga",
        "courses": [
            {
                "id": "georgia-csci-4170-6170",
                "code": "CSCI 4170/6170",
                "guard": "An introduction to implementing computational-based trading strat",
                "summary": "Applies computational finance and machine learning "
                "to market data and trading strategies.",
            }
        ],
        "url": "https://bulletin.uga.edu/Course/Details/38217",
        "source_id": "georgia-csci-4170-6170-metadata",
    },
    "georgia-csci-4380-6380": {
        "pid": "georgia-ai-emphasis",
        "parser": "uga",
        "courses": [
            {
                "id": "georgia-csci-4380-6380",
                "code": "CSCI 4380/6380",
                "guard": "A broad introduction to data mining methods and an exploration of",
                "summary": "Surveys data-mining methods and their application to complex datasets.",
            }
        ],
        "url": "https://bulletin.uga.edu/Course/Details/31068",
        "source_id": "georgia-csci-4380-6380-metadata",
    },
    "georgia-csci-arti-4530-6530": {
        "pid": "georgia-ai-emphasis",
        "parser": "uga",
        "courses": [
            {
                "id": "georgia-csci-arti-4530-6530",
                "code": "CSCI(ARTI) 4530/6530",
                "guard": "Introduction to the hardware and software involved in autonomous ",
                "summary": "Models robotic perception and motion and "
                "implements algorithms in simulated "
                "environments.",
            }
        ],
        "url": "https://bulletin.uga.edu/Course/Details/14113",
        "source_id": "georgia-csci-arti-4530-6530-metadata",
    },
    "georgia-csci-4560-6560": {
        "pid": "georgia-ai-emphasis",
        "parser": "uga",
        "courses": [
            {
                "id": "georgia-csci-4560-6560",
                "code": "CSCI 4560/6560",
                "guard": "An in-depth introduction to evolutionary computation methods and ",
                "summary": "Studies evolutionary computation and its use in "
                "optimization and AI research.",
            }
        ],
        "url": "https://bulletin.uga.edu/Course/Details/13144",
        "source_id": "georgia-csci-4560-6560-metadata",
    },
    "georgia-csci-arti-4600-6600": {
        "pid": "georgia-ai-emphasis",
        "parser": "uga",
        "courses": [
            {
                "id": "georgia-csci-arti-4600-6600",
                "code": "CSCI(ARTI) 4600/6600",
                "guard": "Reinforcement learning studies methods for learning to act optima",
                "summary": "Examines reinforcement learning for single "
                "and multiple agents acting under "
                "uncertainty.",
            }
        ],
        "url": "https://bulletin.uga.edu/Course/Details/44048",
        "source_id": "georgia-csci-arti-4600-6600-metadata",
    },
    "georgia-csci-4850-6850": {
        "pid": "georgia-ai-emphasis",
        "parser": "uga",
        "courses": [
            {
                "id": "georgia-csci-4850-6850",
                "code": "CSCI 4850/6850",
                "guard": "Introduction to the standard approaches to biomedical image analy",
                "summary": "Develops algorithms and software for biomedical "
                "imaging and image analysis.",
            }
        ],
        "url": "https://bulletin.uga.edu/Course/Details/22798",
        "source_id": "georgia-csci-4850-6850-metadata",
    },
    "georgia-csci-4860-6860": {
        "pid": "georgia-ai-emphasis",
        "parser": "uga",
        "courses": [
            {
                "id": "georgia-csci-4860-6860",
                "code": "CSCI 4860/6860",
                "guard": "Introduction to computational neuroscience. Students will learn b",
                "summary": "Studies computational models of neural systems and "
                "analysis of neural signals.",
            }
        ],
        "url": "https://bulletin.uga.edu/Course/Details/45617",
        "source_id": "georgia-csci-4860-6860-metadata",
    },
    "georgia-csci-4900-6900": {
        "pid": "georgia-ai-emphasis",
        "parser": "uga",
        "courses": [
            {
                "id": "georgia-csci-4900-6900",
                "code": "CSCI 4900/6900",
                "guard": "Various advanced topics in Computer Science.",
                "summary": "Covers selected advanced computing topics; the AI "
                "emphasis requires an approved AI-related topic.",
            }
        ],
        "url": "https://bulletin.uga.edu/Course/Details/4687",
        "source_id": "georgia-csci-4900-6900-metadata",
    },
    "villanova-eco-3137": {
        "pid": "villanova-analytics-ai-minor",
        "parser": "villanova",
        "courses": [
            {
                "id": "villanova-eco-3137",
                "code": "ECO 3137",
                "guard": "Intermediate course in stochastic methods with emphasis on applic",
                "summary": "Uses statistical estimation, regression and "
                "forecasting to investigate economic relationships.",
            }
        ],
        "url": "https://live-villanova-catalog.cleancatalog.io/economics/eco-3137",
        "source_id": "villanova-eco-3137-metadata",
    },
    "villanova-fin-2360": {
        "pid": "villanova-analytics-ai-minor",
        "parser": "villanova",
        "courses": [
            {
                "id": "villanova-fin-2360",
                "code": "FIN 2360",
                "guard": "Applied Financial Statistics; Risk and Return; Probability Distri",
                "summary": "Applies statistical and econometric methods to "
                "financial risk, returns and other finance problems.",
            }
        ],
        "url": "https://live-villanova-catalog.cleancatalog.io/finance/fin-2360",
        "source_id": "villanova-fin-2360-metadata",
    },
    "villanova-mgt-3180": {
        "pid": "villanova-analytics-ai-minor",
        "parser": "villanova",
        "courses": [
            {
                "id": "villanova-mgt-3180",
                "code": "MGT 3180",
                "guard": "Application of management theory to problem identification and so",
                "summary": None,
            }
        ],
        "url": "https://live-villanova-catalog.cleancatalog.io/analytics-artificial-intelligence/mgt-3180",
        "source_id": "villanova-mgt-3180-metadata",
    },
    "villanova-mgt-3600": {
        "pid": "villanova-analytics-ai-minor",
        "parser": "villanova",
        "courses": [
            {
                "id": "villanova-mgt-3600",
                "code": "MGT 3600",
                "guard": "Integration of analytics into decision making for sports organiza",
                "summary": "Applies R and statistical analysis to sports "
                "performance, scouting and organizational decisions.",
            }
        ],
        "url": "https://live-villanova-catalog.cleancatalog.io/management/mgt-3600",
        "source_id": "villanova-mgt-3600-metadata",
    },
    "villanova-mis-2030": {
        "pid": "villanova-analytics-ai-minor",
        "parser": "villanova",
        "courses": [
            {
                "id": "villanova-mis-2030",
                "code": "MIS 2030",
                "guard": "Theoretic and practical issues related to the management of a dat",
                "summary": "Studies relational database design, SQL, distributed "
                "databases and client-server systems.",
            }
        ],
        "url": "https://live-villanova-catalog.cleancatalog.io/management-information-systems/mis-2030",
        "source_id": "villanova-mis-2030-metadata",
    },
    "villanova-mis-3050": {
        "pid": "villanova-analytics-ai-minor",
        "parser": "villanova",
        "courses": [
            {
                "id": "villanova-mis-3050",
                "code": "MIS 3050",
                "guard": "Fundamental issues associated with Customer Relationship Manageme",
                "summary": "Uses data warehouses, business intelligence and data "
                "mining to support organizational decisions.",
            }
        ],
        "url": "https://live-villanova-catalog.cleancatalog.io/management-information-systems/mis-3050",
        "source_id": "villanova-mis-3050-metadata",
    },
    "villanova-mis-3060": {
        "pid": "villanova-analytics-ai-minor",
        "parser": "villanova",
        "courses": [
            {
                "id": "villanova-mis-3060",
                "code": "MIS 3060",
                "guard": "This course examines concepts, processes, and tools related to bu",
                "summary": "Builds business-intelligence workflows with generative "
                "AI and modern data tools.",
            }
        ],
        "url": "https://live-villanova-catalog.cleancatalog.io/management-information-systems/mis-3060",
        "source_id": "villanova-mis-3060-metadata",
    },
    "villanova-mkt-2240": {
        "pid": "villanova-analytics-ai-minor",
        "parser": "villanova",
        "courses": [
            {
                "id": "villanova-mkt-2240",
                "code": "MKT 2240",
                "guard": "Covers analytics skills necessary for marketing decision making; ",
                "summary": "Applies analytical software and quantitative methods "
                "to marketing decisions.",
            }
        ],
        "url": "https://live-villanova-catalog.cleancatalog.io/marketing/mkt-2240",
        "source_id": "villanova-mkt-2240-metadata",
    },
    "lc-econ": {
        "pid": "lewis-clark-ai-minor",
        "parser": "lc",
        "courses": [
            {
                "id": "lewis-clark-econ-303",
                "code": "ECON 303",
                "guard": "Content: The theory and practice of analyzing and interpreting da",
                "summary": "Uses econometric models, causal analysis, forecasting and "
                "computing for empirical economic research.",
            }
        ],
        "url": "https://docs.lclark.edu/undergraduate/economics/",
        "source_id": "lc-econ-metadata",
    },
    "lc-math": {
        "pid": "lewis-clark-ai-minor",
        "parser": "lc",
        "courses": [
            {
                "id": "lewis-clark-math-225",
                "code": "MATH 225",
                "guard": "Content: Basic skills and concepts that evolve from the study of ",
                "summary": "Studies vector spaces, matrices, determinants and eigenvalues.",
            },
            {
                "id": "lewis-clark-math-255",
                "code": "MATH 255",
                "guard": "Content: Introduction to principal statistical concepts and metho",
                "summary": "Develops statistical inference, regression and communication "
                "through data analysis.",
            },
            {
                "id": "lewis-clark-math-351",
                "code": "MATH 351",
                "guard": "Content: Introduction to statistical modeling. General model-buil",
                "summary": "Develops linear regression theory and practical model building.",
            },
            {
                "id": "lewis-clark-math-352",
                "code": "MATH 352",
                "guard": "Content: Introduction to simulation-based methods used in statist",
                "summary": "Uses simulation, resampling and Bayesian computation for "
                "statistical analysis.",
            },
            {
                "id": "lewis-clark-math-451",
                "code": "MATH 451",
                "guard": "Content: A two-semester sequence in the theory of probability and",
                "summary": "Studies probability distributions, limit theorems and statistical "
                "inference.",
            },
        ],
        "url": "https://docs.lclark.edu/undergraduate/mathematics/",
        "source_id": "lc-math-metadata",
    },
    "lc-psy": {
        "pid": "lewis-clark-ai-minor",
        "parser": "lc",
        "courses": [
            {
                "id": "lewis-clark-psy-311",
                "code": "PSY 311",
                "guard": "Content: Continuation of PSY 200 ; emphasis on theory and experim",
                "summary": "Applies experimental design, variance and regression methods using "
                "statistical software.",
            }
        ],
        "url": "https://docs.lclark.edu/undergraduate/psychology/",
        "source_id": "lc-psy-metadata",
    },
    "lc-phil": {
        "pid": "lewis-clark-ai-minor",
        "parser": "lc",
        "courses": [
            {
                "id": "lewis-clark-phil-241",
                "code": "PHIL 241",
                "guard": "Content: Exploration of ethical implications specific to data col",
                "summary": "Examines ethical and legal questions concerning data, privacy and "
                "automated decisions.",
            }
        ],
        "url": "https://docs.lclark.edu/undergraduate/philosophy/",
        "source_id": "lc-phil-metadata",
    },
    "lc-rhms": {
        "pid": "lewis-clark-ai-minor",
        "parser": "lc",
        "courses": [
            {
                "id": "lewis-clark-rhms-241",
                "code": "RHMS 241",
                "guard": "Content: Entanglements of democracy and data, including how emerg",
                "summary": "Examines relationships between big data, democracy, surveillance, "
                "misinformation and equality.",
            },
            {
                "id": "lewis-clark-rhms-360",
                "code": "RHMS 360",
                "guard": "Content: Investigation of what happens behind the screens of our ",
                "summary": "Examines digital platforms and infrastructure through labor, "
                "environment, surveillance, race and gender.",
            },
        ],
        "url": "https://docs.lclark.edu/undergraduate/communication/",
        "source_id": "lc-rhms-metadata",
    },
    "indiana-cs-ai-specialization-source-4": {
        "pid": "indiana-cs-ai-specialization",
        "parser": "iu",
        "courses": [
            {
                "id": "iu-ai-csci-b-351",
                "code": "CSCI-B 351",
                "guard": "CSCI-B 351 Introduction to Artificial Intelligence (3 cr.) P: CSC",
                "summary": "Introduces AI representations and "
                "methods including search, logic, "
                "neural networks and learning.",
            },
            {
                "id": "iu-ai-csci-b-365",
                "code": "CSCI-B 365",
                "guard": "CSCI-B 365 Introduction to Data Analysis and Mining (3 cr.) Basic",
                "summary": "Covers data preparation, clustering "
                "and prediction to discover patterns "
                "in data.",
            },
            {
                "id": "iu-ai-csci-b-455",
                "code": "CSCI-B 455",
                "guard": "CSCI-B 455 Principles of Machine Learning (3 cr.) P: MATH-M 211 a",
                "summary": "Develops mathematical and "
                "computational machine-learning "
                "methods through derivation and "
                "implementation.",
            },
            {
                "id": "iu-ai-csci-b-355",
                "code": "CSCI-B 355",
                "guard": "CSCI-B 355 Autonomous Robotics (3 cr.) Two semesters of computer ",
                "summary": "Combines mechanics, electronics, "
                "programming and cognitive science "
                "to build and control robots.",
            },
            {
                "id": "iu-ai-csci-b-363",
                "code": "CSCI-B 363",
                "guard": "CSCI-B 363 Bioinformatics Algorithms (4 cr.) One programming clas",
                "summary": "Applies algorithms and computing to biological problems.",
            },
            {
                "id": "iu-ai-csci-b-456",
                "code": "CSCI-B 456",
                "guard": "CSCI-B 456 Image Processing (3 cr.) P: CSCI-C 212 and MATH-M 212.",
                "summary": "Studies image representation, processing operations and analysis.",
            },
            {
                "id": "iu-ai-csci-b-457",
                "code": "CSCI-B 457",
                "guard": "CSCI-B 457 Introduction to Computer Vision (3 cr.) P: CSCI-A 310 ",
                "summary": "Studies recognition, scene "
                "understanding and motion using "
                "computer-vision methods.",
            },
            {
                "id": "iu-ai-csci-b-401",
                "code": "CSCI-B 401",
                "guard": "CSCI-B 401 Fundamentals of Computing Theory (3 cr.) P: CSCI-C 212",
                "summary": "Studies formal languages, computational limits and verification.",
            },
            {
                "id": "iu-ai-csci-b-403",
                "code": "CSCI-B 403",
                "guard": "CSCI-B 403 Introduction to Algorithm Design and Analysis (3 cr.) ",
                "summary": "Analyzes and designs algorithms for "
                "searching, sorting and other "
                "computational problems.",
            },
            {
                "id": "iu-ai-csci-b-405",
                "code": "CSCI-B 405",
                "guard": "CSCI-B 405 Applied Algorithms (3 cr.) P: Prerequisite: CSCI-C 343",
                "summary": "Develops algorithmic approaches to "
                "mathematical and practical "
                "problems.",
            },
            {
                "id": "iu-ai-csci-p-415",
                "code": "CSCI-P 415",
                "guard": "CSCI-P 415 Introduction to Verification (3 cr.) P: CSCI-C 311. To",
                "summary": "Uses automated reasoning, model "
                "checking and theorem proving to "
                "verify software and hardware.",
            },
        ],
        "url": "https://bulletins.iu.edu/iub/sice/2026-2027/undergraduate/courses/computer-science.shtml",
        "source_id": "indiana-cs-ai-specialization-source-4-metadata",
    },
    "msu-231": {
        "pid": "michigan-state-university-artificial-intelligence-minor-minor",
        "parser": "msu",
        "courses": [
            {
                "id": "msu-cse-231",
                "code": "CSE 231",
                "guard": "Introduction to programming using Python. Design, implementation ",
                "summary": "Introduces Python programming and program design, testing and "
                "problem solving.",
            }
        ],
        "effective": "SS14 - Open",
        "url": "https://reg.msu.edu/Courses/Search.aspx?CourseID=356067",
        "source_id": "msu-231-metadata",
    },
    "msu-232": {
        "pid": "michigan-state-university-artificial-intelligence-minor-minor",
        "parser": "msu",
        "courses": [
            {
                "id": "msu-cse-232",
                "code": "CSE 232",
                "guard": "Continuation of object-centered design and implementation in C++.",
                "summary": "Develops C++ programming, abstraction and fundamental data structures.",
            }
        ],
        "effective": "FS22 - Open",
        "url": "https://reg.msu.edu/Courses/Search.aspx?CourseID=367946",
        "source_id": "msu-232-metadata",
    },
    "msu-260": {
        "pid": "michigan-state-university-artificial-intelligence-minor-minor",
        "parser": "msu",
        "courses": [
            {
                "id": "msu-cse-260",
                "code": "CSE 260",
                "guard": "Propositional and first order logic. Equivalence and methods of p",
                "summary": "Studies logic, proofs, counting, relations and discrete "
                "structures used in computing.",
            }
        ],
        "effective": "FS25 - Open",
        "url": "https://reg.msu.edu/Courses/Search.aspx?CourseID=370916",
        "source_id": "msu-260-metadata",
    },
    "msu-300": {
        "pid": "michigan-state-university-artificial-intelligence-minor-minor",
        "parser": "msu",
        "courses": [
            {
                "id": "msu-cse-300",
                "code": "CSE 300",
                "guard": "Professional responsibilities and informed judgments in computing",
                "summary": "Examines professional judgment, legal and ethical "
                "responsibilities and the social effects of computing.",
            }
        ],
        "effective": "FS26 - Open",
        "url": "https://reg.msu.edu/Courses/Search.aspx?CourseID=371919",
        "source_id": "msu-300-metadata",
    },
    "msu-331": {
        "pid": "michigan-state-university-artificial-intelligence-minor-minor",
        "parser": "msu",
        "courses": [
            {
                "id": "msu-cse-331",
                "code": "CSE 331",
                "guard": "Design, analysis, and application of fundamental algorithms and d",
                "summary": "Designs, analyzes and applies fundamental algorithms and data "
                "structures.",
            }
        ],
        "effective": "FS26 - Open",
        "url": "https://reg.msu.edu/Courses/Search.aspx?CourseID=371907",
        "source_id": "msu-331-metadata",
    },
    "msu-402": {
        "pid": "michigan-state-university-artificial-intelligence-minor-minor",
        "parser": "msu",
        "courses": [
            {
                "id": "msu-cse-402",
                "code": "CSE 402",
                "guard": "Automated techniques used for feature extraction and pattern matc",
                "summary": "Studies feature extraction and matching for face, fingerprint and "
                "iris recognition.",
            }
        ],
        "effective": "FS25 - Open",
        "url": "https://reg.msu.edu/Courses/Search.aspx?CourseID=370817",
        "source_id": "msu-402-metadata",
    },
    "msu-404": {
        "pid": "michigan-state-university-artificial-intelligence-minor-minor",
        "parser": "msu",
        "courses": [
            {
                "id": "msu-cse-404",
                "code": "CSE 404",
                "guard": "Core principles and techniques for machine learning including alg",
                "summary": "Develops machine-learning models and implements learning algorithms.",
            }
        ],
        "effective": "FS25 - Open",
        "url": "https://reg.msu.edu/Courses/Search.aspx?CourseID=370818",
        "source_id": "msu-404-metadata",
    },
    "msu-440": {
        "pid": "michigan-state-university-artificial-intelligence-minor-minor",
        "parser": "msu",
        "courses": [
            {
                "id": "msu-cse-440",
                "code": "CSE 440",
                "guard": "Advanced algorithms and methods in intelligent systems and artifi",
                "summary": "Studies advanced methods and algorithms for artificial intelligence.",
            }
        ],
        "effective": "FS26 - Open",
        "url": "https://reg.msu.edu/Courses/Search.aspx?CourseID=371934",
        "source_id": "msu-440-metadata",
    },
}


def text(node):
    return " ".join(node.get_text(" ", strip=True).split()) if node else ""


def fields_after(heading):
    fields = {}
    for node in heading.next_siblings:
        if getattr(node, "name", None) == "h3":
            break
        if not getattr(node, "name", None):
            continue
        label, value = node.select_one(".col-md-3"), node.select_one(".col-md-7")
        if label and value:
            fields[text(label)] = text(value)
    return fields


def parse_metadata(html, key):
    config = CONFIG[key]
    soup = BeautifulSoup(html, "html.parser")
    full = text(soup)
    rows = []
    for spec in config["courses"]:
        kind, code = config["parser"], spec["code"]
        row = {
            "id": spec["id"],
            "code": code,
            "source_id": config["source_id"],
            "url": config["url"],
        }
        if kind == "uga":
            number = re.search(r"\d+", code)[0]
            if not re.search(r"CSCI\s*(?:\([^)]*\))?\s*" + number, full):
                raise ValueError("UGA course identity missing")
            fields = {text(p): text(p.find_next_sibling()) for p in soup.select("p.large-mws")}
            raw = fields.get("Course Description", "")
            prereq = fields.get("Undergraduate Prerequisite", fields.get("Prerequisite"))
            if "Undergraduate Pre or Corequisite" in fields:
                prereq = (
                    "Prerequisite or corequisite: " + fields["Undergraduate Pre or Corequisite"]
                )
            row["prerequisites"] = prereq
            amount = re.fullmatch(r"(\d+) hours\.?", text(soup.select_one(".credit-number")))
            if amount:
                row.update(credits=int(amount[1]), credit_unit="unknown")
        elif kind == "lc":
            block = next(
                (
                    b
                    for b in soup.select(".courseblock")
                    if text(b.select_one(".courseblocktitle")).startswith(code + " ")
                ),
                None,
            )
            if block is None:
                raise ValueError("Lewis & Clark course identity missing")
            raw = text(block.select_one(".courseblockdesc"))
            match = re.search(
                r"Prerequisites:\s*(.*?)(?= Restrictions:| Usually offered:| Semester credits:)",
                raw,
            )
            restriction = re.search(
                r"Restrictions:\s*(.*?)(?= Usually offered:| Semester credits:)", raw
            )
            credit = re.search(r"Semester credits: (\d+)\.", raw)
            if not match or not credit:
                raise ValueError("Lewis & Clark labeled metadata changed")
            row.update(
                prerequisites=match[1]
                + (" Restrictions: " + restriction[1] if restriction else ""),
                credits=int(credit[1]),
                credit_unit="semester_hours",
            )
        elif kind == "iu":
            block = next(
                (
                    b
                    for b in soup.select("li.nobullet")
                    if text(b.select_one(".ctitle")).startswith(code + " ")
                ),
                None,
            )
            if block is None:
                raise ValueError("Indiana course identity missing")
            raw = text(block)
            amount = re.search(r"\((\d+) cr\.\)", text(block.select_one(".ctitle")))
            if not amount:
                raise ValueError("Indiana fixed course credit amount missing")
            row.update(credits=int(amount[1]), credit_unit="unknown")
            remaining = raw[len(text(block.select_one(".ctitle"))) :].strip()
            pr = re.match(r"P:\s*(.+?\.)\s", remaining)
            if pr:
                row["prerequisites"] = pr[1]
            # Recommended programming preparation does not become a prerequisite.
        elif kind == "rochester":
            if config["term"] not in full or "Term Schedule" not in full:
                raise ValueError("Rochester term identity changed")
            tr = next((tr for tr in soup.select("tr") if text(tr).startswith(code + "-")), None)
            if tr is None:
                raise ValueError("Rochester course section missing")
            raw = text(tr.find_next_sibling("tr"))
            # The schedule does not state course credit amounts or formal prerequisites.
        elif kind == "msu":
            candidates = [
                (h, fields_after(h)) for h in soup.find_all("h3") if text(h).startswith(code + " ")
            ]
            current = [
                (h, f) for h, f in candidates if f.get("Effective Dates:") == config["effective"]
            ]
            if len(current) != 1 or not config["effective"].endswith("Open"):
                raise ValueError("MSU reviewed current course version missing or ambiguous")
            _, fields = current[0]
            raw = fields.get("Description:", "")
            pr = fields.get("Prerequisite:")
            restrictions = fields.get("Restrictions:")
            if restrictions:
                pr = (pr + ". " if pr else "") + "Enrollment restrictions: " + restrictions
            row["prerequisites"] = pr
            amount = re.search(r"Credits:\s*(\d+)", fields.get("Credits:", ""))
            if not amount:
                raise ValueError("MSU course credit amount missing")
            row.update(credits=int(amount[1]), credit_unit="unknown")
        elif kind == "villanova":
            from atlas.adapters.villanova_curriculum import parse_course

            parsed = parse_course(html, pid=config["pid"], code=code, url=config["url"])["courses"][
                0
            ]
            row.update({k: parsed[k] for k in ["credits", "credit_unit", "prerequisites"]})
            raw = text(soup.select_one(".body-text-wrapper"))
            if code == "MGT 3180":
                if "Junior or senior standing" not in raw:
                    raise ValueError("Villanova MGT3180 restriction missing")
                row["prerequisites"] = (row["prerequisites"] or "") + "; Junior or senior standing."
            # MGT3180 has an AI title but an inconsistent management description.
        else:
            raise ValueError("Unknown metadata source type")
        if spec["guard"] and spec["guard"] not in raw:
            raise ValueError("Reviewed description changed: " + code)
        if spec["summary"]:
            row["description"] = spec["summary"]
        rows.append(row)
    if not rows:
        raise ValueError("No reviewed metadata found")
    return {"id": config["pid"], "courses": rows}


def parse_aim(html, key):
    full = text(BeautifulSoup(html, "html.parser"))
    if key == "georgia":
        guards = ["overall aim", "Developers", "Deployers", "Integrators"]
        pid = "georgia-ai-emphasis"
        statement = "Prepare students to develop AI models, deploy them in practice and integrate AI into organizations."
        sid = pid + "-identity"
        locator = "Overall aim: Developers, Deployers and Integrators"
    elif key == "villanova":
        guards = ["business intelligence", "decision modeling", "data mining"]
        pid = "villanova-analytics-ai-minor"
        statement = "Develop business intelligence, decision modeling, data-mining and AI skills for business decisions."
        sid = pid + "-identity"
        locator = "About: skills and coursework overview"
    else:
        raise ValueError("Unknown program aim source")
    if any(g.lower() not in full.lower() for g in guards):
        raise ValueError("Program aim context changed")
    return {
        "id": pid,
        "outcomes": [
            {
                "text": statement,
                "kind": "source_stated",
                "statement_type": "program_aim",
                "source_id": sid,
                "locator": locator,
            }
        ],
    }
