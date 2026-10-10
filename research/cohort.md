# U.S. News cohort verification

Verified on 2026-10-10. Machine-readable inventory: `data/cohort.json`.

## Edition and rule

Use **Best Colleges 2027**, released September 22, 2026. The publisher's [syndicated release](https://www.prnewswire.com/news-releases/mit-claims-no-1-spot-in-us-news-2027-best-colleges-rankings-302885278.html) establishes the edition. It is not the 2026–2027 Best Global Universities ranking.

There are two independent cohorts: **National Universities** and **National Liberal Arts Colleges**. Include every institution with a published numerical rank <=100 in its category, including all rank-100 ties. Do not truncate to 100 institutions. Do not combine the categories into a single ordinal list. Public-only, private-only, regional, subject, value and teaching ranks do not establish membership.

The 2027 edition changes categories using the updated Carnegie classifications, so a previous edition cannot establish current membership. No 2026 ranks were carried forward.

## Verified inventory

| Category | Stored institutions | Enumeration status | Cutoff |
| --- | ---: | --- | --- |
| National Universities | 108 | Enumerated from a complete secondary table; authoritative confirmation pending | Nine institutions tied at 100 |
| National Liberal Arts Colleges | 66 | Incomplete verified subset | Full rank-100 tie group unknown |
| Combined inventory | 174 | Incomplete | Two separate categories |

The `complete` field is **false**: authoritative enumeration is pending for National Universities, and the liberal arts cohort is incomplete. The additive `category_coverage` field records the different enumeration states. National Universities has `enumeration_complete: true` and `verification_status: enumerated_secondary`, while `complete` remains false. Individual ranks distinguish `primary_verified` from `enumerated_secondary`. None of these numbers measures completion of the AI-program search.

### National Universities

The [Poets&Quants table, page 2](https://poetsandquantsforundergrads.com/news/u-s-news-best-colleges-ranking-2027-mit-ends-princetons-long-run-at-the-top/2/), published September 23, 2026, explicitly reports the 2027 rank and university for every row through rank 100. The stored inventory contains the minimal institution/rank facts only; tuition, enrollment, narrative and full source pages are not copied. The [College Kickstart table](https://www.collegekickstart.com/blog/item/u-s-news-world-report-posts-2027-college-rankings) independently agrees on the upper part of the cohort. Primary college reporting and Shorelight's selected-university summary also corroborate several ranks, but they are not needed to infer missing positions.

The nine institutions at rank 100 are Auburn University, Chapman University, Creighton University, Elon University, Florida International University, Saint Louis University, University of Iowa, University of San Diego and University of South Florida. All nine are included. The rank sequence has been checked using competition-ranking arithmetic: each next rank equals the number of preceding institutions plus one, ending in 108 included institutions.

This is secondary-source verification of the full published membership, not a claim that the publisher's own table was directly fetched. Every ranking row points to the source actually consulted. The publisher’s syndicated release directly corroborates MIT, Princeton and Harvard, and official Elon reporting corroborates rank 100. For these rows the primary source is preferred and the secondary table is retained as corroboration.

### National Liberal Arts Colleges

College Kickstart supplies 53 institutions through the complete rank-49 group. Six leading rows are additionally corroborated by the publisher’s syndicated release, which becomes their preferred primary source. Thirteen additional institutions have edition-specific official college sources, each linked directly from its ranking record: Centre and Gettysburg (54); Furman and Wheaton, Illinois (57); Lawrence and Thomas Aquinas (68); Saint Anselm (72); Rollins (74); Earlham (83); Lewis & Clark (97); Beloit, Hendrix and Whittier (100).

These lower-ranked facts do **not** establish complete intervening rank groups or the whole cutoff tie group. The unenumerated institutions are unknown; they must not disappear into an implied no-program result. No complete denominator or coverage percentage should be reported for this category yet.

## Access and remaining work

- Direct U.S. News category URLs were attempted and did not yield accessible tables. A separate source-access check reported robots restrictions. No restriction was bypassed.
- Andrew Reiter's [datasets page](https://www.andyreiter.com/datasets/) was indexed as containing 2027 spreadsheets for both categories, but direct access returned HTTP 403. Its unavailable files were not used.
- CollegeAdvisor's [rankings article](https://www.collegeadvisor.com/resources/us-news-college-rankings/) was indexed as linking a complete liberal arts list, but direct access returned HTTP 403. It was not used.
- Broad and institution-specific searches found many previous-edition results, rankings from other publishers, prediction posts and incomplete top-20/top-50 summaries. These cannot fill the 2027 gaps. Reddit and forum predictions were excluded from the saved evidence.
- Finish the liberal arts enumeration using a lawful accessible 2027 table, an authorized publisher export, or additional official institution reports. Verify all intermediate groups and every rank-100 tie before changing completeness. Obtain authoritative permitted enumeration for National Universities before changing that category’s `complete` flag.
- Search official catalogs and program directories for **every** cohort institution. All records here start with `coverage_status: pending`, `calendar: unknown`, `website: null` and no program IDs; absence of a linked program is not evidence of absence.

## Identifier and validation notes

Names are retained as published, with stable lowercase-hyphen IDs. Purdue and Penn State use the coordinated IDs `purdue-university` and `pennsylvania-state-university`; their ranked campus labels are preserved as aliases. Wheaton is explicitly identified as Illinois. No calendar or institutional website was inferred from a name or ranking.

Validation checks: JSON parses; 174 unique IDs; 108 National Universities and 66 National Liberal Arts Colleges; every rank is an integer between 1 and 100; every row is 2027; every source URL occurs in the source registry; 9 National Universities at rank 100; National University rank progression is internally complete. Repository-wide tests/build are the coordinator's integration check because this task owns only the cohort JSON and this note.
