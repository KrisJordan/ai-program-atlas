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
| National Liberal Arts Colleges | 85 | Incomplete verified subset | Full rank-100 tie group unknown |
| Combined inventory | 193 | Incomplete | Two separate categories |

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

Initial inventory checks (before the dated expansions below): JSON parses; 174 unique IDs; 108 National Universities and 66 National Liberal Arts Colleges; every rank is an integer between 1 and 100; every row is 2027; every source URL occurs in the source registry; 9 National Universities at rank 100; National University rank progression is internally complete. Repository-wide tests/build are the coordinator's integration check because this task owns only the cohort JSON and this note.


## Additional primary verification (2026-10-10)

Fourteen additional LAC institutions were independently read in official 2027 ranking reports and added, each with the exact source URL, publication date when available, and ranking locator in the JSON: Muhlenberg and Berea (62); College of Saint Benedict (68); Saint John’s University, Minnesota, and Kalamazoo (74); Hope and Saint Mary’s College, Indiana (78); Morehouse (83); Allegheny and Randolph-Macon (85); Augustana College, Illinois, Juniata and Southwestern (91); Lycoming (100). Hope, CSB/SJU and Augustana pages did not establish a publication date; those values remain null. Kalamazoo’s page was published September 22 and updated September 25. Randolph-Macon and Augustana explicitly report ties. No whole tie group is certified by these isolated reports.

Fifteen existing ranks were upgraded to primary verification: eight UC campuses using the official table’s **National** column (Santa Cruz at 109 was excluded), three Rutgers campuses using the overall National Universities paragraph, Trinity University and Occidental using Trinity’s explicit three-way 38 tie statement, Scripps using its own September 29 report, and Spelman using its overall National Liberal Arts Colleges 34 listing. Secondary sources remain registered as corroboration. These upgrades do not certify complete authoritative enumeration.

VMI’s supplied official 2027 candidate URL (`https://www.vmi.edu/vmi-maintains-strong-rankings-in-u-s-news-best-colleges-list-2/`) returned HTTP 403 and was not used to establish a new row. Richmond’s supplied official article (`https://news.richmond.edu/releases/article/-/28647/university-of-richmond-named-a-top-25-national-liberal-arts-college-for-10th-consecutive-year-by-u.s.-news--world-report.html`) produced an internal fetch error, so its existing verification was not upgraded. Neither restriction was bypassed.

Updated inventory checks: 188 unique institution IDs; 108 National Universities and 80 National Liberal Arts Colleges. The latter is still an incomplete subset; both category complete flags remain false, the LAC enumeration_complete flag remains false, and its cutoff_tie_count remains null.


## Final evidence batch (2026-10-10)

The loaded LAC subset is now **85** institutions: 80 with explicit-edition numerical evidence, two additional numerical ranks whose edition is inferred from explicit September 22, 2026 release dates (Lake Forest 62 and Ursinus 91 tied), and three with explicit 2027 top-100 membership but unknown exact ranks (Stonehill, College of Wooster, Washington College). The last three use `rank: null`, `rank_upper_bound: 100`, and `primary_membership_verified`; no ordinal rank is invented. The two inferred-edition rows use `primary_edition_inferred`. Sources, dates and locators are in `data/cohort.json`. These additions preserve all incompleteness flags and do not establish a full tie group.

Harvey Mudd 8, Auburn 100, Creighton 100, FIU 100, Saint Louis 100 and Iowa 100 received additional primary evidence upgrades. FIU and Iowa explicitly identify the 2027 edition and overall 100, contrasting public 46; their exact National Universities category label is corroborated by the existing secondary table and that distinction remains in the locator. USF’s [current article](https://www.usf.edu/news/2026/for-the-eighth-consecutive-year-us-news-ranks-usf-among-the-nations-top-50-public-universities.aspx) and Chapman’s [facts page](https://www.chapman.edu/about/facts-and-rankings/index.aspx) lack a usable explicit edition/date combination, so their existing rank evidence was not upgraded.

The [Hobart and William Smith candidate article](https://www.hws.edu/news/2026/hws-climbs-13-spots.aspx) returned an internal access error; HWS was not added. Colorado Boulder’s [2027 report](https://www.colorado.edu/today/2026/09/22/cu-boulder-top-10-nationally-multiple-undergrad-programs-says-us-news-world-report) gives overall 109, and Willamette’s [2027 report](https://news.willamette.edu/library/2026/09/us-news-best-value.html) gives National Universities 208, so both are outside scope. The supplied Illinois Wesleyan article was inaccessible and supplies no usable fact here.
