# UC San Diego SIO course-content contribution

Reviewed 2026-10-11. Scope is exactly the **41 existing unreviewed SIO identifiers** in `/tmp/ucsd-sio-targets.json`. Only the owned helper, manifest, tests and this note change; no seed, requirement, identity group, shared observer or audit ledger is edited.

## Source and bounded results

The observed [official course index](https://catalog.ucsd.edu/front/courses.html) supplies the actual link to the [Scripps Institution of Oceanography chapter](https://catalog.ucsd.edu/courses/SIO.html). The normal robots-aware Fetcher returned HTTP 200 at `2026-10-11T08:26:37+00:00`. The chapter identifies **General Catalog 2026–27**. Raw HTML is kept privately in `/tmp/ucsd-sio.html` and the ignored Fetcher cache; `/tmp/ucsd-sio-source-index.json` records fetch provenance. The committed manifest records the exact response hash, edition, headings and complete normalized body hashes. No raw catalog descriptions are committed.

All **37 exact matching blocks** were read in full. **35 observations are approved for metadata integration: 29 applications reviews, four mixed reviews and two unclassified reviews.** Four identifiers lack an exact current heading; two matched codes have unresolved or contradictory titles. These are individual version/source dispositions, not claims of discontinuation or absence from the institution.

| Identifier | Disposition |
| --- | --- |
| SIO 104 | No exact current heading for the listed Paleobiology and History of Life. |
| SIO 140 | No exact current heading for Wilderness and Human Values. |
| SIO 141 | No exact current heading for Chemical Principles of Marine Systems. |
| SIO 142GS | No exact current heading for Wilderness and Human Values Abroad. |
| SIO 105 | Current **Sedimentology and Stratigraphy** differs substantively from listed **Conservation Solutions**. Current content is documented but withheld. |
| SIO 113 | Current **Computing and Data Analysis in Geosciences** differs from listed **Introduction to Computational Earth Science**. Related subject matter does not independently establish a title/version relationship; current content is documented but withheld. |

Held 105 supports applications and held 113 explicitly teaches beginning Python, supporting foundations for the *observed current blocks only*. Those candidate reviews must not certify the unresolved older seed identities or transfer their metadata. The primary owner should retain an unclassified identity disposition for a held older record until the version relationship is established.

Other title differences are bounded: SIO 102/108 omit “Introduction to”; 109R adds “Online”; 194 varies punctuation. SIO 114 omits “Critical” from its heading but explicitly retains critical analysis in its description. Listed explanatory cross-list text is retained separately from the current title.

## Classification boundaries

- The 29 single-category observations cover planetary, geological, oceanographic, atmospheric, biological, geospatial, public-health and archaeological science or practice. Historical geological time does not make a course human history. Nor do social relevance, a field trip or a computing prerequisite determine category.
- **SIO 25, mixed:** scientific climate evidence and impacts are taught alongside government responses and adaptation strategies.
- **SIO 114, mixed:** scientific models, measurements and research designs are explicit alongside environmental-justice critique, activism and community engagement. This agrees with the independently reviewed ETHN 136 mixed candidate set, without certifying identity.
- **SIO 109/109R, mixed:** the actual SIO descriptions explicitly integrate climate technology with governance, policy and other social dimensions. This is more specific evidence than the prior generic POLI 117 description that remained unclassified. Primary integration should reconcile that added source before certifying any shared course classification. This helper does not edit the POLI review.
- **SIO 110, applications:** GPS field surveys, ArcGIS use, spatial analysis and web presentation are applied geospatial methods, not stated general-purpose programming or computing infrastructure.
- **SIO 101/117/147, applications:** quantitative oceanographic inquiry, climate physics, and phylogenetic inference/comparative methods serve their specified scientific domains. The sources do not establish a standalone general mathematics course. SIO 147 has a substantial computer lab but no stated programming language or software.
- **SIO 116/116GS, applications:** the organizing content is climate-linked public-health mechanisms and responses, including disease, air pollution, extreme weather and vulnerable populations. The sources do not state an independently dominant social-policy analysis objective.
- **SIO 166/167, applications:** multidisciplinary paleoenvironmental tools and geoarchaeological sedimentology/laboratory/field training are primary; human behavior and sustainability are investigated through these methods.
- **SIO 194/196, unclassified:** a UCDC seminar or individually supervised honors research supplies a format and eligibility, not a specific research topic. Neither the SIO prefix nor the host institution establishes the actual subject.

## Units, prerequisites and restrictions

The 35 approved headings give **32 courses at four quarter units and three at six**: SIO 50, 147 and 167. No course-credit range is present in the matched headings. SIO 194’s separate internship has a six-to-eight-unit range; those credits are not added to its four-unit seminar. Credit units follow the verified UCSD quarter-hours contract.

- All printed prerequisite suffixes are preserved literally, including alternatives and conjunctions. Explicit “none” remains stated evidence. SIO 109 and 109R have no prerequisite clause, so their values remain null rather than inheriting the upper-division rule from a different chapter.
- SIO 3 is designed for nonbiology majors, and 30 for a broad audience without a professional-science plan. Neither description states an exclusive major enrollment prohibition.
- SIO 46GS, 121GS and 116GS require application and acceptance to the Global Seminars Program and may have program/materials fees. SIO 121GS additionally requires SIO 10 or 50. These conditions are not transferred to unsuffixed counterparts.
- SIO 50 includes laboratories and substantial fieldwork and may have fees. Held 105 likewise states laboratory/fieldwork and possible fees; those facts are not transferred to the older Conservation Solutions identity.
- SIO 167’s recommended SIO 50/similar, ANTH 3/similar and digital-heritage preparation remains separate from its junior/senior/graduate-standing-or-consent prerequisite.
- SIO 196 permits credit twice. It requires ninety completed units including twelve SIO units, overall GPA 3.3 and SIO GPA 3.5, a Scripps Steering Committee-approved honors proposal and a department stamp. Research is specially arranged under a Scripps faculty member.
- SIO 194 requires department approval and UCDC participation during the enrolled quarter. Its block does **not** state a same-course relationship with other departments’ UCDC seminars; a shared name is insufficient.
- Credit exclusions are preserved for SIO 20/20R, SIO 134/BIEB 134, SIO 114/ETHN 136, SIO 116/116GS, SIO 166/ANAR 166 and SIO 167/ANAR 167. Exclusion alone does not certify identity.
- SIO 109 explicitly cross-lists POLI 117; SIO 109R explicitly cross-lists POLI 117R. Each also allows credit for only one of POLI 117, POLI 117R, SIO 109 and SIO 109R. This four-code credit restriction is not itself a four-way identity declaration; online delivery remains separately stated.

## Guard and validation

`ucsd_sio_reviews.py` supplies metadata-only `parse_observations(html)` and URL-keyed `SOURCE_PARSERS`. It guards the chapter heading, edition, full exact course headings and complete bodies, including nested paragraphs and unwrapped text. Changed text, prerequisites, units, omitted bodies, duplicate codes, changed title-hold evidence or a formerly missing identifier appearing requires renewed review. Password forms are rejected. Output contains only program identity, course metadata and source dispositions; manual taxonomy reviews remain in the manifest. No review/audit/requirement/identity certification is emitted.

**14 focused tests passed**, including exact cached replay of all 35 observations and six dispositions. Tests cover full-body source changes, nested/unwrapped text, edition and title holds, fixed credits versus separate internship range, research/grade/program restrictions, null prerequisites and the domain/mixed/unknown boundaries. Full-suite/build checks and any existing same-URL observer composition remain with the primary owner.
