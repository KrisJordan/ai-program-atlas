# Degree correctness audit — 2026-10-11

Immediate scope is every one of the 63 standalone degree records in the current inventory (25 institutions, including Furman). Additional majors and concentrations are separate. Inventory expansion is paused. This audit is independent of earlier requirement-completeness labels.

## Course taxonomy v1

Categories describe subject matter, never whether a course is an elective. Classify from an authoritative description/syllabus and its specific course identity/version, with a written rationale. A precise official title can support a limited classification when unequivocal; record that limitation. Do not assign from department prefixes, host degree, pool membership or broad title keywords alone.

- `foundations`: programming, data structures, algorithm design/analysis, general software construction and foundational computer-science methods. Mathematical logic/proof may instead be mathematics when that is the actual focus.
- `mathematics`: mathematical/statistical theory and methods, including calculus, linear algebra, probability and statistics; economics/business department membership does not establish this category.
- `ai_ml`: explicit artificial intelligence or machine-learning methods and AI-focused subfields. A course in an AI degree is not automatically AI.
- `systems`: architecture, operating systems, networks, databases, security and computing infrastructure when these are the actual focus.
- `human_context`: ethics, law, social/cultural/political analysis, communication and human implications of technology. Generic writing/language courses can fit this category with explicit rationale.
- `applications`: substantive domain knowledge or applied domain practice outside the other categories. Explain the domain; do not infer an AI application merely from a degree association.
- `electives`: legacy label, not a subject category; newly reviewed courses use their actual subject or `other`.
- `other`: unknown, insufficient evidence, genuinely mixed content without a defensible primary subject, or content outside this taxonomy. Preserve mixed candidate categories explicitly; never split one course into fractional counts.

Course records may add `category_review`:

```json
{"status":"reviewed","taxonomy_version":"1","reviewed_at":"2026-10-11","source_ids":["registered-program-source"],"locator":"CSDS 233 description","rationale":"The description centers on representations, implementation and analysis of data structures.","candidate_categories":[]}
```

Statuses are `reviewed`, `mixed`, `unclassified`; mixed/unclassified records use `category: other`. A reviewed record must have a non-other, non-electives category. Missing review means legacy/unreviewed classification, never independently verified. Cite program-registered sources. Root owns validation, relational persistence and public profile review metadata. Agents own course facts and actual source interpretation. Parsers may extract observations, but never manufacture an independent review or attach stale reviews to changed descriptions.

## Per-program audit ledger

Each assigned JSON file in `research/degree-audit/` is an object with `audit_date`, `reviewer`, `programs` (array). Every program entry contains:

- `program_id`, `institution_id`, `status`: `audited` or `blocked` (while working `in_progress`). `audited` requires all checks below; a partial audit with inaccessible or conflicting authoritative evidence is `blocked`, with verified corrections retained. Accessible work that has not yet been reviewed stays `in_progress`; time or workload is not an access blocker.
- `sources`: objects `{url, catalog_year, locator, checked_at, access_status}`. Include degree/host rules and the actual course-description sources reviewed, including blocked URLs. Exact version/cohort ambiguity must remain explicit.
- `checks`: object of prose findings for `degree_identity`, `required_and_choices`, `elective_pools`, `prerequisites`, `credits_and_units`, `classification`, `family_composition`, `degree_wide_requirements`.
- `expected_profile`: `{required:{count,categories}, options:{count,categories}, unresolved:{count,categories}}` for the independently reviewed current graph, or null if not independently established. Record manual expected course-ID sets in `expected_course_ids` with keys `required`, `options`, `unresolved`, or explain a large reproducible reviewed set in Markdown. Calling the profile function alone is not independent validation.
- `discrepancies`: array of `{issue, correction, status, evidence_urls}`; `blockers`: array of specific evidence gaps with exact URLs; `correction_status`; `second_pass_status` initially `pending`.

Adjacent Markdown explains source interpretation and manual aggregate calculation, not just test output. Keep copyrighted raw documents ignored. Each university degree must be reread or individually blocked. Checking a fetch or parser is not an audit. Preserve exact credit systems and role distinctions; prerequisites are not automatically additional degree obligations, overlapping choices are not extra courses, and complete local requirements do not certify the whole degree.

Independent second pass checks evidence, course identities, mixed/unknown semantics, cross-institution classification consistency, family resolution and displayed aggregate values. Publication may deliver verified corrections before all 63 audits finish, but must expose actual audit progress and remaining blockers.
