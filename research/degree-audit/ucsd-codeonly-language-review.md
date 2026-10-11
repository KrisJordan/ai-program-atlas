# UCSD: 102 formerly code-only language records

Reviewed on 2026-10-11. This contribution covers the exact assigned 77 Literature, 10 Chinese and 15 Japanese records. It does not cover the primary researcher's 41 LTSP records, change any requirement role, or certify the degree audit.

The reviewer read all 83 applicable current course blocks and their relevant section contexts in the three official 2026–27 chapters. They support **87 description observations**: 71 Literature, one Chinese and 15 Japanese. Four additional records arise from the explicit three-member LTWL 19A-B-C and JAPN 150A-B-C headings. The manual taxonomy judgments are 84 human-context records and three creative-writing application records. Fifteen records retain unknown metadata and an exact-identity disposition. Previously stored identifier-only checks were not treated as content reviews.

## Sources and limits

- [Literature](https://catalog.ucsd.edu/courses/LIT.html): full matched blocks, language/standing sections and current heading inventory. The six absent exact codes are LTCS 50, LTCS 52, LTFR 50, LTGM 50, LTIT 2C and LTKO 130. The current LTKO 130F/130W/130P headings do not establish one generic 130 identity.
- [Chinese Studies](https://catalog.ucsd.edu/courses/CHIN.html): CHIN 160/260 explicitly includes undergraduate CHIN 160. The nine generic pool codes CHIN 10A/10B/10C, 20A/20B/20C and 100A/100B/100C have no exact current heading. Current N/M/D track suffixes encode placement distinctions and cannot be removed. Their catalog titles and the shared placement rule are guarded; this contribution does not claim to review every alternative track's full description.
- [Japanese Studies](https://catalog.ucsd.edu/courses/JAPN.html): all 13 matched headings, covering 15 assigned records, and the shared placement policy. Prior Japanese preparation triggers testing and an oral interview; residence in Japan or Japanese spoken at home triggers the stated placement exam. These are conditional source rules, not universal prior-course requirements.

All three source captures were already available from successful ordinary public-source fetches; exact timestamps, hashes and ignored cache locations are in the JSON manifest. No new network route or restricted source was needed. The 15 remaining gaps are current-catalog identity questions, **not access barriers, evidence of cancellation, or claims that no historical description exists**. Resolving them requires an applicable original pool version or an explicit published mapping. No successor, placement track or graduate companion is selected automatically.

## Preserved distinctions

- Each member of the printed 4-4-4 sequences receives four quarter units, not twelve. Grouped sequence members are not aliases.
- French upper-division standing or consent is retained separately from each course prerequisite and the French language of instruction. Lower-division Greek, Korean, Italian and Russian records do not inherit a previous section's upper-division or graduate rule.
- LTGK 101 requires concurrent upper-division Greek enrollment. Repeat limits, CHIN 160's P/NP-only condition, LTWR 8A/8B's attendance requirement and local placement/AP alternatives remain visible.
- LTEN 30 studies poetry and aesthetic inquiry despite its physics-facing title. Its PHYS 30 cross-list and no-double-credit clause remain notes; no identity group is created here. LTIT 137's LTEU 146 cross-list and combined twelve-unit ceiling are also retained without an identity merge.
- LTWR 8A/8B/8C teach writing craft and production and are classified as applications. Language communication, literary interpretation and cultural analysis are human context; Japanese career vocabulary is not inferred to be business-method content.
- The repeated LTKO 130F label in LTKO 140's prerequisite and the printed LTGM 1C/1CX prerequisite in LTGM 2A are preserved, not silently corrected.
- No catalog page is promoted to a public teaching site or syllabus.

## Integration and verification

`atlas/adapters/ucsd_codeonly_language_reviews.json` contains manual course-specific summaries, judgments, source identities, description digests, prerequisites, conditions and gap dispositions. The paired Python helper emits only course metadata and source dispositions. It validates chapter and edition, complete matched blocks, section placement/eligibility, explicit grouped headings and Chinese track headings. It does not emit manual audit status, review certification, requirement nodes or identity groups.

The primary UCSD owner integrates observations and manual reviews. All existing prefix source IDs are reused; only `...-ltla-courses` needs registration with the same independently fetched Literature chapter provenance. Existing course notes must be merged rather than discarded. All absent records remain unchanged by the metadata observer.

Validation: 12 contribution tests pass, including actual cached chapter replays and mutations to content, units, year, placement and eligibility. A temporary UCSD seed with the 87 observations and manual reviews passes isolated ingest and static build; the temporary database and generated site were removed afterward. The maintained database, primary seed, requirements and audit ledger were not edited.
