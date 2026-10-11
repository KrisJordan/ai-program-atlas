# UCSB GE export: bounded Comparative Literature content review

Reviewed 2026-10-11 for catalog 2026-2027. This contribution covers **62 C LIT rows and one C LITW row**, all 63 matching rows in the existing 856-row D/E/F/G CSV. It supplies metadata and manual taxonomy rationales for program-owner integration. It does not audit the full AI BS, establish requirement roles, add GE eligibility claims beyond the pool inventory, or emit identity groups.

Source: the official catalog's ordinary [course-search Export all results CSV](https://catalog.ucsb.edu/courses?generalSubjectAreas=D&generalSubjectAreas=E&generalSubjectAreas=F&generalSubjectAreas=G&page=1&cq=), registered as `ucsb-ai-bs-ge-defg-export`. The source is retained only in ignored `.cache/research/ucsb-course-content/ge-defg-export.csv`. Its URL, catalog edition, complete membership, and row digests are established by the existing pool manifest. Every complete description, advisor comment, repeat comment, prerequisite flag, and unit field in this scope was read. Committed descriptions are original summaries.

The primary researcher previously encountered an explicit human-verification challenge on catalog detail access and stopped. This reviewer made no network requests. The downloaded export contains **40 Yes and 23 No prerequisite flags**, without their corresponding rule text. All 63 prerequisites therefore remain null, with the actual flag and its limitations recorded per course. No flag establishes the absence of prerequisites. Additional detail-page conditions, exact prerequisite logic, and current offering details remain unverified.

## Manual subject decisions

The reviewed source-record counts are **61 human_context, one foundations, and one other/mixed**: 62 reviewed classifications, one mixed classification, and zero unclassified. These are bounded metadata counts, not degree requirements or student course loads.

**C LIT 152, Digital Humanities Practice, is foundations.** Its description explicitly introduces computer programming for humanities research beyond ready-made tools. Natural language processing, computer vision, and machine learning are named concepts within that introduction. The primary skill is introductory programming; neither the humanities setting nor the mention of AI methods overrides that stated focus.

**C LIT 27, Memory: Bridging the Humanities and Neurosciences, is mixed**, with candidate categories human_context and applications. It explores the convergence of neuroscience with literary, artistic, and philosophical questions about memory, morality, perception, identity, and agency. The description does not establish whether cultural interpretation or neuroscience domain knowledge dominates. The decision comes from the description, not its simultaneous Area C and E listings.

The other 61 rows support human_context through literary interpretation, critical theory, philosophy, cultural history, translation, political representation, or related social inquiry. Significant boundaries include:

- C LIT 155 introduces AI history and theory from the humanities. Its discussion of system construction serves critical, philosophical, and political analysis, supporting a primary human_context classification.
- C LIT 185 studies science and technology as questions in European philosophy. C LIT 179C examines media technology's effects on literature. C LIT 37 explicitly analyzes media forms as cultural texts even when a topic includes algorithms or digital humanities. None describes programming as the primary activity.
- C LIT 154 studies science fiction; C LIT 154I studies representations of economic concepts; C LIT 186FL studies vegetarianism through literature, philosophy, religion, and ethics. Their subject references do not establish technical science, quantitative economics, or nutrition instruction.
- C LIT 170 teaches literary translation as creative, cultural, and ethical work. Translation terminology and technologies support language communication rather than establish a computing subject.
- C LIT 100, 101, 181, 181C, 189, 190A/B, 31–34, 37, and 60 allow varying texts or topics but explicitly bound the inquiry to literary or cultural interpretation. An unspecified individual offering does not make those bounded subject classifications unknown.
- C LIT 175A's title specifies Armenian Literature, while its description permits a broader range of Eurasian literary regions. The note preserves this difference without assuming the actual offering's topic. Its literary and cultural subject remains established.

## Existing C LIT 155 overlap

