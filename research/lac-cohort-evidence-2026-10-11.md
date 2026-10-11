# Bounded LAC membership reconciliation — 2026-10-11

**No additions verified.** The current86-member liberal arts roster remains unchanged and incomplete. The [evidence manifest](lac-cohort-evidence-2026-10-11.json) contains18 candidate branches, source locators, precise barriers and empty `proposed_additions`/`proposed_sources` arrays. It is outside the automatic data loader. No institution is excluded merely because this pass did not find sufficient evidence.

The existing contract loads `data/cohort.json`, with a source registry and per-institution ranking objects. Exact overall ranks require the correct publisher/category/edition; explicit top100 membership can instead preserve a null rank and upper bound100. A publication-date inference would receive `primary_edition_inferred`, but this pass found no new numerical evidence warranting that treatment. Both completeness flags and cutoff-tie count remain unchanged.

The most useful source distinctions were:

- [Austin College’s September22 announcement](https://www.austincollege.edu/news/~board/press-releases/post/us-news-world-report-college-rankings) explicitly names2027, but lists subcategories without an overall rank or top100 statement.
- [New College of Florida’s September22 announcement](https://www.ncf.edu/news/new-college-of-florida-on-the-rise-across-three-national-rankings/) explicitly names2027. Its U.S.News numbers14/37/88 concern component metrics; its overall numbers belong to another publisher. None establishes the target bound.
- [Gustavus’s discovered ranking report](https://gustavus.edu/news/gustavus-shows-breadth-depth-national-rankings) dates to September24,2024. Its overall66 was rejected as wrong-edition evidence.
- [Luther’s linked ranking report](https://www.luther.edu/news/u-s-news-rankings-2026) explicitly concerns2026 and gives111. It establishes neither inclusion nor exclusion for2027.

Readable bounded archive/facts reviews also covered Dickinson, St.John’s College, Wofford, Hanover, Bennington, Hampden-Sydney, Wheaton Massachusetts, Reed and Principia. Separate St.John’s campus identities were not inferred. Wofford, Hanover, Hampden-Sydney and Principia exposed news entries around the2026 release period without a qualifying ranking announcement in the inspected listing. Bennington’s returned listing and one Dickinson pagination response had limited freshness; these are not exhaustive archive checks. Wheaton’s observed award was from PrincetonReview.

Five candidate branches retain access/content limits: PugetSound and Hollins homepages returned internal reader errors without a disclosed HTTP cause; Whitman Stories returned502; Susquehanna News returned a restricted-URL error; SarahLawrence News yielded a filter shell; other inspected content there did not establish a rank. No restriction was bypassed or repeatedly retried. Previously documented publisher, VMI, AgnesScott and dataset barriers were not retried.

Targeted search repeatedly returned unrelated single-term results, so official navigation supplied the usable discovery trail. The remaining need is still a lawful complete2027 overall LAC table, authorized export, or sufficient independently verified institutional reports to enumerate every intermediate group and the rank100 ties. The18-candidate list is a bounded research queue, not a proposed substitute roster.

Validation checks JSON readability,18 unique candidate identifiers, no candidate already present in the86-member baseline, source URL structure, empty proposal arrays and unchanged baseline completeness semantics. No runtime data, schema, maintained database or PLAN changes are part of this artifact.
