# Yeshiva College AI concentration: finite course metadata review

Observed 2026-10-11. The [current concentration catalog](https://yu.smartcatalogiq.com/en/current/university-catalog/undergraduate-programs/yeshiva-college/copy-of-computer-science-artificial-intelligence-bs) supplies exactly 22 required course links. Every link was fetched through the ordinary robots-aware client; all returned HTTP 200 and exact code/title/credit matches. The [machine-readable ledger](yeshiva-course-metadata-2026-10-11.json) records all 22 outcomes and source URLs. No course page remains unattempted or access-blocked in this queue.

The seed now contains **22 original description summaries and 21 source-stated prerequisite/corequisite strings**. COM 1300 has no prerequisite statement on its current page, so its field remains null. Specific conditions remain intact: COM 3640 permits COM 2545 before or alongside it; COM 3800 separately names COM 3820 as a corequisite; COM 4010 permits COM 3800 before or alongside it; and COM 4020 allows the published COM 4010/COM 3810 alternative. These are course requirements, not new routes that replace the AI concentration table. MAT 1412 retains the stated pre-semester placement test. No generic “no prerequisites” values are fabricated.

The metadata parser verifies the exact scoped code/title. Original summaries are returned only when the course narrative matches its reviewed hash. Credit and requisite text are read from the live input, so changed values become candidates; new narrative or unsupported separately structured constraints fail for review. It does not read seed files or auto-certify completeness.

## Credit units

The [current catalog credit-hour policy](https://yu.smartcatalogiq.com/en/current/university-catalog/university-policies/undergraduate-policies/credit-hour-policy) links [Provost Academic Policies](https://www.yu.edu/provost/policies), which currently links the [November 1, 2018 university Credit Hour Policy PDF](https://www.yu.edu/sites/default/files/inline-files/Credit%20Hour%20Policy.pdf). The document's date is retained. PDF pages 1, 3 and 4 were rendered and visually inspected: the policy adopts NYSED's semester-hour measure across university courses, requires proportional equivalence for other formats and supplies fifteen-week credit guidance. This is the institutional basis for normalizing the unchanged course-table amounts and 75-credit total as **semester credits**. No conversion from lecture contact hours or assumption based on an academic calendar was used.

The individual course sources identify descriptions, requisites and numerical amounts. The separate registered PDF source supports unit normalization. Raw HTML parsers leave units unknown because the course pages alone do not name them; a separately reviewed PDF-text parser guards the policy evidence before a curated normalization step. Successful HTML refresh is not represented as refreshed PDF verification.

## Remaining boundaries

- The Spring 2026 department guide's 74-credit summary still conflicts with its detailed 75-credit plan and the current catalog's 75-credit table. No amount or required course was changed to reconcile it.
- COM 1300's prerequisites are unstated on its reviewed page. Individual transfer/substitution/summer/residency decisions still require institutional approval under the mapped policies.
- A separate AI concentration declaration/recognition process remains unestablished in reviewed public sources. The complete host BS is outside this concentration inventory.
- Term-specific public teaching sites/syllabi, launch date and assessed program outcomes were not part of this bounded course/policy-link pass. They are not described as unavailable.

The record remains **partial**, with the same 22 required courses and 13 requirement/policy nodes. The metadata review changes no eligibility rules or program identity.

## Verification

145 focused tests passed, including synthetic changed credits, changed prerequisites/corequisites, altered descriptions, wrong course identity, navigation-only content and new constraint blocks. Optional replay matched all 22 captured official pages to curated metadata and rejected a changed credit-policy PDF extraction. An isolated database exported the enriched record, produced 33 candidates through ordinary scrape orchestration, and produced zero new candidates on repetition. Repeated seed ingestion made zero changes; SQLite integrity/foreign keys and a temporary static build passed. Raw captures and rendered PDF pages remain ignored; no maintained DB, shared code, PLAN or site files were changed.
