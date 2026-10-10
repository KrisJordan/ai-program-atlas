# National universities official-source discovery survey

Checked 2026-10-10. This ledger covers the 108 National Universities cohort members enumerated in `data/cohort.json`, including rank-100 ties. Ranking membership relies on the secondary 2027 table recorded by the cohort research; this survey does not independently authenticate U.S. News rankings.

## Exact contribution

- 108 institution rows: **28 confirmed**, **3 inspected**, **5 inaccessible**, **72 pending**.
- **72 discovered program identities**: **44 degrees, 25 minors, 3 concentrations**. Promoted to separate program records and adapters; IDs are in `research/national-discovery-manifest.json`.
- **0 no-qualifying-program conclusions.** Targeted searches do not establish institution-wide absence.
- **0 curriculum-complete records from this survey.** Every discovery record has curriculum pending, no inferred course requirements or credits, no guessed first-offering date, and unknown institutional calendar.
- Four pilot institutions remain pending in this survey because dedicated CMU, Penn, Purdue and Penn State research provides their records. Other parallel surveys are separate evidence and should be merged by institution without letting a pending row overwrite stronger findings.

## Method

Search was used for discovery, followed by opening official university catalog, department, program-directory or announcement sources. A successful source read with a qualifying undergraduate title supported confirmation. Search snippets alone were not promoted. Each discovery retains its exact official evidence URL; each institution row retains sources, check date and scope notes. An institution marked confirmed means at least one qualifying identity was found, not that its entire curriculum or offering inventory is complete.

Generic Computer Science degrees, AI research centers, courses, graduate programs and certificates were excluded. Degrees, minors and explicitly named concentrations were kept separate. The title rule requires standalone AI or the phrase Artificial Intelligence. Florida GeoAI and Vanderbilt GenAI were held as inspected scope questions; Chapman Collaborative Intelligence was excluded on title. Failed catalog access was recorded without bypassing authentication or access restrictions.

## Confirmed institutions

