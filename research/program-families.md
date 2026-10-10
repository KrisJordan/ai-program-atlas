# Evidence-backed program families

Reviewed 2026-10-10. This is an authoring decision and a draft fixture, not a new university credential or a schema change. The initial family is `northeastern-ai-combined-degrees`, with three independently verified Boston BS variants: Artificial Intelligence and Philosophy; Artificial Intelligence and Business Administration; and Artificial Intelligence and Biology. Other Northeastern combinations require their own membership/core review before joining.

## Why this is a supported family

Northeastern's [Khoury Combined Majors overview](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/) explicitly describes designed degrees spanning two disciplines, with substantial study in each and an integrative course connecting them. Its Programs tab lists these three under Bachelor of Science. Their individual catalog pages identify the same combined-major context in the breadcrumbs and explicitly organize requirements into an AI component, partner-discipline components and integrative requirements:

- [AI and Philosophy, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-philosophy-bs-bos/): Artificial Intelligence Requirements, Philosophy Requirements and Integrative Requirement.
- [AI and Business Administration, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-business-admnistration-bs-bos/): Artificial Intelligence Courses, Business Courses, Business Concentration and Integrative Course.
- [AI and Biology, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-biology-bs-bos/): Artificial Intelligence Requirements, Biology Requirements and Integrative Requirements, including a separately labeled Capstone subsection.

Thus the family rests on the university's explicit combined-degree design and curricular component structure, not title similarity, shared course hashes or institutional affiliation alone. The family label and the selection of a reusable common core are **analyst_classified**. Each variant's **integrated** relationship is **source_stated**, grounded in the official combined-major structure. The title order does not establish that AI is the dominant discipline. These are distinct combined-degree program records, not three concentrations in a newly invented parent degree and not two separately awarded majors.

All three pages identify Khoury College of Computer Sciences in their scoped breadcrumbs; the combined-major overview says Khoury offers the programs. That is the only hosting unit entered in the draft. Partner college/department hosting has not been established from those pages and is not inferred from discipline names. Existing award identities, Boston campus labels, program IDs, course IDs, semester units and program-specific evidence are preserved.

## Exact common requirement scope

The following eight required units appear within the explicitly named AI component of **each** of the three catalogs. Course identities, bundle membership, required-versus-optional status and published row credits were checked against the actual tables. The reusable shared core contains these units and the common placement policy, rather than an entire AI table whose other rows vary.

| Shared unit | Course identity or bundle | Published row credits |
| --- | --- | ---: |
| Introductory programming | CS 2000 + CS 2001 | 5 semester hours, subject to placement policy |
| Programming implementation | CS 2100 + CS 2101 | 5 semester hours |
| Databases | CS 3200 | 4 semester hours |
| Advanced programming with data | DS 3500 | 4 semester hours |
| Mathematical AI foundations | DS 3000 | 4 semester hours |
| Information presentation/visualization | DS 4200 | 4 semester hours |
| Large-scale storage/retrieval | DS 4300 | 4 semester hours |
| Machine learning | DS 4400 | 4 semester hours |

This is eight requirement units containing ten course identities. Bundle credits remain attached to the requirement, not assigned to every bundled course. The ninth shared node records the common placement policy: students who place out of CS 2000/2001 substitute 4–5 semester hours of CS/CY/DS courses at level 3000 or above that are not otherwise required. It remains a conditional policy note requiring individual review. Accordingly, the family does **not** advertise an unconditional shared-credit total or a complete/executable degree plan.

The shared nodes retain the exact common fields in the reviewed records. Every occurrence has an explicit binding to its original program requirement ID, parent ID, program source ID and course IDs. Semantic review of the catalog components determined which nodes qualify; equality checks on the resulting fields only validate the mechanical draft. Individual program requirement trees remain the authority for all unshared details.

## Actual variant differences

| Component | Philosophy | Business Administration | Biology |
| --- | --- | --- | --- |
| Discrete/reasoning requirement inside AI component | CS 1800 | CS 1800 | MATH 1365 or MATH 1465 |
| Additional named advanced AI requirement | DS 4420 or DS 4440 | DS 4420 | No separately specified advanced-AI requirement in the reviewed AI component; broad electives can still permit advanced courses |
| Orientation and professional development | Philosophy/interdisciplinary/CS seminar options and program-specific co-op options | Business/interdisciplinary/CS seminar options and business co-op options | Biology/science/interdisciplinary/CS seminar options and program-specific co-op options |
| Khoury elective rule | 4 hours, open CS/CY/DS ranges plus named options; EECE 2322 + 2323 bundle is listed | 4 hours with similar ranges/options and the EECE 2322 + 2323 bundle | 4 hours with similar ranges/options, but EECE 2322 is listed without the lab bundle |
| Partner component | Philosophy core, philosophy electives and critical-philosophy elective pool | Business core, business elective, concentration and experiential requirements | Biology core/labs, biology elective pools, supporting chemistry/physics/math |
| Explicit integration | Two philosophy-related choice groups | MKTG 4604 | Integrative course choice plus a named capstone choice; BIOL 4900 has a concurrent research condition |
| General electives | 28 semester hours | 16 semester hours, plus the stated Marketing Analytics condition when applicable | 20 semester hours |
| Published total degree credits | 128 semester hours | 130 semester hours | 138 semester hours |

The discrete/reasoning difference is a **variant-specific requirement difference**, not a claim that Northeastern grants course equivalence or an automatic substitution between CS 1800 and MATH 1365/1465. Likewise, named advanced-AI requirements outside the common core remain local; their omission from a required block is not a prohibition against taking those courses.

The conservative shared scope means all three current variants bind all nine shared nodes, with **no exclusions or replacements needed**. Their additional requirements remain in their local trees. We do not invent overrides to demonstrate the mechanism. If later catalog evidence changes a genuinely shared requirement for one variant, its exclusion/replacement must carry a reason and the affected program's source; a new course, a missing parser row or a title resemblance is insufficient evidence for that decision.

Source-based component mappings identify local AI-component rows, partner-domain rows and integration rows by their explicit catalog headings. Remaining local policies and supporting/writing requirements are `other` with an analyst classification. Only Biology's explicitly named Capstone is described as a capstone; the other integrative requirements are not relabeled as capstones.

## Draft files and safe transformation boundary

- `research/families/northeastern-ai-combined-degrees.json`: family definition, four official sources and nine shared requirement templates.
- `research/families/northeastern-ai-combined-bindings.json`: three variant descriptors, 27 explicit requirement bindings, verified hosting-unit provenance, empty override lists and disjoint local component mappings.

These research files preserve the reviewed authoring fixtures. After the coordinator implemented the resolver and authorized activation, the family definition was copied to `data/families/northeastern-ai-combined-degrees.json`. The three program seeds now retain their local requirements and replace nine repeated nodes each with explicit bindings. Resolution restores the original IDs, parents, sources, course memberships and requirement fields exactly. The family is stored once; every award retains its own full effective graph.

All three curricula retain their partial status and existing unresolved degreewide, elective, concentration and course-metadata gaps. Family membership cannot upgrade evidence, refresh a verification date or imply that the other combined-major variants have been audited. The family does not introduce a new eligibility conclusion, unit conversion, degree total, ranking or outcome claim.

Production activation verification: all three original flat requirement graphs were captured before transformation and reconstructed exactly, excluding only the resolver’s new origin/component annotations. Five real-data family tests verify these graph fingerprints, shared-change propagation, unchanged local requirements, source-aware validation, relational storage, repeat idempotence and distinct exported awards. Together with the Northeastern/discovery suites, 135 tests passed.
