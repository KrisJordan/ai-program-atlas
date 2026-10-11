# USF BSAI evidence

Reviewed 2026-10-10. The overview parser observes identity only. The curated brochure requirement inventory is deliberately separate; HTML identity success cannot mark it fresh or complete.

The September 2026 brochure identifies a current AI student, supporting active status. First offering term remains unknown. Its BSAI Four Year Plan supports the BSAI award abbreviation.

Catalog retry on 2026-10-10 used the updated default Fetcher, honoring the 120-second robots interval in bounded wait chunks. The original official link https://usf.to/BS-Artificial-Intelligence-catalogue resolved to https://catalog.usf.edu/preview_program.php?catoid=25&poid=13990, which returned HTTP 202 rather than a readable catalog page. The former local scheduling limit is resolved; the remaining blocker is the server response. No challenge-solving, alternate-query bypass or access workaround was attempted. The existing brochure inventory remains partial and was not recertified by this failed fetch.

PDF inspected via public web reader; no PDF content committed. Primary overview adapter remains identity-only and never represents brochure curriculum as freshly verified. PDF curriculum observations require human review on refresh.

https://www.usf.edu/ai-cybersecurity-computing/documents/brochures/bellini-ug-bsai.pdf

## Independent registrar supplement — 2026-10-11

Read https://www.usf.edu/registrar/register/degreeworks.aspx and https://www.usf.edu/registrar/faq/index.aspx. Six new policy nodes map the registrar's overview of 120 total, 42 upper-level and nine summer credit hours; 30 of the last 60 at USF; conditional summer waivers; and grade-forgiveness limits. These are university overview rules, not a definitive AI-major audit. Normalized credit units, entry-cohort exceptions and stricter program/college policies remain unresolved. The summer requirement is explicitly paired with the FAQ's documented waiver procedure; a request does not imply approval. Grade-forgiveness minimum D is not an AI-major passing-grade claim.

The independently public college undergraduate directory at https://www.usf.edu/ai-cybersecurity-computing/academics/undergraduate/ also lists Artificial Intelligence, BSAI, but supplies no additional curriculum. A bounded candidate landing-page request to https://www.usf.edu/undergrad/general-education/ returned HTTP 404. This is not a denial or evidence that general-education information is unavailable everywhere; normal undergraduate-office navigation later resolved a current GE page; see the follow-up below. The known HTTP 202 catalog endpoint was not retried. Major electives, program credits, general education, college policies and course prerequisites remain unresolved.

The degreeworks parser extracts current numeric amounts and checks consistency of the residency fraction. The FAQ parser guards waiver and forgiveness conditions; neither replays brochure courses or emits review state. Synthetic and permitted-cache replay tests pass.

## Current public policy and course-inventory follow-up — 2026-10-11

Normal navigation from https://www.usf.edu/undergrad/ through Undergraduate Education → Curriculum and For Students → Academic Policies and Processes exposed independently public sources. The General Education Council then linked the current GE overview and approval instructions. These successful routes replace the speculative missing GE landing as the useful research path; the earlier 404 remains just a missing URL.

- https://www.usf.edu/undergrad/general-education-council/usf-general-education/index.aspx — 36 published credits: 15 state core + 21 USF GE; each of five disciplines has three state-core and three USF credits, plus two further courses/six credits from any discipline. Enhancement labels have no separate student quota. State-core reuse as a GE elective is conditional on advisor guidance, not a general double-counting permission.
- https://www.usf.edu/undergrad/general-education-council/usf-general-education/approved-usf-general-education-courses.aspx — current eligibility comes from Course Inventory attributes. These open designation criteria are represented directly rather than inventing a finite pool.
- https://www.usf.edu/undergrad/students/civics-literacy.aspx — entry-cohort rules, course/exam and acceleration alternatives, transfer evidence, internal-test cutoff, grade-sensitive GE overlap and additional-degree exceptions. AMS X010 is a transfer-only state code, not a newly inferred USF course. Three existing brochure course names are now verified.
- https://www.usf.edu/undergrad/curriculum/general-course-information.aspx — SCNS transfer framework and all published exception categories. This does not imply acceptance of every external course into the AI major.

