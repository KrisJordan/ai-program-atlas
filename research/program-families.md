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


## Verified expansion to 16 variants

Thirteen further catalog records were reviewed against their own current official pages and the official directory's Bachelor of Science bucket: Behavioral Neuroscience, Biochemistry, Chemistry, Design, Ecology and Evolutionary Biology, Economics, Environmental and Sustainability Sciences, Health Science, Linguistics, Mathematics, Physics, Psychology and Public Health. Their exact sources, fetch timestamps, source heading evidence, graph fingerprints and counts are retained in `research/families/northeastern-ai-combined-expansion.json`.

Every added variant explicitly requires the same eight course units and placement policy. Each shared rule was matched against the current page parse, checked for identical credits and bundle membership, and traced through required (`all`) ancestors. This is separate from the mechanical graph equality check. No exclusions or replacements are needed for these reviewed catalogs. The family now has 144 explicit bindings across 16 separate awards, nine common templates, 1,548 retained local nodes and 1,692 effective nodes. All curricula remain partial with their existing audits and course metadata gaps.

Two source-specific roles are preserved: Design places DS 4200 under **Integrative Requirements**, and Mathematics places DS 4400 under **Integrative Courses** within Integrative Requirements. Their course requirement facts are shared, but their original parent IDs and source-stated `integration` component remain variant-specific. Neither is moved into a newly invented local AI block, and neither integrative label is promoted to a capstone claim. Other shared course units occur in the explicitly named AI component. This permits common factual storage while retaining the university's different curricular role assignments.

The remaining Northeastern records have not inherited this family merely because their names resemble these variants. Each additional membership requires the same official relationship, award, required-status, common-rule and component review.

Expansion validation: 151 focused family, Northeastern curriculum/metadata and discovery tests passed. A fresh temporary database ingested all 16 reviewed variants, repeated with zero changes, exported and built the site with 1,692 effective requirements, and passed SQLite integrity checking. Production database and release plan are maintained separately by the coordinator.


## Final reviewed membership: 23 combined degrees

The remaining seven catalog inventories and family memberships were reviewed individually: Criminal Justice, Communication Studies, Speech-Language Pathology and Audiology, Sociology, International Affairs, Journalism, and Environmental Engineering. The source ledger and exact original-graph fingerprints are in `research/families/northeastern-ai-combined-final-expansion.json`. Each program's current scoped tables require all nine common nodes; their rule fields match, and their ancestry stays within the named AI component. No shared-course exclusion or replacement is needed in this edition. This completes family review of the **23 combined degrees currently documented in this atlas**, not a claim to enumerate every university offering.

The official combined-major directory separately lists 22 reviewed **BS** programs and Environmental Engineering and AI under **Bachelor of Science in Environmental Engineering (BSEnvE)**. The latter's own overview says the combined major blends the two disciplines, and its requirements explicitly separate engineering, AI and integration. The family therefore spans distinct award types; it does not rename BSEnvE as BS or turn the combined degree into two awards. Its source-stated relationship remains `integrated` regardless of title order. The family label/shared scope remains analyst-classified.

Hosting units also differ. Communication Studies' scoped catalog breadcrumb identifies **College of Arts, Media and Design → Communication Studies**. Environmental Engineering's identifies **College of Engineering → Civil and Environmental Engineering**. Those proven units are preserved with each program's catalog source. The other five added catalogs identify Khoury. We do not infer one common host merely from the directory or URL path, nor add partner colleges from discipline names.

The final family contains nine shared definitions, 207 explicit bindings, 2,390 local requirement nodes and 2,597 effective nodes across 23 concrete awards. All original requirement fields, IDs, parents, course memberships and source references reconstruct exactly; sources/courses remain individual program observations. All 23 curricula remain partial with their existing audits. International Affairs' regional paths, Journalism's transfer condition, Engineering's credit allocations and substitutions, and every local integration/capstone rule remain variant-specific.

Final expansion validation: 73 focused Northeastern/family tests passed, including all 23 original-graph fingerprints, shared-change propagation, separate awards/hosting, relational idempotence and export. A clean temporary database ingested 23 variants, repeated with zero changes, built 2,597 effective requirements and 1,466 course observations, and passed SQLite integrity.
