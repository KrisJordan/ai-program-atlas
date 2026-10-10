# Columbia AI minor — identity-only discovery

On 2026-10-10, directly inspected the official [Columbia College CS bulletin](https://bulletin.columbia.edu/columbia-college/departments-instruction/computer-science/), including its **Minor in Artificial Intelligence** subsection and local six-course description. The source states that students in CS-department majors/minors, including joint offerings listed there, are ineligible for this minor. This is a minor, not a standalone AI degree.

The seed confirms identity only. Curriculum is pending despite preliminary visibility of some requirements: no total credit calculation, catalog edition, launch date or course/outcome extraction is claimed. Full institution inventory remains incomplete. The adapter uses `discovery_common.parse_identity` to require a title heading/link and nearby explicit minor wording; it does not replay seeds or assign fresh verification timestamps. Verified against actual public HTML temporarily held under `/tmp`; repository tests use synthetic content.

Next: extract all six requirement groups and alternatives, resolve the source's repeated IEOR E2000 listing rather than double count, verify course metadata and eligibility rules, determine edition/calendar from explicit sources, and separately inspect Engineering/Barnard applicability. Respect any future access restrictions.
