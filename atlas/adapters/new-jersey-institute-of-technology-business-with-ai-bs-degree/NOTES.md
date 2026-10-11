# NJIT Business with AI BS

Reviewed 2026-10-10. Current 2026–27 catalog: https://catalog.njit.edu/undergraduate/management/management/business-with-ai-bs/

Partial: 32 named course rows from the 120-credit eight-semester plan, nine open GER/free-elective slots, and four linked GER directory policy notes. FYS SEM has an explicit zero-credit value. Plan rows are not inferred prerequisites or recurring offerings. Credit amounts are preserved; a later explicit university policy review below establishes semester-hour normalization.

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

### Degree correctness review — 2026-10-11: units and GER roles

The Faculty Senate's publicly posted Definition of Course Credit by Hours
explicitly defines semester credit hours and applies that unit across NJIT's
schools and colleges. Its publication date is unstated; the date in the cited
New Jersey regulation is not a university policy effective date. This supports
semester_hours normalization without deriving units from the semester calendar.
The PDF was independently read; it is manually registered evidence, not a
fabricated HTML parser observation.

The four finite GER inventories are credit-choice pools (3, 6, 7 and 3 hours),
not merely contextual notes. All original course records and open wildcard
criteria remain. Source-proven individual laboratory relationships remain
conditional; no arbitrary lecture/lab combination is authorized. PHIL310 is
already fixed and its additional GER eligibility does not add a second course
or establish permission to fill two allocations with it. The mapped profile is
32 fixed and 349 named options, not a student load. Whole-degree correctness and
individual course-subject review remain in progress.


### Fixed-course description review — 2026-10-11

Read 31 of 32 fixed-course descriptions through ordinary public department catalog
sections: management 22, computing 2, information systems 2, humanities 4 and math 1.
The search-popup denials remain untouched; these are independently published
catalog chapters. New parsers require the exact reviewed course block and never
emit category-review or audit certification. Twenty-four subjects are primary
and seven mixed; FYS SEM remains unknown/unreviewed with its published zero
credits. The plan parser no longer assigns subjects from prefixes or keywords.

MGMT116/216 and OM375 primarily teach statistical/optimization/decision methods;
MIS385 teaches database systems; FIN410, MGMT435, IS392 and DS110 explicitly teach
AI/ML methods. MGMT416 instead teaches managerial use of AI systems for business
decisions. MGMT422 centers visual communication/storytelling. DS100, FIN320,
MGMT232/432, MIS245, IS465 and PHIL310 combine substantial fields and remain mixed.
The IS465 description expressly disclaims depth in any one subfield.

Exact prerequisites and restrictions are preserved, including MTSM permission,
class standing, the FIN218/310 preparation outside the printed core, and IS392's
database prerequisites. They are conditional enrollment rules, not extra fixed
degree rows or inferred waivers. PHIL335 expressly permits ENGL102 concurrently.
DS100 explicitly states no prerequisites; blank statements elsewhere remain
unknown. The PHIL310 course description confirms GER eligibility but does not
resolve double use in the plan's separate allocations. Full audit remains in
progress; large GER option descriptions and existing policy questions remain.

### GER science content review — 2026-10-11

Individually reread 22 actual NJIT science option descriptions: 13 physics, seven chemistry/environmental-science and two biology courses. Twenty concern physical/environmental-science domain knowledge and practical experiments (applications under this taxonomy); BIOL 115 combines biology with critical gender/social interpretation and BIOL 150 combines variability/statistics with natural-science applications, so both are mixed. Lab-only descriptions are interpreted using their explicit named lecture association, not assumed from course numbering. Existing nine conditional laboratory relationship nodes remain unchanged.

Current NJIT R120 101/102/207/208/237 entries provide only headings/contact hours, not explanatory descriptions. They remain unreviewed while independently public Rutgers evidence is still to be pursued. A blank course block is not a publisher denial or proof that no fuller source exists. Nothing changes the R216 206 three-credit observation or the unresolved Rutgers pairing question. No physical-science code prefix, elective role or AI program association supplies a subject label.

### Humanities/social-science option content — 2026-10-11

Fifty current course blocks individually read: 43 primary subjects, four mixed (PSY 210/358 and STS 380/382), three unclassified (variable PSY 325, broad methods STS 205, individually determined STS 303). STS 307 is statistical/quantitative methodology and therefore mathematics; the philosophy and social-context AI courses are human_context because of their actual content. Topic variability alone does not make STS 325 unknown: its description explicitly fixes a social/ethical/political lens. No prefix or degree-membership classification was used.

PSY 210 and STS 201/205/221/376 explicitly allow either indicated GER allocation but not both; these are conditional option notes, not added fixed requirements. HSS 404/407 preserve senior standing and the stated concurrent three-credit portion of prior GER preparation. STS 303 refers to STS 301's individualized work and still explicitly qualifies for the GER; the reference does not substitute STS 301 or its one-credit amount.

STS 378 and LIT 378 each explicitly name the other as co-listed. Their distinct displayed titles remain; a manually reviewed crosslisted identity group counts one offering. The graph is now 32 fixed and 348 named option identities from 349 option source records (381 total records, 380 mapped identities). Other Rutgers/slash or similarly named courses are not merged. This is a bounded identity correction, not proof that all possible aliases are resolved. GER content and degree-wide policy work remain in progress.

### History descriptions and Rutgers source boundary — 2026-10-11

Read all 44 degree-listed HIST descriptions in the independently published NJIT History chapter. Each describes historical, cultural, legal or social interpretation and is manually reviewed as human_context. This is not prefix classification: HIST 328/329 use geographic databases for historical inquiry; HIST 322 examines AI law; HIST 373/381 interpret science and medicine historically; HIST 387 examines computer innovation and social context. None is mislabeled as technical methods merely because its objects include technology. HIST 325 has variable topics but explicitly confines them to historical inquiry. Published English/GER grade and concurrent-preparation clauses remain intact.

The same current NJIT chapter contains 89 R510 and 54 R512 degree-option entries with headings/credits but no explanatory descriptions. The independently located Rutgers SASN page https://sasn.rutgers.edu/undergraduate-history-course-list was refused by robots-aware Fetcher, and that route was stopped. Search results included dated older Rutgers catalogs; these were not promoted as current-course metadata. The route denial does not establish that all Rutgers sources are inaccessible. Their subjects remain unreviewed while additional ordinary public sources may be considered.

### FYS completion and AD333 content — 2026-10-11

The public Learning Communities First Year Seminar page explicitly requires an S (satisfactory) grade for new first-time students before graduation; unsuccessful students retake online asynchronously. Attendance is mandatory and two or more absences create a risk of failure, not an automatic-failure statement. These completion conditions are now mapped separately from the degree plan's explicit zero-credit amount. The goals cover transition, study skills, campus resources, self-assessment and professional connections; after reading them, FYS SEM is reviewed unclassified rather than unreviewed. No portal or Canvas was entered.

AD333's actual description teaches visual art, creative sketching and communication and is human_context. English/GER minimum grades and the explicit exclusion of ID, INTD and DD majors are preserved. The source permits interpretation for this Business with AI option without inventing exceptions for excluded majors.
