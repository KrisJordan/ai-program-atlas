# UCSD remaining code-only humanities content — 2026-10-11

This contribution disposes all 89 assigned existing identifiers across 20 prefixes. The previous code-only classifications documented insufficient evidence and were not course-content reviews. Actual full descriptions and surrounding catalog context were read; curated summaries and individual manual taxonomy reviews now support 80 records. Nine retain precise missing-heading dispositions. No primary seed, degree ledger, requirement membership or identity group was changed.

## Source and version scope

Existing verified 2026–27 chapter captures were reused for History, Education Studies, Management, International Studies, Anthropology, Urban Studies, college writing programs, Environmental Studies/Systems, Black Diaspora and African American Studies, Latin American Studies, Religion and Jewish Studies. Exact timestamps, URLs, hashes and ignored cache paths remain in the manifest under the same registered source IDs.

Three additional course links were observed in UCSD's official course index, then fetched normally with the robots-aware Fetcher: [Global South Studies](https://catalog.ucsd.edu/courses/GSS.html), [Critical Community Engagement](https://catalog.ucsd.edu/courses/CCE.html) and [Synthesis](https://catalog.ucsd.edu/courses/SYN.html). All returned HTTP 200 and explicit 2026–27 catalog context. Their new source IDs end in `-gss-courses`, `-cce-courses` and `-syn-courses`. Primary integration must register these sources. No blocked endpoint, authentication, historical URL substitution or access bypass was used.

## Exact identities and shared headings

The printed HILD 2A-B-C heading establishes all three assigned components and their 4-4-4 unit sequence. HILD 7A-B-C has both a shared overview and separate 7A, 7B and 7C descriptions; every applicable block is guarded, and each specific description supplies its own emphasis. Neither the overview nor the individual block is silently dropped based on parser order.

The AAS 10/R and 11/R headings explicitly establish the two corresponding R suffixes, but do not independently describe delivery mode; online restrictions are not inferred merely from the suffix. The GSS 21-22-23-25-26-27 heading and its literal regional sublabels establish six subjects at four units each. GSS 24 is not part of that printed list. No shared sequence or slash notation becomes a cross-list identity group, and the original degree roles remain unchanged.

Missing exact current headings are ANSC 140, CCE 110, CCE 120, DOC 170, ESYS 150, GSS 24, HILD 20, HILD 80GS and USP 103. The inspected CCE chapter describes only CCE 1–3; these are not substitutes for 110/120. Other similar titles, old prefixes and incidental references do not repair a missing identifier. The chapter gaps do not establish discontinuation or invalidate the source that originally listed the code.

## Content and units

The 80 exact records contain 63 human-context, 11 applications, one mathematics and five `other` classifications. Four of the latter are mixed and one is unclassified. MGT 3 explicitly teaches probability, inference, regression and optimization and is mathematics. ANTH 2/5/42 teach biological evolution, anatomy and primate biology/conservation; these are domain knowledge, not humanities by prefix. USP 4 uses GIS for spatial decision making without establishing general-purpose programming instruction. Real-estate models and planning practice, environmental field ecology and conservation education are also applications.

EDS 124AR/BR combine actual novice programming/computational concepts with practical education and social dimensions; these remain mixed foundations/applications/human_context. ANTH 102/104 combine biological or physical-environment subject matter with human social context, without a defensible single primary category. SYN 100 gives a collaborative project structure but allows different climate-related themes and disciplinary content; it remains unclassified pending actual section evidence. Writing, Hebrew instruction and communication practice remain human context under the shared taxonomy.

JWSP 1, 2 and 3 each explicitly publish five quarter units. The other 77 exact records publish four. Uniform units in shared sequences are read component by component, never added as a student's total obligation. No unit amount is inferred for a missing heading.

## Preparation, participation and grading

SYN 100 explicitly restricts enrollment to Seventh College students with upper-division standing and completion of SYN 1/1R and SYN 2/2R. Letter grading is needed for Seventh's general-education requirement. Those clauses remain together with their exact scope, not generalized to other programs.

MCWP 40 explicitly requires satisfaction of Entry Level Writing; MCWP 50 explicitly requires the MCWP 40 requirement or IGETC. The exact online 40R, 40CR and 50R descriptions do not print labeled prerequisite clauses, so their fields remain unknown rather than copying the face-to-face variants. All published student-population, prerequisite-grade, letter-grading and credit-exclusion statements are retained where printed. MCWP 40CR's climate-education satisfaction claim remains a course-specific applicability statement, not a degree certification.

CAT 125GS explicitly requires upper-division standing and department authorization. Lower-division writing completion is preferred rather than mandatory, and the letter-grade suggestion for graduate-school preparation is a recommendation. The same source explicitly describes distance education despite the Global Seminar title; neither field is silently corrected. HILD 30GS and ENVR 142GS retain Global Seminar application/acceptance requirements and potential fees. ENVR 105 retains possible required field travel and students' responsibility for transportation. EDS 124AR explicitly requires no prior programming experience. INTL 101/102 require INTL 100 completed with C– or better. JWSP 101/102 explicitly use Hebrew and English instruction but print no formal language prerequisite.

Course-wide framing is also preserved where applicable: Anthropology cautions that not every course is offered annually; EDS advises consultation about credential applicability; ESYS directs readers to current schedule/program information; and History defines its plus marker as pre-1800 focus. No unrelated upper-division History or colloquium eligibility is applied to the lower-division HILD targets.

## Observer and handoff

`ucsd_codeonly_humanities_reviews.parse_observations(html, subject=...)` validates chapter identity/edition, exact complete course blocks, grouped-heading membership and actual section/region placement. Multiple HILD 7 observations are jointly guarded. Chapter-context hashes additionally guard the relevant History, EDS, Anthropology and ESYS framing. A newly appearing previously missing code triggers review. Runtime emits metadata and dispositions, never a manual `category_review`, an identity group or a requirement certificate.

`SOURCE_PARSERS` composes ANTH and ANSC within their shared chapter URL. The primary owner must compose this helper with all existing same-URL observers, not replace previous chapter contributions. Manual reviews are in the separate manifest; exact missing fields remain null. Fifteen focused tests cover sequence expansion, shared and individual block changes, eligibility suffixes, context and section changes, previously absent identifiers, all current cached chapters, credit amounts and conditional rules. Primary integration and the isolated degree build remain the program owner's responsibility.
