# UC San Diego remaining COGS course-content contribution

Reviewed 2026-10-11. Scope is exactly **64 identifiers** in `/tmp/ucsd-codeonly-cogs-targets.json`. Each earlier record had no title or description and carried an explicit evidence-insufficiency label, **not a content review**. This contribution reads actual descriptions for those identifiers; it does not reuse that earlier label as certification. The three previously handled COGS 2/190A/194 records are excluded. Only the helper, manual manifest, tests and this note are changed.

## Exact official evidence

The observed [official course index](https://catalog.ucsd.edu/front/courses.html) links the [Cognitive Science chapter](https://catalog.ucsd.edu/courses/COGS.html). The existing ordinary robots-aware Fetcher response is HTTP 200, fetched **2026-10-11T09:31:42+00:00**, and identifies **General Catalog 2026–27**. Its raw source at `/tmp/ucsd-final-science-COGS.html` was verified against SHA-256 `d6d8970ba53b2122dfc0c9ccb28ca025f6a97ece28c24808ed1f89e0d7f1c564` before reuse. No additional network request was needed. Provenance remains in the final-science source index and ignored HTTP cache; the manifest preserves the same registered `-cogs-courses` source identity.

All **64 exact current headings and complete bodies were read**, together with the chapter and Lower Division/Upper Division/Graduate introductions. Every target has its own single-code heading: no assigned record depends on a shared/range heading, and unrelated graduate ranges are not used. There are **64 approved observations, no missing records and no title holds**. Because earlier titles were null, exact code matching supplies current names without pretending there was an earlier title match or guessing a renumbering.

**COGS 120 prints five quarter units; the other 63 print four.** Twelve blocks have no formal `Prerequisites:` clause and retain null values, with separately stated recommendations/exclusions still in notes. Absence of the clause is not absence of institutional eligibility conditions. The inspected section introductions add no independent eligibility policy; any future change is guarded.

## Manual taxonomy and rationale

The result is **58 single-category reviews and six mixed reviews**. Counts are 44 applications, seven AI/ML, two foundations, two mathematics, three human context and six other/mixed. These are content counts for this exact batch, not the degree's fixed requirements or a complete department inventory.

| Category | Codes | Actual content boundary |
| --- | --- | --- |
| AI/ML | 118A, 118B, 181, 182, 185, 186, 188 | Explicit supervised/unsupervised learning, artificial neural/deep learning, reinforcement learning or AI/optimization algorithms. Variable advanced methods in 185 still have a specified AI method family. |
| Foundations | 3, 18 | Programming, algorithms/data structures, Python functions, tests/debugging or web implementation are explicit taught skills. |
| Mathematics | 14B, 109 | Statistical analysis and mathematical/computational modeling are the described methods, rather than department-derived labels. |
| Human context | 10, 102A, 126 | Human consequences of technology; explicit philosophy/history/cultural framing of cognitive science; or a survey of ideas and technologies shaping HCI. |
| Mixed AI/ML and mathematics | 9 | Introductory mining/learning methods and graph-theoretic concepts are both named; the brief outline does not establish one as primary. |
| Mixed foundations, mathematics and AI/ML | 108 | Hands-on programming and experimental data-science challenges explicitly span statistical and machine-learning methods. |
| Mixed applications and human context | 12, 20, 174 | Cognitive/scientific explanation and cultural/philosophical perspectives on language; biological/cognitive and cultural music systems; or pharmacology and historical/cultural drug accounts. |
| Mixed foundations and applications | 8 | Introductory Python and hands-on robotics are both explicit activities; no AI algorithm is stated. |

The other **44 are applications**, with a separate rationale for each actual description:

- Biological/cognitive science: 1, 11, 13, 14A, 15, 17, 100, 101A/B/C, 102B, 107A/B, 110, 115, 118C, 143, 151, 152, 153, 154, 155, 156, 157, 164, 169, 171, 172, 175, 176, 178, 179 and 184.
- Applied HCI, product/design or neural-interface practice: 102C, 120, 121, 122, 123, 124, 125, 127, 187A/B and 189.

The boundaries matter:

- COGS 107B's **Systems Neuroscience** concerns biological neural activity, not computing systems. COGS 118C and 179 teach neural-signal/electrophysiological methods. COGS 189's pattern recognition is part of a concrete brain-interface domain; the description does not separately establish a primary AI curriculum.
- COGS 164's reward/learning is biological and educational; 178's genetic influences are biological, unlike 186's explicitly AI genetic algorithms. COGS 101B's learning concerns experimental human cognition. A shared word does not imply a shared taxonomy.
- COGS 152 studies how minds create mathematics; it does not teach mathematical technique. COGS 153 uses computer simulations as evidence about human comprehension, without specifying software/NLP implementation training. COGS 184 synthesizes evolutionary, anatomical and cognitive evidence into a timeline; “modeling” does not establish a general mathematics course.
- The HCI cluster specifies design practice, prototypes, portfolios, users and professional products. “Technical systems” in 124 and “information architecture” in 187A do not establish operating systems, computer architecture or databases. COGS 120's applied-design judgment agrees with the separately reviewed CSE 170 content boundary. Its computer implementation and cognitive/social principles support that design practice.
- COGS 1 is an introductory scientific survey of cognition. Examples such as robots and neural networks do not independently establish a taught AI-methods component. COGS 100 concerns theories of embodied/distributed cognition rather than robot construction. COGS 102A, by contrast, explicitly specifies philosophy/history themes and cultural framing.
- COGS 13/102B explicitly practice empirical field methods and observation of cognition; ethnography's history supports that research activity. COGS 14A's research ethics accompanies concrete experimental-design methods. COGS 15 uses taboo language to teach acquisition, change, pronunciation and comprehension rather than cultural criticism by default.

## Preparation and source-specific conditions

All formal prerequisite suffixes are retained exactly, including compressed AND/OR syntax, parentheses, old code references and repeated terms. No new precedence or equivalence is invented.

- **118A/118B may be taken in either order.** Their alternatives are preserved literally. The repeated CSE 11 in 118B is not silently removed. The long preparation lists for 181/182 remain as printed.
- **18:** COGS 3 is recommended for limited computing experience, not mandatory. **120:** basic HTML familiarity is recommended. **101B:** COGS 1 is required while 101A is recommended, even though the recommendation follows inside the parsed suffix.
- **156:** the suffix prints upper-division standing and expressly recommends developmental psychology/linguistics background; that background is not rewritten as required named courses. **157:** students should have music-notation experience, separate from the formal 101A/101B/101C alternatives. **164:** biology, physiology, 107A/B/C or education courses are recommended; upper-division standing is the formal prerequisite.
- **3** explicitly requires no previous programming experience, without asserting every possible enrollment condition is absent. **8** prints freshman and sophomore standing and explicitly says no prior programming experience is required; no all-years eligibility is inferred.
- **187B** permits 187A or instructor consent. **169** retains its printed COGS 1 and 107A or permission wording. **178** retains COGS 107A-B or consent without turning the range into a new identity. **152** preserves EDS (20S or 30 or 31) within its alternatives.
- **15** has a content advisory about swearing/taboo language. That caution is not converted into an enrollment prohibition.

No major restriction, grade threshold or repeat permission is invented where the individual blocks do not state one. All exact source clauses remain in the manifest and emitted prerequisite strings/notes.

## Credit exclusions and identity evidence

Exclusions remain distinct from cross-list or historical identity evidence:

- Only one of **BILD 62, COGS 18, CSE 8A or CSE 6R** may earn credit.
- Only one of **COGS 181, CSE 151B or CSE 154** may earn credit.
- **COGS 188/CSE 151A**, **COGS 120/CSE 170**, **COGS 143/143GS**, **COGS 184/184GS** and **BILD 12/COGS 17** have duplicate-credit restrictions. Those alone do not create alias groups.
- **COGS 20 explicitly cross-lists MUS 20** and separately limits credit to one of MUS 20, MUS 20R or COGS 20. The exclusion does not prove that every online/in-person version is one identity. Its physiological/cognitive and cultural perspectives support the current mixed review.
- **COGS 110 explicitly cross-lists HDS 121**, states HDS 121 was renumbered from HDP 121, and restricts credit to one of the three codes. That explicit history is retained for primary identity review without emitting a group here.
- COGS 17 separately states college general-education applicability for Marshall and Roosevelt and for Warren **by petition**. This is not a universal AI-degree requirement or an unconditional Warren approval.

## Guarded helper and focused checks

`ucsd_cogs_remaining_reviews.py` exports metadata-only `parse_observations(html, subject=None)` and the URL-keyed `SOURCE_PARSERS`. It validates H1, 2026–27 edition, exact single-code heading, full normalized body including nested and unwrapped text, actual section membership and entire chapter/section context. A changed code, combined heading, duplicate, policy or password form fails closed. It emits no manual review, audit or identity group. The primary owner deliberately replaces earlier insufficiency labels after integration and composes this observer with the same-URL prior three-target helper.

**16 focused tests passed**, including an exact cached replay yielding all 64 observations and no dispositions. Tests cover five-unit content, full-body changes, recommendations versus prerequisites, section movement, source omissions, exclusions versus identity, AI versus biological meanings, manual mixed categories, null earlier titles and nonoverlap with COGS 2/190A/194. No full suite, build, seed or ledger change was performed.
