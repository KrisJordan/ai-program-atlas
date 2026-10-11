# Analytics & Artificial Intelligence Co-Major

Reviewed 2026-10-10. Official identity source: https://live-villanova-catalog.cleancatalog.io/analytics-artificial-intelligence/analytics-artificial-intelligence-comajor

A co-major within the BBA requiring a primary VSB major; award other preserves the nonstandalone BBA relationship. Official directory specifies Class of 2029 and beyond, not a launch date.

The identity source and local curriculum are parsed from fresh content. No parser emits a verification timestamp or manual completeness audit. See the review below for current scope and remaining gaps.

- Context: [Majors and Minors](https://www.villanova.edu/university/business/academics/undergraduate-programs/degrees.html)
- Context: [Undergraduate Catalog 2026-2027](https://live-villanova-catalog.cleancatalog.io/)

## Curriculum review — 2026-10-10

**Partial:** the co-major’s Other Approved Electives modal is empty; this is an unresolved inventory/approval gap. This scope does not certify the host BBA. Analytics electives retain the separate MIS 3050/MIS 2030 co-major choice. CSC 4480 is disallowed in the minor but conditionally permitted in the co-major. Graduate substitutes retain the joint-program condition and permission/retroactivity rules. Published elective-pool subtotals are not graduation totals.

Fresh parsing reads actual course rows, local credit totals and elective counts. Reviewed policy summaries require matching source clauses and otherwise fail for review. Source changes never renew the manual audit. Separate course-source parsers observe exact identities, prerequisites, credits and description hashes; curated descriptions are short original summaries, not replayed by the parser. Only five required course catalogs were inspected across the three programs; elective metadata remains incomplete. Credit amounts remain unit `unknown` until separately normalized.

## Other Approved Electives clarification pass — 2026-10-11

The live catalog returned HTTP 200; modal `#modal8225`, titled **Other Approved Electives**, contains only a `Total Credits` label, with no course, link, amount, or approval procedure. The primary adapter now verifies that exact empty state and raises for review when content appears, rather than reusing a stale empty-pool interpretation.

The official directory links to the [Analytics and AI program page](https://www.villanova.edu/university/business/academics/undergraduate-programs/degrees/analytics-and-artifical-intelligence.html), which confirms the co-major's host curriculum but does not supply the missing elective pool. Its “EARNING A CO-MAJOR” link points to `https://test-villanova-catalog.cleancatalog.io/analytics-artificial-intelligence/analytics-artificial-intelligence-comajor`; the standard fetcher reports **robots disallows fetch** for that exact URL. That route stops there. No alternate-host substitution, hidden endpoint, or test/live curriculum merge was used. **Partial remains** for the same exact missing inventory/approval-rule gap; all 14 courses and 11 requirement nodes are unchanged.


2026-10-11 second-major relationship review: reread the official program catalog and retained its exact additional-major/second-major/co-major terminology and mandatory companion-major eligibility in `major_relationship`. The award remains unchanged. This manual evidence-backed relationship is separate from scraper observations; optional double-major compatibility is not equivalent. See `research/second-majors.md`.

## Additional-major correctness review — 2026-10-11

Fresh actual source review covers all 14 represented course descriptions and current co-major rows. Manual fixed/option/context sets are 2/8/4. Exact MIS 3050 or MIS 2030 becomes one nested elective slot. Hash-guarded metadata observations cannot emit manual category review or completeness. Source corrections distinguish statistics, databases, applications and programming from AI; MGT 3180 remains unclassified because its AI title conflicts with a management-theory description. Undergraduate MSA 8105 substitution label differs from current graduate title; graduate edition/applicability stays unresolved. MSA 8240's actual body is mathematical despite its title. VSB GPA and letter-grade applicability were reread separately. The empty Other Approved Electives inventory, graduate version applicability and credit-unit normalization preserve partial status. Detailed source locators, hashes, manually expected categories and review limits are in `research/additional-major-review-business.json/.md`; no host BBA certification.

Independent peer-source correction: MIS 3060 is mixed systems/AI (other), because its actual output is a BI pipeline/Modern Data Stack with a GenAI framing and no primary AI-method instruction established. Final option subject counts: mathematics 2, systems 2, applications 2, other 2. FIN 2360's Finance-elective exclusion, MGT 3180 junior/senior standing, and MKT 2240's ambiguous literal “Maximum of 5 VSB minors” remain course notes; no eligibility meaning was invented for the last phrase. Manual review digest updated.
