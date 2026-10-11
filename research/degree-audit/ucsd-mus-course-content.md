# UC San Diego MUS course-content contribution

Reviewed 2026-10-11. Scope is the **33 existing represented MUS targets** supplied in `/tmp/ucsd-mus-targets.json`. Only this contribution’s helper, manifest, tests and note change; no seed, shared adapter, requirement, identity group or audit ledger is edited.

## Official source and coverage

The observed [official course index](https://catalog.ucsd.edu/front/courses.html) links the [Music course chapter](https://catalog.ucsd.edu/courses/MUS.html). The normal robots-aware Fetcher returned HTTP 200 at `2026-10-11T08:41:05+00:00`. The chapter explicitly identifies **General Catalog 2026–27**. Raw source is kept in `/tmp/ucsd-mus.html` and the ignored Fetcher cache; `/tmp/ucsd-mus-source-index.json` records provenance. The committed manifest records exact source and full-body hashes, headings, edition and fetch time, with original summaries rather than raw descriptions.

All **27 exact matched target blocks** were read in full. They support **17 human-context and five applications reviews, plus five unclassified observations**; 22 have a reviewed single category. Six exact identifiers are absent from this edition: **MUS 8GS, 19R, 20R, 126R, 150GS and 13AS**. Unsuffixed MUS 13/19/20/126 and MUS 8’s reference to 8GS do not supply those missing identities. No cancellation or university-wide absence is inferred. All matched title variations are limited punctuation, numbering, subtitle or explanatory cross-list differences; there are no substantive matched-title holds.

All course headings, including shared headings, were inspected. None of the 33 targets is represented only by a shared range heading: in particular, 137A/B/C and 137D/E/F each have separate blocks with distinct sequence prerequisites. The chapter-level advisory says courses are not necessarily offered every year. Its section-wide graduate restriction applies to numbers 200 and above, not these targets. No lower/upper-division section-level enrollment condition was imported into individual courses. MUS 160A and 132 were additionally read to check continuation context; their independent restrictions were not inherited by 160B or 132R.

## Actual-content decisions

- **Applications:** MUS 103A explicitly teaches composition and instrumentation through creative work. MUS 132R prepares an instrumental/vocal honors recital. MUS 137A/B/C apply jazz theory through instrumental work, transcription, composition and improvisation. Musical theory here is musical practice, not general mathematics.
- **Human context:** the remaining reviewed courses center music history, cultural interpretation, representation and social change. MUS 17’s listening-based recognition of production techniques supports historical study; it is not evidence of hands-on production instruction. MUS 107/150 retain specific critical or historical scope even with variable topics. MUS 111/112/113/116 bound their topics by cultural traditions, historical periods or music scholarship. MUS 120A explicitly introduces historical and ethnographic music studies; 120B/C continue research within that stated sequence rather than implying programming or composition projects.
- **Unclassified:** MUS 160B’s independent computing-arts project and MUS 137D/E/F’s jazz/African-diaspora honors projects do not identify their concrete methods or work. They may involve different kinds of creation or inquiry. MUS 199 permits reading, research or creative work without specifying the selected subject. Neither an arts/computing title nor a senior research format supplies a precise category.
- MUS 116’s represented source is a Latin American studies pool, but this generic topic description does not identify a particular regional offering. This is a source-content limitation, not a newly invented eligibility condition on that independently reviewed pool.

## Units and eligibility

**26 approved courses print four quarter units. MUS 199 prints 1–4**, so its scalar credits remain null and its literal range is retained in notes. No sequence credits are summed into one course. The quarter-hours context is already institutionally verified.

Every matched block has a prerequisite clause. The helper retains the complete printed suffix, including approval, recommended preparation and grading qualifications, and notes distinguish their meaning:

- MUS 8 explicitly states no prerequisites, is offered in selected years, and excludes credit alongside 8GS. Its suffix is not inferred to identify a currently available separate course.
- MUS 107 requires upper-division standing, music-major status or instructor consent, and department approval. It may be taken for credit twice.
- MUS 132R is for senior music majors pursuing performance honors. It requires MUS 132, audition and department approval, with a special Welcome Week audition before fall quarter. **R is not assumed to mean online.** The separate MUS 132 concurrent-enrollment and repeat rules are not copied into 132R.
- MUS 160B requires MUS 160A or VIS 160A, is open only to music and ICAM majors, and requires department approval. It completes and presents a project with documentation. The source explicitly says it was renumbered from ICAM 160B and permits credit for only one of MUS 160B, VIS 160B and ICAM 160B. No identity group is certified.
- MUS 160B’s exact **“Two production-course limitation”** is preserved. This block does not define its period or broader application. No per-term maximum, degree selection amount or other interpretation is invented.
- MUS 137A/B/C are the successive courses of a yearlong practical sequence. A uses the printed MUS 2A-B-C/proficiency-exam/consent alternatives; B requires A or consent, and C requires B or consent. Each retains four units.
- MUS 137D/E/F describe senior music-major honors projects. D requires MUS 137A-B-C, admission to the Music Department Honors Program in jazz and department approval. E requires D and department approval; F requires E and department approval. Admission and sequence requirements remain course-specific.
- MUS 120A/B/C recommend concurrent MUS 101A/B/C for music majors; these recommendations are not mandatory corequisites. Nonmajors require department approval. The actual prerequisite chain is preserved. Likewise MUS 112/113 recommendations for MUS 4, 8–10 or 120 are not elevated into required preparation; 113 also requires department approval.
- MUS 112/113 may be taken for credit five times; 111/116 three times; 150 twice. Variable offerings do not guarantee future availability or an unchanged selected topic.
- MUS 199 requires material not already covered by an existing course and an area derived from previous coursework. It requires instructor consent, department-chair approval and department approval, is Pass/Not Pass only, and may be taken for credit twice.

Current blocks explicitly cross-list MUS 18/JUDA 18, MUS 151/ETHN 108, MUS 152/ETHN 128 and MUS 153/ETHN 164. MUS 18 also excludes duplicate credit. These observations remain notes for primary identity review; no group is emitted. MUS 150’s slash-form prerequisite notation is preserved literally without inferring an identity group from punctuation.

## Guard and validation

`ucsd_mus_reviews.py` provides metadata-only `parse_observations(html)` and URL-keyed `SOURCE_PARSERS`. It verifies chapter identity, edition, exact course headings and complete normalized bodies, including nested/unwrapped text. Changed content, units, eligibility, duplicate headings or a formerly missing exact identifier appearing fails closed for renewed review. Password forms are rejected. Output contains only program identity, courses and source dispositions; manual `category_review` remains in the manifest for integration.

**14 focused tests passed**, including exact cached-source replay of all 27 observations and six dispositions. Tests cover variable credits, musical practice versus cultural scholarship, unspecified projects, sequence and admission rules, recommended corequisites, literal production limitation, no inferred online suffix, missing codes and complete-block/edition guards. No full suite, build, seed or ledger update was run; primary integration remains outstanding.
