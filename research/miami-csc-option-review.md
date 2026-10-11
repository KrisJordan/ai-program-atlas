# Miami CSC option-description contribution

Reviewed2026-10-11 for the DS/AI BA and BS only. The primary owner retains all degree seeds, requirement graphs and fixed CSC courses. This contribution supplies16 disjoint named options: **115,210,322,329,405,410,411,412,423,431,506,542,543,548,549,550**.

## Actual source review

I read each entire block in the official [Computer Science course directory](https://bulletin.miami.edu/courses-az/csc/). The normal HTTP200 cache was fetched2026-10-11T03:04:20+00:00, with content hash `245d4b1b926857e82c62abcb06b88c8004349e9bb7bd45daa8781cc2f0255cf7`. Its metadata and body are in `.cache/http/3e3f3760a89143d1df61ba64a88785189d7a5a19a1a752d556fb28123c6399e3.*`. The page identifies the2026–2027 bulletin; the generic download interface also retains a2025–2026 PDF label, which was not used as the version of the observed course blocks. No raw HTML is committed or new retrieval time claimed.

`miami_csc_option_reviews.json` contains original descriptions and classification rationales, whole-block hashes, exact names, individual amounts/ranges, literal prerequisite fields, source/version/review metadata and explicit program scopes. All16 matching blocks are present; this bounded subset has no unread or inaccessible course description.

| Subject decision | Codes | Evidence distinction |
|---|---|---|
|Foundations|115,329,410,411,431|Programming or general software design, implementation and verification are the stated content.|
|Systems|322,423|UNIX interfaces/resources and database organization dominate, respectively.|
|AI/ML|542,543|Statistical learning and deep-learning vision methods are explicit.|
|Domain applications|550|The main subject is modeling biological neural systems; machine-learning connections do not establish an AI-methods course.|
|Mixed, retained as other|210,506,548,549|Scientific computing; formal logic with automated reasoning; programming/learning with bioinformatics; and programming with genomic analysis each span substantial subjects.|
|Unclassified, retained as other|405,412|The seminar topics and commercial internship work are unspecified.|

CSC405 is explicitly **one credit**, with the singular heading form. CSC410/411/412 each allow **one to three credits**. Their scalar credits stay null; the range is preserved in the original summaries, manifest and parser's `observed_credit_ranges`. No observed range becomes an assumed three-credit course or a zero. The other12 courses each state three credits.

Prerequisites retain the complete source expression, including CSC115's pre/corequisite and test-score alternatives, the CSC506 expression with no inserted parentheses, and the12-CSC-credit requirement for405/410/411/412. The brief CSC548 block has no labeled prerequisite; null is not a promise of unrestricted enrollment. CSC412 normally requires50 documented internship hours per credit; this is course workload evidence, not a degree-credit conversion.

Both existing degree graphs require CSC410/411/412 projects or internships to be approved as related to data science and AI. That **program-specific eligibility condition remains separate** from the course description and subject classification. This helper neither deletes it nor infers AI content from approved program membership. It does not alter fixed/option roles, cognate membership, elective quantities or prerequisite obligations elsewhere.

## Integration and verification

Register source ID `miami-csc-option-course-catalog` for the official directory, and call `register(pid,sources,parsers)` **after** `miami_fixed_course_reviews.register`. The helper composes an existing same-URL observer, preserving its fields and requirements while rejecting duplicate course identities. Repeated registration is idempotent. It parses singular/plural credit headings and actual prerequisite fields, validates the exact reviewed whole-block hash, and rejects missing, duplicate or changed blocks. It emits no `category_review`, verification date or audit/completeness claim; the primary owner applies reviewed manifest evidence explicitly.

Six focused tests pass: synthetic singular/range cases, literal eligibility handling, source-change failures, nonmutating composition and duplicate rejection, program scope/subject decisions, plus replay against the actual cached directory. No seed, shared national ledger or maintained database was edited. The much larger Miami cognate metadata inventory and whole-degree policy uncertainties remain outside this bounded contribution.
