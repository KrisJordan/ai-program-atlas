# UCSB GE export: bounded Religious Studies content review

Reviewed 2026-10-11 for catalog 2026-2027. This contribution covers **all 67 rows whose exact Subject & Prefix is RG ST** in the existing 856-row D/E/F/G CSV. It supplies source-reviewed metadata for manual program-owner integration. It does not certify the full AI BS, assign required/option roles, add GE eligibility claims beyond the existing pool inventory, or establish cross-listed identities.

The source is the official catalog's ordinary [course-search Export all results CSV](https://catalog.ucsb.edu/courses?generalSubjectAreas=D&generalSubjectAreas=E&generalSubjectAreas=F&generalSubjectAreas=G&page=1&cq=), registered as `ucsb-ai-bs-ge-defg-export`. The ignored source is `.cache/research/ucsb-course-content/ge-defg-export.csv`. The existing pool manifest establishes the source URL, 2026-2027 edition, complete inventory, and row digests. Every complete RG ST description, advisor comment, repeat comment, prerequisite flag, and unit field was read. Descriptions in this contribution are original summaries.

The primary researcher previously encountered an explicit human-verification challenge on catalog detail access and stopped. This reviewer made no network requests and used only the already downloaded ordinary UI export. The export has **37 Yes and 30 No prerequisite flags**, without the corresponding rules. All 67 prerequisite values remain null. Each course note preserves its flag without claiming that a No flag establishes absence. Detail-page conditions, exact prerequisite logic, and current section availability remain unverified.

## Manual subject decisions

All **67 classifications are reviewed human_context**, with **zero mixed and zero unclassified**. Each manifest entry contains its own taxonomy-v1 rationale grounded in its description. This is a subject-content count for a bounded source set, not a count of courses a student must complete.

The descriptions specify historical, philosophical, ethical, literary, political, sociological, linguistic, or cultural analysis. None identifies technical computing or clinical instruction as its primary activity. Boundary decisions follow the complete descriptions:

- RG ST 147 varies by offering but explicitly limits the subject to a topic in U.S. religious history studied in cultural context. Its unspecified individual topic does not make the bounded subject classification unknown.
- RG ST 157CP, 157G, 157I, and 157PP teach Persian reading, translation, communication, and interpretation through literature or media. These language and cultural activities support human_context rather than an unrelated domain-practice category.
- RG ST 152VR studies religious uses of technology. Possible virtual-reality delivery is a conditional teaching format, not evidence of systems or programming instruction.
- RG ST 193B compares worldviews that shape healing traditions; it does not describe clinical treatment training. RG ST 14 likewise studies Native religious and philosophical concepts, including medicine, rather than clinical practice.
- RG ST 185 studies food through cultural identity, religion, history, and social resilience; it does not describe culinary training or nutrition science. RG ST 150WR studies wrestling as ritual and popular culture rather than teaching athletic performance.
- RG ST 128 and 48 address environmental questions through religious thought and ethics. RG ST 80C treats modern science as a historical challenge to religion. These subjects do not establish technical environmental or scientific-methods instruction.

No category was inferred from the RG ST prefix, GE designation, or association with an AI program.

## Units, restrictions, and source inconsistencies

There are **29 five-quarter-hour records and 38 four-quarter-hour records**. Each amount comes from the fixed-unit-value field. The secondary fixed field is a dash, and unused variable fields contain zero or dash placeholders; these are not credit amounts or variable ranges. Quarter-hour normalization follows the already verified UCSB calendar. No total student credit load is calculated.

The notes preserve these course-specific conditions:

- RG ST 147 may repeat for a maximum of eight units; RG ST 153 states no repeats.
- RG ST 19 excludes credit after Religious Studies 158A. RG ST 20's repeat-comment field excludes credit after Religious Studies 162E. RG ST 179B excludes credit after German 169. These conditions are not identity equivalences or complete prerequisite statements.
- RG ST 157CP targets intermediate or advanced Persian proficiency; RG ST 157PP targets advanced proficiency. The description's proficiency audience does not supply exact enrollment logic.
- RG ST 133E lectures and discussions are in English; translated and Hebrew readings are available. RG ST 179B is taught in English. RG ST 175B and 73 use texts in English translation.
- RG ST 152VR may use virtual reality partly or entirely in some versions. No particular delivery format is guaranteed.

**RG ST 4 contains an inconsistent advisor comment:** it names Religious Studies 5 and East Asian Cultural Studies 5 as the same course even though the row itself is RG ST 4, Introduction to Buddhism. The note explicitly preserves this discrepancy. Its clear description supports the content classification, but the comment cannot establish an RG ST 4 alias or justify changing its code. This contribution does not silently repair the source.

Seventeen other advisor comments identify matching courses in other subjects. They are preserved in per-course notes: RG ST 123 / Asian American Studies 161; 133E / Comparative Literature 184C; 147T / EACS 147T; 167A / Japan 167A; 175B / JAPAN 175B; 176 / EACS 176; 179 / EACS 179; 179B / Comparative Literature 179B and German 179B; 183B / Chinese 183B; 21 / EACS 21; 28 / History 28; 3 / EACS 3; 32 / Chinese 32; 37 / ENGL 37; 48 / Chinese 48; 71 / AS AM 71; 73 / Japan 73. Other subjects are outside this review. No identity group or merged record is emitted.

## Exact reviewed set

RG ST: 1, 101, 110, 111B, 114, 115A, 115G, 116A, 12, 123, 124G, 128, 129, 13, 131H, 133C, 133E, 14, 140B, 141A, 144, 144A, 147, 147T, 149H, 150WR, 152, 152VR, 153, 157CP, 157G, 157I, 157PP, 166, 167A, 175B, 176, 179, 179B, 18, 183B, 185, 19, 193B, 20, 21, 28, 29, 3, 30, 31, 32, 35, 37, 4, 48, 5, 6, 61, 62, 66, 7, 71, 73, 80A, 80B, 80C.

Stable IDs are `ucsb-rg-st-<lowercase course number>`. URLs remain the observed export source URL; no detail URL is guessed.

## Replay and validation

`ucsb_ge_rgst_reviews.parse_csv(data)` invokes the existing full-export guard, validates the exact RG ST scope, rejects duplicate codes, and checks the SHA-256 of every complete row against the review manifest. Any row change requires review before existing metadata can be replayed. The helper emits only `id` and `courses`, never a category review, curriculum audit, requirement, or identity group. Manual `category_review` objects remain solely in the manifest for owner integration.

**21 focused tests passed**, including replay of the actual ignored export. Synthetic fixtures test changed descriptions, names, advisor/repeat comments, all unit fields, prerequisite flags, GE/university fields, changed subject, missing/new/duplicate rows, and mandatory full-export validation. Additional checks protect manual totals, null prerequisites, repeat/credit restrictions, the RG ST 4 discrepancy, and content-specific boundary decisions. Only this batch's tests were run; integrated build and release validation belong to the primary researcher. No full-degree conclusion follows from these checks.
