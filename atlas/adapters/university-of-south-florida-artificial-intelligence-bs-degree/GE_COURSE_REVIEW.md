# Current USF general-education pools — 2026-10-11

The public Course Inventory search has separate state-core and USF-designated checkboxes for communication, humanities, mathematics, natural sciences and social sciences. Selecting all ten returns their union. Both result pages were read (1–100 and 101–152); the official **Export to excel** download has 152 unique course rows. Each row's designations were checked against its individual current Course Details page, whose description, credit, prerequisite, corequisite, co-prerequisite, restriction and other-information fields were read completely. No hidden endpoint or authentication was used. The export and full descriptions remain in ignored local caches.

| Designation | State core | USF |
| --- | ---: | ---: |
| Communication | 1 | 22 |
| Humanities | 6 | 51 |
| Mathematics | 4 | 18 |
| Natural sciences | 12 | 17 |
| Social sciences | 6 | 21 |

These 158 memberships represent 152 courses, not 158 distinct courses or a student load. Eleven records already existed in the brochure/civic/statistics inventory. The 141 new records remain contextual under note-based pool nodes; existing fixed/option sets remain 24/5, with no claim that the inaccessible current major catalog certifies them. State/USF quotas and conditional overlap rules are separate. MUN 1120 is an approved one-credit humanities course, and many language/calculus records have four credits; neither becomes an automatic three-credit selection.

All 170 represented course descriptions now have manual dispositions: 158 reviewed, 11 mixed and one unclassified orientation course. Categories follow actual subject matter. Examples: CGS 2060 explicitly teaches programming (foundations), ART 2602 teaches Photoshop use (domain applications), PHI 2101 teaches formal logic (mathematics), MAD 2470 combines mathematical cryptography and security methods (mixed), and MUN 1120 is ensemble performance (domain applications). The GE attribute itself does not classify a course.

Course restrictions remain exact. ENC 2251 simultaneously says Graduate Standing and Exclude Graduate. DAN 2100 lists both Majors Only and Non-Majors Only, plus permission. ART 2500C/2602 say Majors Only without identifying a major. CGS 2060 excludes Engineering credit; no assumption is made about Bellini AI applicability. Physics laboratory concurrency/drop and mutually exclusive credit rules, native-language exclusions, placement alternatives and unparenthesized AND/OR wording remain attached. Blank fields remain unknown. Prerequisites do not become new fixed degree courses.

## Repeating the review

`general_education_courses.py` registers the 152 exact public course URLs and rejects changes to complete fields or current attributes. It emits observations, never manual audits. The course manifest contains our short summaries, explicit subject decisions and hashes, not copied catalog descriptions. Existing course reviews are preserved where the source and identity match.

To refresh membership, repeat the ordinary public search and its export, then run:

```sh
uv run python -m atlas.adapters.university-of-south-florida-artificial-intelligence-bs-degree.ge_export '/path/Course Inventory.xlsx'
```

This validates export headings and returns factual designation rows for manual review; it does not update the DB, infer a catalog year absent from the file, or use undocumented endpoints. Confirm the catalog-year banner on the actual result page. No public pool endpoint is invented. Empty exports, duplicate identities and unexpected attributes fail instead of erasing data.

## Remaining bounded degree blockers

The current major catalog remains unreadable at its documented HTTP-202 destination, and current brochure reinspection is robots-disallowed. The older 24-prescribed/five-choice inventory is retained but cannot be freshly certified, nor can an exact major elective pool, major-wide grade rule or full credit scope be supplied by these general-education descriptions. The primary audit is now **blocked** on those named source boundaries; the previously accessible GE reading queue is complete. No full independent second-pass certification is claimed.