The policy-directory link https://cloud.usf.edu/catalog/undergrad/academic-policies-and-procedures leads back toward catalog.usf.edu. Fetcher stopped at that host's 120-second scheduling boundary; its previously unreadable HTTP 202 route was not retried. This is preserved as a redirect back to the existing catalog boundary, not a newly independent readable policy source.

The exact separately linked https://usfweb.usf.edu/academic-programs/course-inventory/ loaded publicly. Its ordinary Chrome interface navigated to https://cloud.usf.edu/academic-programs/course-inventory/; a normal CAI-prefix search returned https://cloud.usf.edu/academic-programs/searchresults?&pre=CAI. The visible notice identifies undergraduate information as effective for 2026–2027 (the separate graduate year is not inherited). Eight explicit undergraduate CAI detail links from those results were then fetched with normal robots checks:

- https://cloud.usf.edu/academic-programs/details/prefix/CAI/code/1000
- https://cloud.usf.edu/academic-programs/details/prefix/CAI/code/2001
- https://cloud.usf.edu/academic-programs/details/prefix/CAI/code/4002
- https://cloud.usf.edu/academic-programs/details/prefix/CAI/code/4024
- https://cloud.usf.edu/academic-programs/details/prefix/CAI/code/4105
- https://cloud.usf.edu/academic-programs/details/prefix/CAI/code/4203
- https://cloud.usf.edu/academic-programs/details/prefix/CAI/code/4624
- https://cloud.usf.edu/academic-programs/details/prefix/CAI/code/4841

All eight provide descriptions and three published credit hours; six contain prerequisites/restrictions. The parser preserves Boolean alternatives, grade minima, the CAI 4002 COP 4530 co-prerequisite and its “Majors Only” restriction without inventing a major list. Empty fields remain unknown. Descriptions are paraphrased only when the exact reviewed source-description digest matches; changes require review rather than replaying stale prose. Course search listings alone do not establish AI-major elective eligibility, so other CAI results were not imported as an approved elective pool. No hidden API, gate solving or rewrite of a blocked catalog URL was used.

Final coverage: **29 course records, 28 requirement/policy nodes, eight descriptions, six prerequisite/restriction statements**. Curriculum remains **partial**. Remaining requirement boundaries are the full major elective pool, exact program credits, college/program grade policies and detailed university exceptions. General education now has its published distribution and current eligibility criteria mapped. Other course metadata remain an accessible future enrichment task, not evidence of a source denial. Normalized credit units, syllabi and instructional sites are still unknown.

## Exact award label review — 2026-10-11

The reviewed award option preserves **BSAI**, mapped to **BS**. Brochure page 2: BSAI Four Year Plan. BS normalization is independently supported by the registered official program source (same program, /academics/undergraduate/bsai.aspx), whose h1 reads Bachelor of Science in Artificial Intelligence. The abbreviation remains BSAI; no prefix-based inference. Existing program ID, award_level, title and requirement graph are unchanged. This optional mapping is reviewed metadata. Scrapers queue observations without replacing curated JSON; a parse result that omits award_options does not erase it. No parser or shared Northeastern helper change is needed.

### Degree correctness review — 2026-10-11

The current official identity page and eight CAI descriptions were reread.
CAI4624 focuses on training/deployment infrastructure, distributed systems and
cloud scaling, so its reviewed subject is systems. CAI4024 is ethics/human
context; six other descriptions explicitly support AI content. Remaining
course subjects are unreviewed.

