# Miami policy correctness review

## Transfer enrollment versus credit — 2026-10-11

The complete current [undergraduate transfer policy](https://bulletin.miami.edu/general-university-information/undergraduate-policies-and-procedures/undergraduate-transfer-credit-policy/) was fetched through the normal robots-aware transport and reread. The earlier seed claim of a categorical summer contradiction was too strong and is withdrawn.

The source excludes summer from one concurrent-enrollment prohibition. Its separate credit-acceptance section rejects outside coursework during active Miami enrollment, explicitly including a Miami summer Session A course and an outside Session B course. Its financial-aid clause excludes concurrent outside summer courses from federal, state and institutional aid administered through Miami. Enrollment, credit acceptance and aid are different facts: the summer exception does not grant transfer credit, degree applicability or aid.

The MATES process also distinguishes required evaluation from preapproval discretion. Students must use the official process; future requests should be submitted in the prior semester, and the university reserves the right to reject work taken without preapproval. The previous summary’s categorical instruction to obtain approval before enrolling is replaced with these exact scopes. Preapproved equivalence remains subject to university policy and the college’s degree-applicability decision. Transcript deadlines, repeat restrictions and the regular-GPA versus Latin-honors distinction remain explicit.

The four degree records retain their existing stable requirement IDs, although the legacy identifier contains `summer-transfer-conflict`. Their current titles and summaries no longer claim a contradiction. The same narrow correction is applied to the existing AI for Business Technology minor because it cites the identical current university policy; this does not constitute a full minor re-audit or change its other requirements. Every record remains partial, and available course/policy review continues.

`miami_transfer_scope.py` validates the official source identity, expected sections and the complete reviewed policy digest, then observes only the two corrected course-free notes. It never grants approval or emits an audit. Tests mutate the summer exception, session example and rejection discretion to require renewed review. The corrected model preserves the restrictive course-credit rule rather than treating absence of an enrollment prohibition as permission.

Validation: 48 focused policy/content tests passed, with isolated four-degree ingestion/repeat, ledger/integrity/foreign-key checks, 655 review exports and static build. No maintained database edits.

## Program requirements and general minima — 2026-10-11

The AI BS requirements table publishes nine credits of language study at the 200 level or higher and 121 total credits. The current [Arts and Sciences graduation requirements](https://bulletin.miami.edu/undergraduate-academic-programs/arts-sciences/) establish an at-least-three-credit language minimum, while the university establishes at least 120 total credits. A higher program requirement is compatible with these minima. The earlier mismatch was a false contradiction; the model retains the program’s nine-credit row and 121-credit total. Its illustrative sample plan cannot override the requirements table.

College language waivers remain conditional on the published placement, proficiency or educational-background criteria. These sources do not establish that any particular waiver removes every credit in this program’s higher nine-credit row; no individual exemption or replacement credit is invented. The BS/BA shared supplemental note now distinguishes a general minimum from program-specific higher requirements. Other version, proposed-program and optional-path questions remain separate.

The source-specific adapter requires both exact published amounts before emitting the corrected scope note. A changed amount, wrong program, or duplicate note requires review. The existing stable note ID is preserved, although its historical identifier contains `language-conflict`.

Validation: 53 focused policy, degree-table and cognate tests passed; isolated four-degree ingest/repeat changed 4 then 0 records, with ledger/integrity/foreign-key checks, 655 manual review exports and static build.

## Public enrollment and graduation scopes — 2026-10-11

The current course-information sections on academic credit, course numbering, CR/NC, enrollment, adds, confirmation, modality and repeats, and the complete graduation page were read. Seven additional conditional notes now preserve source-defined semester-credit terminology; 500 versus graduate-only course eligibility; permission versus completed enrollment; in-person program online limits; CR/NC timing and letter-grade conversion; processed declarations; optional dual-degree approval; and nonregistration-credit ceilings. These are seven notes because academic credit and level share one note, and declaration/dual-degree/nonregistration credit have separate notes.

The source permits ordinary faculty/department permission through a PIN or form but does not thereby promise prerequisite waivers. A declaration deadline means processed in CaneLink, not merely requested. The optional dual-degree pathway requires different awards/majors, normally at least 150 credits and final Dean of Undergraduate Education approval before first conferral. These conditional paths do not raise any single degree's published total. The 30-credit military-experience ceiling does not automatically contradict a narrower rule for transferred military schooling; neither is a credit grant. Earlier degreewide residence and college minima remain unchanged.

The complete current policy digests guard observations; a changed rule requires renewed interpretation. The manual audit remains in progress while course-content review continues. No private student record or individual permission is accessed or inferred, and no new named courses enter the graph.

Validation: 46 focused policy tests and isolated four-degree ingestion/repeat (4/0), integrity/foreign keys, 2,287 reviewed exports and static build passed.
