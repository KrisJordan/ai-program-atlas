# Degree correctness audit — 2026-10-11

Immediate scope is every one of the 63 standalone degree records in the current inventory (25 institutions, including Furman). Additional majors and concentrations are separate. Inventory expansion is paused. This audit is independent of earlier requirement-completeness labels.

## Course taxonomy v1

Categories describe subject matter, never whether a course is an elective. Classify from an authoritative description/syllabus and its specific course identity/version, with a written rationale. A precise official title can support a limited classification when unequivocal; record that limitation. Do not assign from department prefixes, host degree, pool membership or broad title keywords alone.

- `foundations`: programming, data structures, algorithm design/analysis, general software construction and foundational computer-science methods. Mathematical logic/proof may instead be mathematics when that is the actual focus.
- `mathematics`: mathematical/statistical theory and methods, including calculus, linear algebra, probability and statistics; economics/business department membership does not establish this category.
- `ai_ml`: technical AI/ML methods and AI-focused subfields, evidenced by objectives or substantive topics such as search/reasoning algorithms, model construction/training, inference, learning algorithms or their analysis. An introductory course can qualify when it teaches these methods; advanced prerequisites or a high course number are not required. AI in a title, general explanations of how AI works, tool use or membership in an AI degree are insufficient.
- `systems`: architecture, operating systems, networks, databases, security and computing infrastructure when these are the actual focus.
- `human_context`: ethics, law, social/cultural/political analysis, communication and human implications of technology. Generic writing/language courses can fit this category with explicit rationale.
- `applications`: substantive domain knowledge or applied domain practice outside the other categories, including cross-disciplinary AI literacy, responsible practical use of AI tools and prompt workflows when those are the primary learning aims. Explain the domain/practice; do not infer an AI application merely from a degree association. A technical ML course using domain examples still belongs in AI/ML when learning those methods is the primary aim.
- `electives`: legacy label, not a subject category; newly reviewed courses use their actual subject or `other`.
- `other`: unknown, insufficient evidence, genuinely mixed content without a defensible primary subject, or content outside this taxonomy. Preserve mixed candidate categories explicitly; never split one course into fractional counts.

For every new review, identify the primary learning activity from the actual description, outcomes or syllabus. Distinguish learning AI methods from using existing AI systems. Ethics, governance or societal analysis as the primary activity belongs in `human_context`, even if tools are discussed. Where substantial method, application and human-context content has no evidenced primary focus, retain `other` with `status: mixed` and candidate categories. Missing evidence stays unclassified. Do not infer a precise technical depth, pedagogy or quality from a short catalog description.

Record the source identity/version, locator, date and rationale explaining the primary focus and any competing themes. Source changes require a new review; deterministic adapters only propose candidates and cannot issue or overwrite manual review judgments. Lexical searches are review triage, never automatic classification. Existing legacy AI/ML labels need source review before being called reviewed.

UNC DATA 117 is a worked example: the [2026–27 catalog](https://catalog.unc.edu/courses/data/) emphasizes cross-disciplinary understanding and responsible application. Its supported primary category is Applications; the catalog does not establish a technical-methods course or a measured depth assessment. Its ethics themes do not by themselves establish an ethics-primary course.

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

## Verified cross-listings

Keep all source code records. A program can add `course_identity_groups`, each with `id`, `relation: crosslisted`, `canonical_course_id`, `course_ids`, `source_ids`, `locator`, `reviewed_at` and `rationale`. Groups require at least two existing, nonoverlapping course IDs; the canonical record belongs to the group and supplies the subject classification. Registered authoritative evidence must establish the same course, preferably reciprocal course-description cross-list statements. A slash, similar title, credit exclusion, substitution, or ordinary OR choice does not establish identity. Different catalog versions are not merged by code alone.

The profile counts registered identities once, with fixed membership winning over options across aliases. It retains `source_record_count` per view and overall identity coverage. Unregistered records stay separate; counts therefore describe mapped identities, not a guarantee that all aliases have been resolved. Source-stated choice quantities never change and a one-item observed pool is not promoted automatically. An actual closed cross-listed required row needs its own source-reviewed requirement-role correction. Migration 012 preserves group membership and evidence relationally. Parsers can observe cross-list text but cannot certify an independent identity review.

Independent secondary ledgers use the `independent-*.json` filename prefix. They do not replace primary per-program audit entries or certify the full degree merely by verifying a bounded correction.

## Bounded source reviews and stale-evidence protection

`independent-core-*.json` files attach separate `fixed_requirements`, `choice_rules`
and `classification` judgments to the primary audit as `core_review`. Each judgment
has a status (`verified`, `partial`, `unverified`), a precise source scope, evidence
URLs/locators and explicit limitations. These statuses do not change the primary
whole-degree status or assert that every elective description was reread. A missing
readable saved source is an evidence limitation even when the existing graph has
consistent arithmetic. An unverified empty core never means no core is required.

Reviewers record source-enumerated course IDs and expected counts where established.
Null role sets or category totals remain unchecked, not zero. Named option subsets
do not certify full option pools. The compiler rejects duplicate review ownership,
unknown programs and malformed evidence. Export checks the exact reviewed identities,
recorded counts and a pinned digest of the resolved requirements, course facts,
identity groups and source editions. Thus changing a choice quantity or replacing a
course invalidates the review even when aggregate totals happen to remain equal.
The digest is a stale-evidence guard, never an automated source certification.

An exceptional closed rule can establish a fixed sequence by manual source review:
WPI's exact published “Three of DS 1010, DS 2010, DS 3010” names all three members
and a three-course minimum, with no fourth candidate or open-ended pool. Its adapter
requires that exact heading and complete code set before retaining the three fixed
identities. This does not permit the generic profile algorithm to promote observed
options merely because their count equals a selection quantity. Credit pools,
incomplete menus, example paths and ordinary alternatives remain choices.

## Separate bounded review dimensions

An optional per-program `core_review` records an independent, bounded source judgment with `reviewed_at`, `reviewer`, and `dimensions`. The three dimension keys are `fixed_requirements`, `choice_rules`, and `classification`. Each contains a `status` (`verified`, `partial`, or `unverified`), a scope `summary`, `evidence` entries with `url` and `locator`, and explicit `limitations`.

Degree pages label these dimensions **Fixed requirements**, **Choice rules**, and **Chart classification**. A verified dimension means verified within its stated source scope; it does not certify the whole degree or erase a policy blocker. Missing dimensions display **Not independently reviewed**. Explicit `unverified` judgments display **Not verified from available evidence**: a bounded source inspection may be complete without establishing the dimension. The original audit `status` and `second_pass_status` continue to describe the whole-degree review. Neither manual expected sets nor profile totals independently establish any review status. The UI preserves each dimension's date, reviewer, evidence and limitations without combining them into an overall score.
