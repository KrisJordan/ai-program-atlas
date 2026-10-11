# NJIT Business with AI BS

Reviewed 2026-10-10. Current 2026–27 catalog: https://catalog.njit.edu/undergraduate/management/management/business-with-ai-bs/

Partial: 32 named course rows from the 120-credit eight-semester plan, nine open GER/free-elective slots, and four linked GER directory policy notes. FYS SEM has an explicit zero-credit value. Plan rows are not inferred prerequisites or recurring offerings. Credit amounts are preserved but normalization remains unknown.

## Further source inspection

History/Humanities 200 and 300+, Scientific Literacy, and HSS Senior Seminar lists are accessible and registered. Their large approved pools are not fully extracted; wildcard categories and Rutgers options prevent a simplistic finite inventory. PHIL 310 appears in the advanced GER list and as a named degree course, so overlap policy needs review. HSS 404/407 are stated capstone options.

MGMT 416, MGMT 432 and DS 110 course-search URLs were robots-disallowed; no bypass attempted. Descriptions/prerequisites remain null. No public syllabi verified.

## Next checks

Complete GER pools and constraints; verify school/university GPA, grades, residency, transfer, double-counting and substitutions. Verify credit-unit definition independently. The department supplies curriculum/schedule PDFs, but these were not inspected in this pass. No launch date inferred.

## Adapter

Reads actual course rows, credits, suggested terms and generic requirement slots from the catalog plan. Rejects changed/missing identities, missing totals, unexpected rows and duplicate named courses. Does not emit reviewer audit or complete status.

## 2026-10-11 degree-wide review

The live robots-permitted 2026–2027 catalog GER pages now feed rerunnable
`atlas.adapters.njit_degree_policies` parsers registered with this adapter.
The four full named option pools contain 64 GER-200, 248 GER-300+, 36 natural
science and 2 HSS-seminar rows. Wildcard HIST/HUM/STS subject-level rules stay
textual eligibility rules; blank credits stay unknown. Existing named degree
courses retain their primary-plan source and credit values when also eligible
in a pool. In particular, PHIL 310 is one course, not two requirements satisfied.

The GER root supplies minima/progression (3 computing, 18 cultural, 6 quantitative
with probability/statistics, 7 science with laboratory experience, 3 social
science, freshman seminar). These contextual nodes and option-pool allocations
must not be added to the plan’s 120 credits. The academic-policies page supplies
the two 2.0 graduation GPA tests, 33-credit transfer-student upper-division NJIT
residency, C/equivalence/official-transcript transfer conditions, prior outside
study approval, summer limitations and NJIT HSS-capstone residence, four-attempt
limit, expiration review, and no degree credit for U grades. Material source
wording is guarded so a changed numeric rule fails instead of silently retaining
a stale interpretation.

The published R216 206 laboratory row says **3 credits**; retained without
correction. Exact eligible lecture/lab combinations and PHIL-310/GER overlap,
free-elective substitutions and any further MTSM degree-specific conditions
remain unresolved; **partial** is deliberate. School overview was inspected and
describes separate Business, FinTech and Business-with-AI degrees, with no
standalone graduation-policy section. Its accessible direct management course
entries can support a later metadata review despite robots-disallowed search
popups; this update does not claim those descriptions/prerequisites were mapped.
No raw HTML is committed and no blocked endpoint was bypassed.

## Science option follow-up — 2026-10-11

The ordinary robots-aware fetcher read the current catalog's [Physics](https://catalog.njit.edu/undergraduate/science-liberal-arts/physics/), [Chemistry and Environmental Science](https://catalog.njit.edu/undergraduate/science-liberal-arts/chemistry-environmental-science/) and [Biological Sciences](https://catalog.njit.edu/undergraduate/science-liberal-arts/biology/) course blocks. `njit_science_options.py` now reruns the extraction for 19 already-approved GER courses and nine conditional option notes. It reads titles, credits and explicit preparation clauses, validates the reviewed laboratory relationships, rejects missing/duplicate blocks and changed material relationships, and emits no audit or complete status.

CHEM 125A permits CHEM 125 **or** CHEM 121; CHEM 126A permits CHEM 126 **or** CHEM 122 after CHEM 125A at C or better. PHYS 102A/103A/111A require their corresponding lectures concurrently. PHYS 121A permits concurrent PHYS 121 or PHYS 122, but only 121 is in this reviewed GER pool: 122 is not silently added. PHYS 202A is an optional associated astronomy lab without an explicit concurrency rule; PHYS 203A is optional with 203 as a corequisite. BIOL 150 explicitly includes a laboratory. These are conditional eligibility observations, not nine extra required course groups or nine interchangeable four-credit choices. Explicit prerequisite/corequisite clauses are retained; absence remains null.

The remaining science question is narrowed to the Rutgers-listed options and R216 206's published three-credit lab amount. The inspected NJIT biology descriptions for Rutgers courses largely omit explanatory prerequisites; their course titles/contact hours do not justify inventing lecture/lab pairs. No Rutgers credit correction is made.

The school [course-planning page](https://management.njit.edu/course-planning), [petition page](https://management.njit.edu/petition) and [permits page](https://management.njit.edu/permits) were inspected. They direct individual planning to advisers/degree audit and do not publish a PHIL-310 double-use or free-elective substitution exception. DegreeWorks is explicitly described as requiring the student portal; no private audit was accessed. These pages' semester overload and administrative details are not presented as new graduation requirements.

Both PDF URLs were explicitly linked from the program page and returned HTTP 200 after normal robots checks: [school curriculum](https://management.njit.edu/sites/management/files/BS%20BusinesswithAI%20Curriculum%20.pdf) (three pages) and [course offering grid](https://management.njit.edu/sites/management/files/bsai-curriculum-studentgrid20262028%20.pdf) (two pages). The former repeats the 120-credit plan and does not supply the missing overlap/substitution rule. The latter includes tentative future offering annotations and a cancellation caveat; these are not a degree requirement, launch date or guaranteed recurring offering. PDFs remain uncommitted and are research provenance only, not falsely accepted as HTML parser inputs.

**Partial remains.** PHIL 310/GER reuse, free-elective substitution limits/additional school completion conditions, and unresolved Rutgers science relationships still require authoritative evidence. The full published 36-course GER option pool is already mapped; the remaining gap is not a missing entire pool. Course metadata is tracked separately.
