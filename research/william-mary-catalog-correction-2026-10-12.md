# William & Mary current catalog correction

The [2026–2027 Applied Artificial Intelligence BA catalog](https://catalog.wm.edu/programs/applied-artificial-intelligence-ba-interdisciplinary-studies-cdsp/index.html#requirementstext) was read through ordinary Chrome on October 12. Its REQUIREMENTS tab establishes the major table below. The previous adapter had no catalog source/parser: it treated the undated department FAQ's three-course residency subset as the displayed fixed set. This is a data/extraction defect, not a requirement-renderer defect.

| Catalog table row | Correct representation | Previous discrepancy |
| --- | --- | --- |
| AAI 101, Reasoning with GenAI, 3 hours | Fixed | Missing |
| AAI 301, Designing AI Agents, 3 | Fixed, distinct from DATA 305 | FAQ DATA 305 incorrectly occupied fixed set |
| DATA 201, Data in the Age of AI, 3 | Fixed; retain independently reviewed PATH description | Present |
| DATA 202, AI & Data Ethics, 3 **or** PHIL 150, Philosophy of Technology, 4 | Choose one; preserve unequal course credits | DATA 202 fixed; PHIL 150 missing |
| DATA 210, Research Design and Statistics, 3 | Fixed | Missing; example pathway methods were not authoritative |
| DATA 303, Data Visualization, 3 | Fixed | Missing |
| DATA 405, Trustworthy AI, 3 | Fixed | Missing |
| Capstone: AAI 302, Agentic Coordination, 3 | Fixed capstone | Missing coded capstone |
| Applied AI attribute courses or advisor-approved courses in other disciplines, six credits | Open choose-credits rule; no invented finite pool or two-course count | Missing |
| Major total 30; degree minimum 120 | Separate major total and degree-context minimum | Department 30-credit total present; major table missing |

Manual mapped sets: seven fixed identities (AAI101/301/302, DATA201/210/303/405), two option identities (DATA202/PHIL150), one contextual identity (DATA305). Before: three fixed, zero options/context. After: seven fixed, two options, one context. No concentration or prerequisite branch appears on this requirements page. PATH section prerequisites remain course metadata; they do not create degree requirements.

Seven fixed courses × 3 hours + DATA 202 (3) + electives (6) = 30. Choosing PHIL 150 (4) yields 31. Preserve the source's published 30 and PHIL 150’s four credits without inventing a credit waiver or adjusting the elective minimum. The undated FAQ still names DATA305 and treats DATA202 as core for residency; the dated governing catalog membership is separately represented. No AAI301/DATA305 cross-list, equivalence or effective rename is inferred. The catalog edition is 2026–2027; prior cohorts and individual matriculation/declaration catalog applicability remain separate.

Existing Fall 2026 PATH subject reviews survive for DATA201 (AI), DATA202 (human context), DATA305 (AI), with exact original sources. Seven new catalog-only course records remain explicitly unclassified pending actual descriptions. Thus fixed subjects currently comprise one reviewed AI and six unclassified; options comprise one reviewed human-context and one unclassified; context contains one reviewed AI. Neither titles nor a corrected membership graph certify technical depth. Independent review of this new primary correction remains pending; all bounded dimensions stay partial and the whole-degree review remains blocked.

The new source-specific observer parses semantic course-table rows, inline OR, section headings, credits, open approval text and publication totals; it rejects changed editions, missing scope and unsupported syntax. It emits candidates only, never completeness/review state. Synthetic fixtures are reductions of the actual rendered semantic table, not stored raw website copies. The regular robots-aware Fetcher still stops at robots HTTP 202 before requesting catalog content. Ordinary browser reading succeeded without a challenge; no denial was bypassed. A raw-HTML save was interrupted by user changes to the shared native Chrome surface, so native UI actions stopped. Live HTML structural verification is still needed when a permitted saved page or fetch becomes available; synthetic extraction checks do not establish it.

Previous resolution proposals retain their dated facts and are explicitly superseded, rather than being rewritten as if they had inspected this catalog. Current primary/core ledgers and the maintained database pin this correction. Full BA residence/time-limit/degree policy review, new course descriptions, the PHIL150 total qualification and cross-version code applicability remain outside this bounded table correction. No publication is authorized in this task.

Validation before API integration: 97 focused tests pass (25 optional private-capture skips); full required suite passes 3,833 tests including all 93 Chromium cases, with 1,026 optional cache/historical skips. Fresh and maintained W&M exports agree; repeat ingestion changes zero programs; integrity/foreign keys pass; repeated static builds are byte-identical. Static program QA checks all ten actual course anchors, the ethics OR, open six-credit elective rule, credit-total qualification and nested base-path links. Browser launch needed ordinary sandbox escalation; the approved gate passes. These software checks do not certify the remaining source facts or live raw-HTML extraction.