| Institution | Program identities | First official evidence source |
| --- | ---: | --- |
| Duke University | 3 | [Official source](https://cs.duke.edu/undergraduate/degrees/minors) |
| Northwestern University | 2 | [Official source](https://catalogs.northwestern.edu/undergraduate/engineering-applied-science/artificial-intelligence/artificial-intelligence-major/) |
| Cornell University | 1 | [Official source](https://bowers.cornell.edu/programs/artificial-intelligence-minor) |
| Rice University | 1 | [Official source](https://ga.rice.edu/programs-study/departments-programs/engineering/artificial-intelligence/) |
| University of Notre Dame | 1 | [Official source](https://mendoza.nd.edu/undergraduate/ai-analytics-in-business/) |
| Emory University | 2 | [Official source](https://computerscience.emory.edu/undergraduate/degrees-and-requirements/minors.html) |
| University of Michigan–Ann Arbor | 1 | [Official source](https://www.si.umich.edu/programs/undergraduate-minors/human-centered-artificial-intelligence) |
| University of Southern California | 1 | [Official source](https://www.marshall.usc.edu/news/usc-marshall-launches-applied-ai-and-business-minor) |
| Georgia Institute of Technology | 2 | [Official source](https://catalog.gatech.edu/programs/minor-artificial-intelligence-machine-learning/) |
| University of California San Diego | 1 | [Official source](https://catalog.ucsd.edu/curric/CSE-ug.html) |
| Boston College | 1 | [Official source](https://www.bc.edu/bc-web/schools/morrissey/departments/computer-science/academics/programs.html) |
| Northeastern University | 25 | [Official source](https://catalog.northeastern.edu/undergraduate/engineering/civil-environmental/environmental-engineering-artificial-intelligence-bsenve/) |
| Case Western Reserve University | 3 | [Official source](https://bulletin.case.edu/engineering/computer-data-sciences/artificial-intelligence-minor/) |
| Lehigh University | 1 | [Official source](https://engineering.lehigh.edu/cse/academics/undergraduate/bs-ai-ml-ds) |
| University of Maryland, College Park | 2 | [Official source](https://academiccatalog.umd.edu/undergraduate/colleges-schools/computer-mathematical-natural-sciences/computer-science/artificial-intelligence-computational-structures-ai-systems-major/) |
| Virginia Tech | 1 | [Official source](https://website.cs.vt.edu/academic/undergraduate/ai-minor.html) |
| University of Miami | 3 | [Official source](https://bulletin.miami.edu/undergraduate-academic-programs/business/business-technology/ai-for-business-technology-minor/) |
| Stevens Institute of Technology | 2 | [Official source](https://www.stevens.edu/program/bachelors-degree-in-artificial-intelligence) |
| Tulane University of Louisiana | 1 | [Official source](https://catalog.tulane.edu/science-engineering/computer-science/artificial-intelligence-minor/) |
| Michigan State University | 1 | [Official source](https://reg.msu.edu/ACADEMICPROGRAMS/ProgramDetail.aspx?PType=MNUN&Program=AINTL_MNUN) |
| Clemson University | 1 | [Official source](https://www.clemson.edu/cecas/departments/computing/academics/undergrad/degrees/) |
| New Jersey Institute of Technology | 1 | [Official source](https://catalog.njit.edu/undergraduate/management/management/business-with-ai-bs/) |
| University at Buffalo–SUNY | 9 | [Official source](https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html) |
| Gonzaga University | 1 | [Official source](https://www.gonzaga.edu/school-of-engineering-applied-science/degrees-and-programs/electrical-computer-engineering/ece-tech-minors/ai-minor) |
| Rochester Institute of Technology | 2 | [Official source](https://www.rit.edu/study/artificial-intelligence-bs) |
| Florida International University | 1 | [Official source](https://cec.fiu.edu/news-events/news/2026/new-artificial-intelligence-ai-minor-prepares-fiu-engineering-computing-students-for-an-ai-driven-future.html) |
| University of Iowa | 1 | [Official source](https://catalog.registrar.uiowa.edu/engineering/electrical-computer-engineering/artificial-intelligence-theory-methods-applications-minor/) |
| University of South Florida | 1 | [Official source](https://www.usf.edu/ai-cybersecurity-computing/academics/undergraduate/bsai.aspx) |

## Material qualifications

- Northeastern contributes 22 combined AI BS programs from its official combined-major directory, plus an environmental-engineering combined degree and two minors. Individual combined-program curricula are not extracted; these are distinct named credentials, not 25 different universities.
- Buffalo contributes seven explicitly BS-labeled AI-plus-discipline degrees and two minors from its official department directory. Another AI and Philosophy, Politics and Economics listing lacks an established award in the inspected material and remains a lead.
- Maryland's Human-Centered AI BA is listed for fall 2026; the BSAI catalog and official AI hub identify fall 2027 availability. The BSAI record is marked announced. These dates are not converted into first-instruction claims.
- Case Western's official AI education directory describes new BA and BS AI pathways. Their current activity, final catalog details and full curricula remain pending. The separate Applied AI minor is expressly in approval and was not promoted.
- Miami's BBA and Northeastern's BSEnvE are stored as `other` under the contract award enum; their actual awards remain explicit in notes or titles. Miami's linked BSBA variant needs separate inspection.
- Official catalogs at MIT, Syracuse, Tufts, Baylor and NC State did not return usable program content in the attempted reads. These rows record access failures, not evidence of absence.
- USC's AI BS and other AI minors, Michigan's technical AI minor and other uninspected program leads remain follow-up work. The confirmed rows do not imply those universities have only the records presently listed.

## Refresh behavior and validation

The shared `atlas/adapters/discovery_common.py` helper validates a visible title in content headings or links, and an award/type in the same bounded program card or heading section. It excludes navigation and script text and rejects password or access pages. Each program adapter declares its own source URL, ID, expected title, award and type. Successful parsing returns **only identity fields**, never seed metadata, inferred curriculum, verification dates or old observations. Conservative parse failures require review and do not establish program absence. Full live refresh validation of all 72 adapters is not claimed.

Synthetic regression checks cover missing titles, unrelated directory awards, navigation-only title mentions, login/password pages, and registration/schema checks for every generated record. At this checkpoint, the existing virtual environment equivalents of the requested commands passed: `.venv/bin/python -m pytest -q` reported **129 passed, 4 skipped**; `.venv/bin/atlas build` built **83 programs and 174 institutions**. The `uv` command was unavailable on PATH in this agent shell. Browser checks are owned by the frontend/integration work; skipped tests here are not a deployment verification.

## Remaining work

Merge parallel institutional surveys and complete remaining official catalog/program-directory checks. Review held compound-title scope questions. Verify program activity and catalog years, expand each discovery into course/requirement/outcome evidence, and validate refresh parsers against permitted live responses. Complete authoritative ranking-source verification separately. Preserve pending and inaccessible states until genuine evidence resolves them.
