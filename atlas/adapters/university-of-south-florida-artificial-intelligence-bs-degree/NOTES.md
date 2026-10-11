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
