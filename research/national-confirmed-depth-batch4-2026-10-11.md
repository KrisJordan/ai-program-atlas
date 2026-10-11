# Confirmed-institution depth batch 4 — 2026-10-11

Six previously confirmed institutions received an additional bounded title search: Carnegie Mellon, Penn, Purdue, Georgia Tech, Northeastern and Buffalo. The dated [ledger](../data/surveys/national-confirmed-depth-batch4-2026-10-11.json) contains 32 official source references and the precise inspected/denied scope. Existing presence was not treated as proof of a complete institution inventory. No rankings, existing program files, shared family definitions, production database or site were changed.

## Three new verified records

| Record | Official curricular identity | Mapped observations | Boundary |
|---|---|---:|---|
| [CMU AI and Business](../data/programs/cmu-ai-business-concentration.json) | Concentration in Business Administration BS | 9 courses; 7 requirement nodes | One required course, three independent choose-one groups; minimum 36 CMU units and no double counting. Remaining local policies/metadata unreviewed. |
| [Georgia Tech Artificial Intelligence](../data/programs/georgia-tech-ai-thread.json) | AI Thread within BSCS | 23 courses; 24 nodes | Must pair with one of eight other Threads. One concentration record, not eight separate degree awards. Paired curricula remain unexpanded. |
| [Northeastern Chemical Engineering and AI](../data/programs/northeastern-chemical-engineering-ai-bsche.json) | Boston BSChE; 134 semester hours | 43 courses; 77 nodes | Local major page mapped; external policies/metadata remain partial. No unreviewed family inheritance. |

All three remain partial, with unknown first-offering dates. Course counts are observations, not mandatory-course totals. Exact source-specific adapters and NOTES accompany each record. They validate live source structure and parse current course/choice data; none replays a seed or emits a completeness audit.

Georgia Tech’s official catalog and department heading now use Artificial Intelligence. The old department URL and residual Intelligence labels are retained as historical-source context, not evidence of a rename date. The source calls the path a Thread; independent transcript recognition is unknown. Its paired-degree completion rule is explicit. Department course credits remain unknown-unit values.

Northeastern’s chemical department retains a Data Science URL and PlusOne paragraph, but its current AI heading links to the exact 2026–2027 AI BSChE catalog. The source-specific parser preserves that award rather than coercing BS. The shared CourseLeaf guard received only a tested BSChE extension. A program-specific guard corrects the generic summary for this paragraph: co-op **may** satisfy EX; IC/SI/DD/EX are not automatically fulfilled by engineering coursework. The family’s DS-based environmental-engineering core is a promising comparison, but policy applicability and every shared binding remain unreviewed for this new member. No existing family or seed is changed.

## Purdue: three explicit leads, not confirmed additions

The current [ECE Degree Information directory](https://engineering.purdue.edu/ECE/Academics/Undergraduates/Curriculum) names AI and Machine Learning concentrations in Computer Engineering and Electrical Engineering, plus an AI and Machine Learning minor for students outside ECE. All three linked catalog pages returned 403. They were not retried or bypassed.

The independent [ECE Academic Programs page](https://engineering.purdue.edu/ECE/Academics) says the same EE and Computer Engineering degrees are offered at Indianapolis and West Lafayette. It does not expressly locate these three subpaths. The directory labels another concentration Indianapolis-only, but absence of that qualifier is not sufficient campus evidence. A 2021 announcement describes a proposed minor and expected fall 2022 approval; it is not proof of first offering or current rules. Needed: a permitted current official catalog/advising source explicitly locating the AI/ML subpaths at the cohort campus and describing their approved requirements. No Purdue Global, Fort Wayne or Northwest credential was substituted.

## Other bounded results and remaining depth

Penn’s department and Engineering/Wharton directories corroborate existing records without a new qualifying title. The central catalog presented JavaScript robot verification and was not bypassed. College/Nursing and remaining departmental suboptions are not exhausted.

Buffalo’s program finder and AI/Society page identify the existing eight AI+X degrees and two minors. BSCS lists AI/ML/Data Mining as a research branch, without a formal declared curriculum in the inspected page; it is not promoted to a concentration. Graduate AI programs and certificates remain outside scope. Previously denied catalog paths were not retried.

CMU SCS lists the existing AI paths; Machine Learning and Intelligent Environments are not renamed. The deeper Tepper concentration panel produced the new record. Other departments remain only boundedly inspected. Georgia Tech’s other departments and Northeastern’s remaining college-specific directories likewise remain incomplete. These six ledger entries preserve confirmed presence without claiming inventory completeness or universal absence.

## Verification

Eleven focused synthetic/seed replay tests and 68 existing Northeastern curriculum/family regression tests passed. Tests exercise changed course codes and choice counts, wrong-degree/title rejection, navigation isolation, alternative-course semantics, required-versus-suggested boundaries, current BSChE guard and exact private-cache replay. A source-specific parser rejects changed NUpath applicability rather than silently making conditional EX universal. Raw downloaded HTML stays in ignored cache.

Isolated verification also passed: three initial program ingests, zero repeat changes; four source observations across three successful adapter runs, zero repeat candidates; SQLite integrity OK and no foreign-key violations; static build completed from that isolated database. The brief shared-tree import interruption cleared before the successful build.