The current public brochure request was stopped by robots disallow at its exact
registered URL. The web PDF reader also returned inaccessible, but no alternate
route or access workaround was used. Its previously extracted course inventory
retains the earlier provenance and is not freshly certified. The known catalog
HTTP202 boundary was not retried. Unsupported semester_hours values inherited
by old brochure courses/rules are now unknown; actual printed credit amounts
remain. Whole-degree correctness is blocked by these requirement-source limits.

### Audit status correction — 2026-10-11

Eight CAI subject reviews and conservative unit correction complete. Other named-course metadata remain accessible through the public course inventory and are not yet reviewed; full audit remains in progress while exact catalog and brochure boundaries are retained. A source barrier does not convert still-accessible unfinished work into a completed blocked audit.


### All represented course descriptions — 2026-10-11

Read the21 remaining exact course details through ordinary public prefix-search links; all29 represented descriptions now have manual content dispositions (28 classified, CIS1930 orientation explicitly unclassified). Current exact names, numeric credit amounts and all prerequisite/restriction/other-information fields are integrated. The new `remaining_courses.py` guards each reviewed heading and full field bundle; source changes fail for review, and parsers never emit manual category certification or degree eligibility.

COT3100 and EGN4450 are mathematics based on their actual descriptions; computing orientation is not programming. PHY lecture/lab concurrent/drop conditions and credit exclusions remain distinct. EGN4450's printed calculus conjunction is preserved; permissions and minimum grades are not waived. All normalized credit units remain unknown. Source summaries/hashes and21 tests with actual permitted caches accompany the helper; raw copyrighted pages remain ignored. See [course review](../../../research/degree-audit/usf-course-content-review.md).

This closes accessible represented course content, not definitive degree roles or elective eligibility. Primary remains in progress during the remaining independently public college/university policy review. Exact catalog HTTP202 and brochure robots-disallow boundaries remain unchanged; no restricted route was retried.

2026-10-11 public entry/progression follow-up: see [ENTRY_PROGRESSION_REVIEW.md](ENTRY_PROGRESSION_REVIEW.md). AI-specific entry, transfer allocation and manually read Policy 10-505 conditions now mapped. Neighboring majors' requirements and admission-only grade rules are not imposed on every AI student. Public GE pool and full manual graph review remain in progress.

2026-10-11 general-education closure: [GE_COURSE_REVIEW.md](GE_COURSE_REVIEW.md) documents the 152-course/158-designation current export, all full course-field readings and the 141 contextual additions. All 170 represented descriptions now have manual dispositions. Current major catalog/brochure restrictions remain the exact primary-audit blockers; the GE reading queue is finished. Raw export/source pages remain private.

## Bounded independent correction — 2026-10-11

A separate reviewer flagged PSY 2012; the coordinator reread its saved public Course Details description. Scientific study of behavior and mental processes is psychology domain knowledge, consistent with Rice PSYC 203, rather than ethics/communication or social interpretation of technology. Classification changes human context→applications without asserting an AI application. Its recorded fixed role is unchanged; that role remains bounded by the inaccessible current major-source limitation. Both course-review manifests and the replay regression now agree. No denied catalog or brochure route was retried.

## Fixed-source available-evidence closure — 2026-10-11

A fresh independent investigation found no readable saved official brochure PDF
or nonempty brochure capture in existing permitted local evidence. The exact
brochure robots denial and catalog HTTP202 were not retried. Fixed/choice roles
remain unverified, with null independent role sets/counts. All 29 original Course
Details descriptions were independently reread (excluding the later 141 GE
additions), supporting the existing subjects without certifying their major roles.
Manual subject subset: foundations4, mathematics6, AI7, systems2, human6,
applications3, other1. No seed or adapter change is justified by these sources.
See [resolution evidence](../../../research/degree-audit/independent-resolution-usf-wm.md)
and the adjacent proposed replacement core rows; shared-ledger application belongs
to the coordinator. A permitted readable governing major table/PDF is the exact
remaining evidence need, not a still-unread course-description queue.
