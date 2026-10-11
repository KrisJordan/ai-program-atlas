# Additional undergraduate AI paths at six already-confirmed universities

Reviewed 2026-10-11. Baseline release snapshot: `91974dc63c95a863960f8685e20eb6f80e74315b` (before these four additions). The [dated ledger](../data/surveys/national-confirmed-depth-batch2-2026-10-11.json) retains 31 official-source observations, precise inspection boundaries and remaining work for all six institutions. A confirmed program does not exhaust its institution's inventory.

## Four newly confirmed records

| Institution | Additional path | Local inventory captured | Remaining scope |
| --- | --- | --- | --- |
| NC State | [Computer Engineering BS: AI and Machine Learning concentration](https://catalog.ncsu.edu/undergraduate/engineering/electrical-computer/computer-engineering-ai-machine-learning-concentration-bs/) | Linear algebra alternative, machine learning, 6 published AI/ML elective hours, 10 open-elective hours, named pools and conditional approval rules. 111 course observations / 9 nodes. | Applicable declaration, grades, host-course reuse, residence and transfer; exact credit-unit definition. |
| NC State | [Electrical Engineering BS: AI and Machine Learning concentration](https://catalog.ncsu.edu/undergraduate/engineering/electrical-computer/electrical-engineering-bs-ai-machine-learning-concentration/) | Parallel local structure but 12 open-elective hours. ECE 525 is in the open list, not this program's AI pool. 111 observations / 9 nodes. | Same policy/unit review; do not silently share the Computer Engineering elective pool. |
| Michigan State | [Artificial Intelligence concentration in Computer Science BS](https://reg.msu.edu/AcademicPrograms/ProgramDetail.aspx?PType=UGRD&Program=CMPS1_BS1) | Choose two initial courses, then three not taken above; 24 distinct named options plus conditional CSE 499 research. Official transcript certification, maximum one concentration. 25 observations / 5 nodes. | Applicable declaration, grade, overlap, residence/transfer and graduate CSE 803 enrollment rules; credit-unit definition. |
| Texas A&M | [Artificial Intelligence in the Arts minor](https://catalog.tamu.edu/undergraduate/performance-visualization-fine-arts/artificial-intelligence-arts-minor/) | Three required courses and two of four prescribed electives; 15 explicitly published semester credit hours. The [department](https://pvfa.tamu.edu/academics/visualization-program/minor-in-ai-in-the-arts/) supplies elective names and individual credits. 7 observations / 4 nodes. | University/college minor eligibility, grades, overlap, residence and transfer. |

Stable IDs are `ncsu-computer-engineering-ai-ml-concentration`, `ncsu-electrical-engineering-ai-ml-concentration`, `michigan-state-cs-ai-concentration`, and `texas-am-ai-arts-minor`. Total: **254 program-course observations and 27 requirement nodes**. These are inventory counts, not required-course totals, unique institutional courses or comparable credit loads. All four remain **partial**.

The NC State open lists contain verbatim slash labels that overlap separately named AI options. Their labels are retained without inventing equivalences. Blank course titles, alternative-row credits and variable-credit amounts remain null where a single value is not published. Open-ended advisor permission clauses are represented as rules, not treated as a missing finite list. Published hour selections remain notes while the precise credit unit is unverified; no credit conversion or completed student pathway is inferred.

The concentration records exclude the rest of their host bachelor degrees. The minor is a separate credential; its application links were read, never submitted. Course descriptions, prerequisites, public sites/syllabi, source-stated outcomes and first-offered dates remain separately unverified.

## Depth and nonfindings

- **Florida:** The [undergraduate program directory](https://catalog.ufl.edu/UGRD/programs/) and engineering CS, liberal-arts CS, computer engineering and electrical engineering detail pages yielded no additional qualifying path in those branches. Four additional AI-titled directory hits are certificates; they stay excluded. The existing GeoAI minor remains distinct. An intelligent-systems elective-interest example is not a formal AI concentration.
- **Georgia:** The [public directory](https://bulletin.uga.edu/Program/Index) rendered 13 results for `artificial intelligence` in ordinary Chrome, all on one page. The existing CS AI emphasis is confirmed again. Cognitive Science's AI Foundations Area is a distribution category, not an independently declared concentration. Four undergraduate AI certificates and graduate AI awards remain excluded. Other department details, including the Cognitive Science minor, are not exhaustively reviewed.
- **Ohio State:** The current public majors finder displayed `Majors (0)` for the same query. That narrow result was supplemented by the [cross-college minor directory](https://artsandsciences.osu.edu/academics/programs/minors), CSE undergraduate major/minor pages and ECE's seven academic domains. No additional formal AI-titled path was established in those branches; the existing BSCSE/BSCIS AI specialization remains. A stale `/majors-and-academics/minors` URL returned HTTP 500 and a browser Page Not Found, then visible navigation led to the current directory. This is not an access barrier.
- **NC State, Michigan State and Texas A&M:** Their program/minor directories were followed into the newly confirmed formal paths. Graduate awards and certificates stayed excluded. Other departments and announcements remain outside the bounded review.

No row claims institution-wide absence. Dynamic search shells were reviewed through the ordinary public UI rather than treated as empty catalogs. Readable pages were fetched with the project's robots-aware cache; no authentication, robots or explicit access restriction was bypassed. Raw HTML and browser source material are excluded from Git.

## Georgia host-plan ambiguity

The [current CS BS Bulletin page](https://bulletin.uga.edu/Program/Details/73962?IDc=ARTS) retains the same AI emphasis and waiver language as the existing department-sourced record. Its general Major Electives heading says 23 hours, while the Areas of Emphasis preface and AI paragraph say 12. The sample AI four-year plan also retains CSCI 4720 and CSCI 4730 although the emphasis waiver removes those requirements on full completion. This pass records those host-plan ambiguities; it does not rewrite the existing local emphasis audit or silently choose one parent-plan interpretation.

## Reproduction and checks

`atlas/adapters/confirmed_depth_batch2.py` observes actual source tables and scope boundaries. Each new ID has its own wrapper and evidence notes. Parser tests cover changed choice amounts/pool members, omitted sections, source-specific NC State alternatives, MSU non-reuse and transcript context, missing course metadata and separately sourced TAMU course-versus-credit selection rules. Observers never generate completeness audits.

Focused command: `uv run pytest tests/test_confirmed_depth_batch2.py`. An isolated ingest/check/build uses only these four records, this ledger and the committed cohort; it does not alter the maintained database.
