# Lewis & Clark Artificial Intelligence minor

Reviewed 2026-10-11. The current official directory, program page and 2026–27 catalog explicitly identify an undergraduate AI minor. The catalog and program minoring page agree on the finite curriculum: three required courses, one of eight mathematical courses, the single published advanced/applied option, and one of three social-context courses; minimum 24 credits and 12 discrete credits.

The reviewer marks the **minor inventory complete** after also reading the College of Arts and Sciences policies for residence, exclusive credits, GPA, declaration/certification, two-minor limit, credit shortages, grading and transfer approval. This does not certify the parent BA. Transfer application remains conditional on registrar eligibility and chair/program-director approval; that documented decision route is mapped, not assumed satisfied. General CR/NC policy is preserved without inventing a minor-specific prohibition.

15 course identities, 13 requirement nodes, 6 sources and one source-stated program aim. Five CS course blocks provide concise original descriptions, prerequisites and four semester credits each. The other ten course options retain null metadata. First-offered date stays null: “new” without a date is insufficient. Alumni career statements on the overview describe broader college/CS alumni, not AI-minor outcomes, and were not imported.

`parse` is bounded between the AI-minor heading and the next minor heading; it rejects changed credit totals, option cardinalities and group wording. It does not return the review audit or verification timestamp. `parse_course_metadata`, `parse_minor_policy`, `parse_grading_policy` and `parse_transfer_policy` independently observe successfully read sources. Primary catalog parse is the normal scraper candidate; policy/metadata helper results need reviewer integration. Successful robots-aware fetches on 2026-10-11 supplied the timestamps in the seed. Raw HTML remains in ignored cache and `/tmp`, never committed.

Validation: synthetic source-shape tests cover adjacent-program contamination, changed pool/total rejection, changed prerequisite extraction and wrong policy scope. Reviewed seed passes schema validation and isolated ingest/build.

## Evidence quality review — 2026-10-11, batch 2

All ten non-CS options now have concise catalog descriptions, prerequisites and explicit semester-credit amounts from the Economics, Mathematics, Psychology, Philosophy and Communication catalogs. Source-stated None prerequisites are recorded only where explicit; class-standing restrictions remain attached. ECON 303 prerequisite punctuation is retained without imposing an invented logical grouping. All fifteen named courses have descriptions, prerequisites and credits; public course sites/syllabi and a first-offered date remain unverified. The overview calls the minor new without dating its first offering.

Source-specific parsers in `small_complete_metadata_batch2.py` validate the reviewed descriptions and extract labeled metadata. Fetches preserve actual cache timestamps. They emit observations only, never an audit or complete status. See the dated batch-2 research ledger for exact residual missingness.