The export **includes C LIT 155, Critical Artificial Intelligence**, at four quarter hours, with prerequisite flag No and the same humanities-centered framing as the existing `ucsb-c-lit-155` record. Its advisor comment identifies German 155, Comparative Literature 155, and ENGL 155AI as the same course. These details agree with the existing 2026-2027 source-reviewed course and `ucsb-critical-ai-155` group containing C LIT 155 and GER 155.

The primary researcher was notified of the overlap. The new manifest records an integration disposition to preserve the existing separately reviewed course-page provenance and identity group. This helper does not merge records, expand that group, infer ENGL 146AI equivalence, or edit the seed. The 63 reviewed rows therefore represent at most 62 additional stable course IDs relative to that pre-existing record, before any other integration or identity review.

## Credits, conditions, and versions

There are **47 four-quarter-hour rows and 16 five-quarter-hour rows**. Values come from the fixed-unit-value column; unused variable-field zeros and dashes are not substituted for credits or converted into ranges. Quarter-hour normalization follows the already verified institution calendar. No combined student load is computed.

Per-course notes preserve repeat conditions and exclusions:

- C LIT 113: repeat credit up to eight units requires department-chair consent.
- C LIT 139TX: repeat credit up to 16 units requires a different letter designation.
- C LIT 181, 181C, 186EE, 186FL, and 186G: repeat credit up to 12 units requires different letter designations.
- C LIT 181B: repeat credit requires different letter designations; no maximum is supplied in this row.
- C LIT 122A excludes credit after German 116A; 179B after German 169; 179C after German 180; 43A after German 41. C LIT 189 is not open after French 189.
- C LIT 106E's repeat field calls it and PORT 106E English versions and legal repeats of Portuguese 106. The same-course statement for PORT 106E is preserved separately; legal-repeat eligibility does not establish identity with Portuguese 106.

English instruction/readings are retained when explicit. C LIT 184C offers translated readings and Hebrew options with English lectures/discussions. C LIT 52 is taught in English and may have a Spanish discussion section depending on enrollment; the optional section is not guaranteed.

Other same-course statements are retained as notes, including statements located in repeat fields. The corresponding other-subject rows are outside this review. No alias group is inferred from a credit exclusion or similar title.

**C LITW 40 requires particular caution.** Its title and description match C LIT 40, but its advisor comment names EACS 41 and C LIT 40, not C LITW 40. The row therefore does not explicitly establish the online code's identity with either course. The C LITW record remains separate with that limitation recorded. A prefix and identical description alone do not justify an identity merge.

## Exact reviewed set

C LIT: 100, 101, 106, 106E, 107, 108, 113, 114, 122A, 126, 128A, 131B, 132, 133, 134, 139, 139TX, 152, 153B, 154, 154I, 155, 161, 170, 171, 175A, 179B, 179C, 181, 181B, 181C, 182, 184C, 184KA, 185, 186EE, 186FL, 186G, 187, 189, 190A, 190B, 191, 27, 30A, 30B, 30C, 31, 32, 33, 34, 35, 37, 40, 43A, 50, 50A, 50B, 50C, 52, 60, 82.

C LITW: 40.

Stable IDs are `ucsb-c-lit-<lowercase course number>` and `ucsb-c-litw-40`. URLs use the observed export source rather than guessed detail links.

## Replay and focused validation

`ucsb_ge_clit_reviews.parse_csv(data)` first invokes the full-export guard, then checks exact subject-scope membership, duplicate codes, and each complete source row's SHA-256. Any changed row field requires review before replay of the existing metadata. It returns only `id` and `courses`; category reviews stay in the manifest for manual integration. No curriculum audit, role inference, or identity group is emitted.

**21 focused tests passed**, including actual cached-export replay. Synthetic fixtures exercise changes to complete row fields, scope and duplicate failures, and mandatory full-export validation. Other checks protect manual totals, mixed candidates, null prerequisites, source restrictions, C LIT 155 overlap, and the online-code ambiguity. No full suite or build was run for this batch; integrated validation belongs to the primary researcher.
