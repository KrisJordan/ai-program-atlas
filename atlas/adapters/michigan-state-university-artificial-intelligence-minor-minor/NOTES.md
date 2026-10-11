# Artificial Intelligence

Official identity source: https://reg.msu.edu/ACADEMICPROGRAMS/ProgramDetail.aspx?PType=MNUN&Program=AINTL_MNUN

Directory/identity verified; curriculum pending. No courses, requirements or outcomes have yet been extracted.

Official undergraduate program source inspected; qualifying title confirmed. Institution-wide inventory and curriculum extraction remain incomplete.

The adapter validates a title in visible content headings or links and the award/kind in its local card or heading section. It returns only observed identity fields and never replays seed metadata, curriculum, or dates. A failure means review is required; it does not mean the program is absent. Tests use synthetic HTML to verify rejection behavior; live refresh is not claimed.

## Curriculum review — 2026-10-10

Supersedes identity-only pending coverage. The official [program detail](https://reg.msu.edu/ACADEMICPROGRAMS/ProgramDetail.aspx?PType=MNUN&Program=AINTL_MNUN) and [Undergraduate Education, Selecting a Minor](https://reg.msu.edu/AcademicPrograms/Text.aspx?Section=110#s261) were fetched with the robots-aware bounded client. The Engineering catalog context was also inspected; its general minor section describes other offerings rather than adding an AI-specific completion rule.

**Complete minor requirement inventory:** 12 distinct course options, 8 requirement/policy nodes. Six required courses total 19 source credits; choose one of six advanced options for three credits; minimum total 22. CSE 231 and 260 each require 3.0 for acceptance and remain the same required course entities, without double-counting admission credits. Apply to CSE; enrollment may be limited. Calculus I is explicitly implied preparation, but its code/extra credit amount is not invented. CS/Computer Engineering/Computational Data Science/Data Science BS students and CS-minor students are excluded. Degree overlap needs administering department/college approval. The university minor policy adds primary-degree relationship, same-name-major exclusion and explicitly stated unique-credit rules. It does not impose an unstated unique-credit minimum on this minor.

This is a complete inventory judgment for the **minor**, not the whole bachelor degree or a degree audit for an individual. The reviewer audit has no unresolved local requirement rule. Course descriptions/prerequisites, unit/calendar normalization, public sites/syllabi, catalog edition and launch date remain metadata gaps. Credits are preserved as source values with unit `unknown`, not compared to semester systems.

The adapter reads actual table cells, group credits, admission grade and policy section; changed exclusions/overlap/preparation structure fail closed. Additional-source parser observes the university policy. Parsers emit partial observations; only the reviewed seed certifies complete. Synthetic tests vary grades, course titles and minimum policy credits. No raw source pages are committed.

## Evidence quality review — 2026-10-11, batch 2

Current open-ended course versions were read through the public course search and eight observed View all versions links. Historical versions in those pages are not treated as current. The minor excludes CS/CE/Computational Data Science/Data Science majors and the CS minor, yet required CSE 300 lists only Computational Data Science, Computer Science, Computer Science Minor and Lyman Briggs Computer Science Coordinate students. CSE 345 similarly omits the AI minor from its listed eligible programs; several electives restrict enrollment as well. No AI-minor exception was found in the reviewed sources, so eligibility remains unresolved and inventory is partial. Course 300 and 345 titles differ between minor table and course search; requirement-table titles remain unchanged. Published Credits remain unnormalized. CSE 345/434/446 and MTH 483 were visible in normal browser search, but their metadata is not automated in this bounded batch; their existing unknown fields remain null.

Source-specific parsers in `small_complete_metadata_batch2.py` validate the reviewed descriptions and extract labeled metadata. Fetches preserve actual cache timestamps. They emit observations only, never an audit or complete status. See the dated batch-2 research ledger for exact residual missingness.
