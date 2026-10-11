# Maryland AI curriculum research

Reviewed 2026-10-10. Official catalog fetched through the robots-aware fetcher; raw HTML remains outside the repository. Parser validates title and table inventory, extracts actual rows, nested choices and approval footnotes, and emits only partial observations. It never refreshes the curated audit or launch evidence.

Six-course specialization pools preserve the extra GVPT170 requirement and course-content approval footnotes.

University-wide graduation/general education and linked college requirements remain unreviewed.

Launch evidence: https://today.umd.edu/umd-to-launch-2-bachelors-degrees-to-explore-technical-human-dimensions-of-ai

Catalog: https://academiccatalog.umd.edu/undergraduate/colleges-schools/arts-humanities/philosophy/human-centered-artificial-intelligence-major/

## University/college closure and selected metadata — 2026-10-11

Before the public-viewer review below, the BA had **70 course observations, 69 requirement nodes and five explicitly classified learning outcomes**. University sources add minimum degree/residence/upper-level hours, major enrollment and GPA, General Education area counts and choices, lab/outside-major requirements, Big Question overlay, diversity alternatives, the 40-credit minimum, transfer acceptance versus applicability, transfer caps and levels, degree applications, incompletes, Pass-Fail and repeat rules. Approved term designation is a criterion, not an invented finite General Education pool.

ARHU sources add 39 upper-level credits, conditional first-year ARHU158, major grade/residence conditions, advising milestones and Global Engagement. Its proficiency option and three alternative routes are a choice tree, not cumulative requirements. The explicit MATH115 requirement is now a course observation; its official course block supplies name, credits, description and prerequisites. Official INST blocks add three more metadata observations. Five catalog program learning outcomes are short paraphrases, not career claims.

The [Global Engagement page](https://arhu.umd.edu/academics/advising/global-engagement/) links a [language-sequence PDF viewer](https://drive.google.com/file/d/1Lk076FdbP8aXNku8kzuKZkkMnQeEZGkI/view?usp=sharing). The public viewer loaded, but its exact embedded `drive.usercontent.google.com/uc` download URL was disallowed by robots. Retrieval stopped; no alternate download or preview path was tried. Exact approved language sequences remain a concrete access gap. The examples on the college page are not promoted to a complete sequence inventory.

Selected metadata: **two descriptions and four prerequisite/restriction statements**. The current INST listing has no blocks for listed INST430/431/432/433/436; metadata stays unknown without an inference of program withdrawal. Course enrollment restrictions and prerequisites remain visible, with no invented AI exception. Public course sites/syllabi and most other course metadata remain unknown. The record remains **partial** because of the sequence source barrier and unresolved applicability of restrictions to some listed options.

## Ordinary public language viewer review — 2026-10-11

The prior sequence access gap is **partly resolved through the permitted public viewer**, not through the blocked download. Chrome's ordinary Google Drive viewer exposed readable page text and the rendered two-page document without a sign-in requirement. Page 1's heading/date, sequence rows, bold-underlined terminal courses, and placement/grading/ASL notes were inspected visually. Page 2 reiterates the three routes already mapped. No download, print, alternate preview, hidden app state or download-endpoint request was used. The existing `drive.usercontent.google.com/uc` robots denial remains in force.

The document is explicitly **September 2023**, although still linked by the current college page. Added **24 dated placement-dependent path notes and two context/condition notes**, with **51 concrete course codes and published credit amounts**. The BA now has **121 course observations and 95 requirement nodes**. These are alternative progression references, not 51 new universally required courses. Courses are codes-only with unknown names, descriptions and catalog prerequisites. Arrows do not become prerequisite metadata. Credit units use the already verified Maryland semester system; no path totals are invented.

The Chinese non-heritage path requires **CHIN102 and CHIN103** at its terminal, not either one; the KORA211/212 path is heritage-only. Both alternative Russian paths end at RUSS102. Historical Arabic104/105 renumbering is excluded from current course observations. FOLA138_/139_/148_/149_ and158_/159_ retain their literal suffix placeholders in notes, without fabricated concrete course identities. ASL has a qualified advising/availability rule but no verified fixed pool in this reference. Asterisked languages require online placement; other languages call for department consultation. Existing proficiency and non-language alternatives remain intact.

### Exact remaining applicability gaps

- **Source conflict:** the September2023 PDF says the final sequence course must be letter-graded with minimum D-. Both the current ARHU catalog and current Global Engagement page say all sequence courses may use Pass-Fail, subject to eligibility, major/minor and GenEd exclusions. Neither statement is silently chosen as the operative rule for the 2026–2027 degree. College clarification or a current replacement reference is needed.
- **Scope:** the current policy permits a designated level of one language **or one level of two different languages**. The dated PDF lists one-language paths only; its examples do not certify every current two-language combination, language-level definition, suffix-specific offering or ASL path. The current page itself directs students to ARHU advising for required sequences.
- Previously documented applicability of selected restricted major courses remains unresolved. Course metadata/outcomes/launch gaps remain separate from these requirement gaps. Status stays **partial**.

`maryland_language_sequences.parse` is rerunnable against a reviewer-captured **visible page-one text** with row line breaks (plain text or AX `text` lines). It validates the edition, conditions, complete subject/path inventory, code order, conjunctions, heritage/placement labels and the visually reviewed terminal identities; it extracts credit amounts. A raw Drive HTML shell without rendered text fails closed. It makes no network requests, returns no audit/freshness/completeness, and does not imply unattended PDF retrieval works. The ignored local visible-text capture is `var/maryland-visible-language.txt`; synthetic changed-policy/credit/identity/heritage fixtures are committed. Raw source pages/PDFs are not committed.

Validation: `uv run pytest -q tests/test_maryland_language_sequences.py tests/test_maryland_degree_policies.py` — **36 passed** (including available policy-source cache replays). An isolated one-program CLI ingest, SQLite/tree check and static build passed under `var/maryland-viewer-check/`; the maintained database was not changed.

### Degree correctness review — 2026-10-11

The requirements introduction explicitly permits an internship in place of the capstone seminar. HCAI490 is therefore a named option, not universally fixed. The alternative has an uncoded internship note; no course or credit amount is invented. Current mapped roles become 9 fixed / 59 named options; MATH115 and college-language contextual records retain their unresolved roles pending applicability review.

This is a bounded requirement-role correction. Whole-degree correctness remains
in progress; existing partial curriculum status and substantive source questions
are preserved. Synthetic tests distinguish explicit choices from context, and
current cached catalog replay agrees with the reviewed seed roles.
