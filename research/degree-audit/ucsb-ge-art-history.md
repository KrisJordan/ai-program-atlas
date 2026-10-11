# UCSB GE export: bounded Art History content review

Reviewed 2026-10-11, catalog 2026-2027. This contribution reviews **57 complete CSV rows: 54 ARTHI and three ARTHIW**. It supplies course metadata for the program owner's integration. It does not audit the complete UCSB AI BS, establish required/option roles, establish GE eligibility beyond the existing pool inventory, or certify identity groups.

The official source is the catalog's ordinary [course-search Export all results CSV](https://catalog.ucsb.edu/courses?generalSubjectAreas=D&generalSubjectAreas=E&generalSubjectAreas=F&generalSubjectAreas=G&page=1&cq=), with areas D/E/F/G selected. The downloaded 856-row file is retained only in ignored `.cache/research/ucsb-course-content/ge-defg-export.csv`. The existing `ucsb_ge_catalog_pools` manifest establishes this export's catalog edition, complete membership, and full-row digests. Source ID: `ucsb-ai-bs-ge-defg-export`. No guessed course-detail URLs are used.

The primary researcher encountered an explicit human-verification challenge on catalog detail access and stopped. This reviewer made no network requests to that catalog and reviewed only the already obtained ordinary UI export. Exact prerequisite rules and additional detail-page conditions remain unavailable. The exported prerequisite column has **40 Yes and 17 No flags**, with no rule text. Every emitted prerequisite is therefore null, including the No rows. Notes report the actual flag without treating it as an absence claim.

## Content decisions and manual totals

Every complete description, fixed/variable unit field, advisor comment, and repeat comment was read. Original summaries and individual taxonomy-v1 rationales are recorded in the manifest. Categories follow the subject described, not the ARTHI prefix, GE area, or AI program association.

- **55 human_context, reviewed:** historical or critical interpretation of art, architecture, museums, urbanism, cultural exchange, and representation.
- **1 applications, reviewed:** ARTHI 136W explicitly teaches manual architectural visualization through sketching, projections, perspective, and rendering. This is architectural practice; it does not imply programming or AI.
- **1 other, mixed:** ARTHI 5B explicitly combines museum history, theory, and practice without enough detail to establish a dominant subject. Candidate categories are human_context and applications.
- **0 unclassified.** Thus 56 reviewed + one mixed = 57 reviewed source records; this is not a degree-course total.

Several boundary cases require content-specific interpretation. ARTHI 109C treats science and technology as influences on Renaissance art. ARTHI 136O studies the history, theory, and aesthetics of sustainable architecture rather than technical environmental design methods. ARTHI 141G considers display design within museum architectural history and cultural debate. ARTHI 187D includes curatorial practice but foregrounds representation, institutional power, inclusion, and public participation. Each has a defensible human_context primary subject. ARTHIW 6R uses a game as a teaching medium for Roman heritage, repatriation, and research writing; it does not teach game implementation.

There are **17 five-quarter-hour rows and 40 four-quarter-hour rows**. Each amount comes from the fixed-unit-value column. The unused variable-unit fields contain zero or dash placeholders, which are not substituted for the fixed amount. Quarter-hour normalization follows the already verified institution calendar. No aggregate student load is calculated.

## Eligibility and identity qualifications

ARTHI 113B preserves the restriction against students who completed Art History 113A. ARTHI 144C preserves credit exclusion for Russian 144C or Slavic 144C and its English instruction note. ARTHI 107B may be taken separately from 107A, while ARTHI 127B is described as a continuation of 127A; neither statement supplies an exact prerequisite rule.

The export explicitly associates ARTHI 6H with LAIS 6H, 134D with CHIN 134D, 134F/134G/134H with Japan courses of the same numbers, 136O with ENV S 136O, 136W with Art Studio 106W, and 144C with Slavic 130C. ARTHIW 6R is identified with WRIT W 6R. The other subjects are outside this review. These statements are retained as notes, not emitted as identity groups.

ARTHIW 6C is identified as the online version of ARTHI 6C; ARTHIW 6F is identified as the online version and same course as ARTHI 6F. Both records in each pair remain separate. ARTHIW 6F's repeat field describes fall-or-spring offerings; the note preserves that qualification without asserting a current section schedule. No other repeat-credit rule is inferred from dash placeholders.

## Exact reviewed set

ARTHI: 5A, 5B, 6B, 6C, 6DS, 6E, 6F, 6G, 6H, 6I, 6J, 6K, 6L, 6M, 105C, 107A, 107B, 109B, 109C, 111B, 113B, 113F, 115E, 117F, 119B, 119G, 121B, 121D, 121F, 121G, 123E, 127A, 127B, 130D, 132A, 132I, 134C, 134D, 134E, 134F, 134G, 134H, 136B, 136C, 136I, 136K, 136M, 136O, 136W, 136Y, 141D, 141G, 144C, 187D.

ARTHIW: 6C, 6F, 6R.

Stable IDs are `ucsb-arthi-<lowercase number>` and `ucsb-arthiw-<lowercase number>`.

## Refresh and verification

`parse_csv(data)` first invokes the existing full-export guard, then verifies exact subject-scope membership, rejects duplicates, and checks each complete row's SHA-256 against this review's manifest. A change to any field, including an enrollment comment, unit value, flag, or GE designation, requires review before old metadata can be replayed. The helper returns only `id` and `courses`, with no category review, curriculum audit, identity group, or requirement-role inference. Manual category reviews remain in JSON for the program owner.

Fourteen focused tests pass using synthetic rows and the optional actual cached export. Tests exercise changed source fields, missing/new/duplicate rows, mandatory full-export validation, immutable returned notes, review counts, units, and null prerequisites. `uv` was unavailable on the execution PATH, so focused checks used `python -m pytest`. Integration, whole-degree validation, and publication remain with the coordinator.
