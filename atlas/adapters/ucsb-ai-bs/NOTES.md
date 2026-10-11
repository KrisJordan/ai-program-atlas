# UCSB AI curriculum

Reviewed 2026-10-10. The parser re-extracts actual HTML course rows and core-area labels, rejecting missing headings. It excludes the sample plan and never replays worksheet additions or manual audits. Worksheet PDF was inspected through the web PDF reader, not redistributed; PDF refresh requires human review until binary extraction is supported.

Only explicit curriculum tables/core areas were parsed; illustrative four-year schedules were excluded. Webpage and 2026–27 worksheet conflict on CMPSC 41 units and upper-division totals. Science approved lists and capstone details remain unresolved.

CMPSC 41: webpage four units versus worksheet five; worksheet sample plan returns to four.

Upper-division subtotal 81 on worksheet does not reconcile with listed rows or webpage 36 core + 36 electives.

Science List A/B approved lists unavailable on inspected pages; worksheet List B allocation blank.

Capstone course, full college policies and ambiguous worksheet department wording need clarification.

Launch is recorded as announced because the source schedules the inaugural class rather than confirms enrollment.

https://ai.cs.ucsb.edu/curriculum
https://ai.cs.ucsb.edu/
https://ai.cs.ucsb.edu/sites/default/files/2026-04/AI%20major%20rqmnts_4.10%20(1).pdf
https://www.cs.ucsb.edu/index.php/happenings/announcement/ucsb-launches-dedicated-website-new-bs-artificial-intelligence-inaugural

## 2026-10-11 policy and current-guide review

The college's current [2026–27 GEAR](https://www.engineering.ucsb.edu/sites/default/files/docs/26-27_GEAR.pdf), linked from its public GEAR Publications page, was fetched with the robots-aware transport and visually reviewed on printed page 16; page 17 is an illustrative schedule. Raw PDF and rendered page remain temporary, not committed.

Page 16 explicitly prints **72 upper-division units** (36 core plus 36 major-field elective units), **8 List A / 12 List B science units**, and **Computer Science** department language for major letter grading. These provide current college evidence for fields that were 81, blank and ambiguous on the April standalone worksheet. The nine-course elective pool and CMPSC 192/196 combined four-unit, GPA≥3 restriction agree. Combined sequence unit values are not assigned to each constituent course. Cross-listed pairs remain one choice despite separate course identifiers.

CMPSC 41 still conflicts: requirements page five, sample plan four, AI website four. Its single credit value is null, not an assumed resolution. No science-list membership or identified capstone course is supplied by this guide. No requirement is inferred from the sample plan or from a different major's science rules.

Public Engineering requirements and grading pages now supply residence, EAP/UCDC exception, three separate GPA tests, entry-writing deadlines, American History routes/overlap, both finite Area A writing pools, D/E/F/G distribution, special designations, overlap, grading and catalog-year rules. The current catalog entry-writing page adds multilingual placement and limits AWPE recognition to transfers from another UC; the broader college wording is preserved as a discrepancy. Historical examination routes do not claim tests are still offered. The lettering rule preserves the source's “120 units, or two-thirds” rather than manufacturing a formula.

`ucsb_policies.py` reads policy headings, validates operative clauses, extracts Area A codes and observed distribution counts; missing/changed policy guards require review. It never supplies an audit or replays the curated PDF. The PDF source has no HTML parser and requires renewed manual review on change.

Remaining: CMPSC 41 disagreement; finite science Lists A/B; capstone identity; approved American History and D/E/F/G/special GE pools; additional progression/transfer policies. The public filtered catalog Area D page returned HTTP 200 with a loading shell (and web reader was unavailable), not an observed empty pool. No login or hidden endpoint was used. Degree remains partial. Course metadata remains incomplete independently of those inventory gaps.

## 2026-10-11 bounded progression, transfer and AHI closure

Reviewed current public college transfer, repeat, MCP, academic-notice and petition pages. The MCP parser extracts all twelve actual threshold values rather than replaying seed numbers. Rules now include community-college 105-unit/lower-division limits, non-UC vs UC GPA treatment, authorized repeats, concurrent-enrollment restrictions, first 16 repeated-unit GPA treatment, entry-specific MCP counts, 12/9-quarter and 215-unit limits, notice/dismissal review, and publicly stated petition conditions. These are policy inventories, not individualized academic advice or private portal access.

A useful qualification: the general transfer page says special-subject writing must be at UCSB, while the more specific petitions page permits **up to two approved UC EAP exceptions**. Its linked public Google Doc was read through the normal browser and exported as a temporary two-page PDF; both pages were visually checked. October2025 guidance adds 1–3 papers, 1,800 words, at least25% of the grade, writing instruction/feedback, supporting documents, non-English eligibility and student-specific approval. No submission, private form or hidden endpoint was used. HTML shell refresh does not claim to re-read this document.

Current GEAR PDF pages13–14 were visually reviewed. All **15 department expressions** in the AHI approved list are mapped with compressed suffix/range notation preserved; the missing separator in Political Science “152 153” is not silently repaired. GEAR expressly includes AP African American Studies3+, completed IGETC substitution for the Engineering GE pattern (not AHI), and letter grading for both Area A courses. It does not establish CalGETC treatment. The independent Writing Program page supplies WRIT1/1E titles, four-unit values and entry restrictions.

AI FAQ establishes that AI transfer admission and current-student changes begin in2028, prohibits CS+AI double majors, and states that the curriculum page contains all requirements. It does not identify the generic capstone. Its career descriptions are tagged career pathways, not assessed learning outcomes. The stale bare academic-notice URL and old writing ELWR path returned404; observed official navigation found the current pages. The writing `/academics` landing page contains obvious template filler, which was excluded.

Remaining blockers: CMPSC41 five/four-unit disagreement; finite AI-specific science ListsA/B; unidentified capstone; D/E/F/G and special-designation approved GE pools previously returned only a catalog loading shell. No renewed shell/robots attempts or assumption that CS science lists apply to AI. Degree remains partial, now with96 requirement nodes; course metadata remains independently incomplete. Next research queue: independently published AI science/capstone clarification if linked publicly, and current public GE exports; UCSD's smaller remaining finite cross-links and college exam-credit charts remain separately queued.
# Cal-GETC bounded discovery — 2026-10-11

Read [current UC systemwide Cal-GETC guidance](https://admission.universityofcalifornia.edu/admission-requirements/transfer-requirements/preparing-to-transfer/general-education-igetc/cal-getc/) through the robots-aware fetcher (HTTP200). It describes the pattern available to CCC entrants from fall2025, full completion before transfer, C-equivalent grading and receiving-college review otherwise. It does not specify UCSB Engineering substitution/remaining-requirement rules. Added a context-only parser and one policy note; applicability remains unresolved, not rejected.

Bounded official-source discovery using UCSB/Engineering with CalGETC and Cal-GETC found the UC-wide page but no verified independent current college decision. Existing GEAR IGETC wording is not automatically extended. No known catalog shell or broken/denied route was retried; no absence inference is made. Current total: 86 course observations / 97 requirement nodes, partial. Other science-list, capstone, GE-pool and CMPSC41 issues remain as documented elsewhere in these notes. Finite pass complete; a specific new official policy lead or institution clarification is needed to close this decision.

## Degree correctness audit — 2026-10-11

See [eight-degree audit](../../../research/degree-audit/west-purdue-wpi.md) and its adjacent per-program JSON ledger. This program is blocked for whole-degree certification by the specific evidence gaps recorded there. Verified role/subject corrections are retained; parser success and prior local curriculum labels are not a completed degree audit. Remaining course-content review work is distinguished from actual source barriers. Independent second pass remains pending.

Corrected CMPSC130A/130B to computing foundations, ECE139/CMPSC41 to mathematics and CMPSC183 to human context, based on exact published content titles. CMPSC41 credit remains null because of the source conflict. Code-only elective observations are other/unclassified, not an elective subject. Partition remains19fixed/65options/2contextual.

### Public department descriptions — 2026-10-11

The independently linked CS department course directory yielded 35 exact-code detail pages, read in full. The helper `ucsb_reviewed_course_content` guards each entire course article, code and title before emitting original summaries, eligibility and native quarter-unit observations. It emits no review certification. These observations preserve the existing 19 fixed / 65 option / 2 contextual source-record partition.

Thirty-three records state four units; CMPSC192 states 1–5 and196 states2–4, so both remain null with explicit ranges. Their course repeat limits do not replace the degree's combined four-unit elective cap. CS132/188 explicitly have no required prerequisites; recommendations remain recommendations. Many undated pages restrict enrollment to CS/CE or other named majors, with some consent routes. The new AI degree is not silently added to those permissions.

CMPSC184 is explicitly Fall2017 and contains only prerequisites, leaving substantive content unclassified. The other34 pages carry no catalog edition. Nine represented CMPSC codes are absent from this directory (1A,25,41,42,135,183,187,189C,189D), not inferred nonexistent. No denied catalog route was retried. The department overview describes conditional nonmajor access and waitlist priority; its undated rules are not assumed an AI-specific waiver.

CMPSC153A and181 explicitly identify ECE153A and181 as the same courses. This batch records those statements in metadata but leaves separate source records until paired ECE sources are independently reviewed. Credit exclusions for other courses are not treated as identity equivalence. CMPSC185 is mixed foundations/human context; generic192/196 topics and historical184 are unclassified. Remaining other-subject descriptions, paired identities and source-version applicability remain accessible research work; existing unit, science-list, capstone, GE and ELWR/CalGETC gaps remain.

The five fixed MATH3A/3B/4A/4B/6A full general descriptions and prerequisites were also read on the independent Mathematics department page. Its undated blocks supply no unit values: the adapter emits no credits and the existing degree-source four-quarter-unit amounts remain. Login-only study resources were not accessed. The public ECE2026–27 schedule was read, but it supplies names/availability and directs prerequisites to the catalog; it is not reciprocal identity or full-description evidence. The paired ECE review remains open, with historical2020–21 sources not silently used as current proof.

### Writing Program course blocks — 2026-10-11

The full lower- and upper-division pages supply25represented descriptions (19upper,6lower, including the2previously reviewed ELWR contexts). Upper105/107/109series explicitly state4units, Writing2/2E/2LK prerequisites, and upper-division standing; the introduction specifies90recorded units and AreaA1. Lower1/2state5units,1E/2E/50/50E4. WRIT50excludes seniors. The2E/50E local entries stateEngineering enrollment but do not independently restate generic2/50requirements; the observation retains that limitation rather than silently merging rules.

WRIT105AI is strategic writing/communication with generativeAI, classifiedhuman context;105CDcombines code and composition, classifiedmixed. Twenty-four other descriptions are human context. WRIT107EP is explicitly formerly109ES, while the degree pool retains bothcodes; no current cross-list or duplicate-credit relation was invented. WRIT109ES has no separate current block and remains an exact legacy-code applicability question. Both pages are undated. Full-page guards cover common series rules as well as individual content. Current partition remains19fixed/65option/2contextual; optionhuman-context rises to23from actual descriptions, not option membership.

Follow-up comparison of both actually read Writing sources exposes a unit conflict: the individual WRIT1 guide says4quarter units while the lower-division overview says5. Neither undated page establishes precedence. Curated WRIT1 credits are therefore null; its contextual rule states the discrepancy. Source-specific parsers still observe4and5respectively. WRIT1Eagrees at4; WRIT2five/2Efour are not this conflict. This corrects the earlier batch's provisional preference for the overview value.

### Alternate current GEAR file — 2026-10-11

The independently surfaced official `/sites/default/files/images/26-27_GEAR.pdf` returned200 under normal robots/HTTP checks. ItsSHA256is693a71da8261577ccfec6b02ebfaa9dd1a69d133b63f9b5c04ca4066754299e5; the previously reviewed docs-path file isebbd053b9b2cb479bc130cd10fb652816963cf9d238a281999fa74b46d32a853. Full-file differences exist, but PDFpages13/14(university/GE),16(AIrequirements),17(illustrativeplan) have identical whitespace-normalized extracted text. AIpages16/17were also rendered and visually read. This branch is closed: no change to the applicable inventory and no resolution of the41unit/science/capstone gaps. CMPSC190AA–ZZ remains the existing open topic criterion, not676invented course records. Slash-coded153A/155rows are described as source choice rows, with identity groups requiring separate evidence.

### English exact-code and access follow-up — 2026-10-11

The independent main English Department site permits normal fetching, unlike the Transcriptions host's robots-disallowed archive (not retried). Full exact-code descriptions were read for ENGL146AI(displayedWinter2021despite its spring-2021URL),146DS(Winter2023), and all three department-listed ENGL197Fall2026topics:Poetry andPainting;NovelThinking;BlackFantastic. All are literary/cultural analysis, not technicalAIcourses inferred from their topics. Historical146AI/DSapplicability remains explicit. ENGL197is variable: its seed summary combines the three observed current topics, while each source parser emits only its own topic note and bounded subject observation, not a universal description. None states units; prerequisites direct toGOLD, so actualprereqs remainnull.

Fall2025ENGL155AIis a distinct observed code and is not substituted for146AIor C-LIT/GER155. RecentFall2025/Winter2026/Spring2026directories do not establish absence of the older exactcodes. Main ME requirements explicitly say individual course sites are nowCanvas; no login accessed. Department-linked public course search cannot be automatically retrieved under normal policy because its robots URL redirects cross-origin to registrarhelp; the redirect was inspected only to identify the barrier, not to bypass it. ComparativeLiterature's public2025–26offeringsPDF remains the next independentlead.

### Current catalog browser closure: Critical AI 155 (2026-10-11)

The GSS department's public courses page linked directly to the 2026–27 catalog
course directory. Ordinary Chrome navigation rendered the actual directory and
course body after its initial loading shell. This was not a denial or a hidden
API workaround. Both [GER155](https://catalog.ucsb.edu/courses/GER%20155/general-aoYks)
and [C LIT155](https://catalog.ucsb.edu/courses/C%20LIT%20155/general-aoYks) were read
in full. They state four units, Area E, and reciprocal same-course statements
naming German155, Comparative Literature155 and ENGL155AI. Their description
centers humanities history/theory and philosophical/political implications of AI;
`human_context` follows the actual content, not the AI title. No prerequisite
field appears, retained unknown rather than asserting unrestricted eligibility.

Both source-code records remain; the verified pair now counts once among options.
The graph has 19 fixed, 64 option and 2 contextual identities, from 86 raw records.
No ENGL146AI/155AI substitution is made. The parser guards the full visible field
block and never emits identity certification or manual taxonomy reviews.

The independently inspected Comparative Literature2025–26 offerings PDF and GSS
2025–26 schedule confirm offerings only; they did not supply full descriptions.
Sixteen exact course codes still need content review. Current catalog browsing
also reopens GE/science/capstone and current-version checks as accessible work;
old raw-shell observations cannot be treated as definitive access barriers.

### Current catalog CS/ECE/ME batch (2026-10-11)

Read the full current degree tree and16full current course records: CMPSC1A,25,
41,42,135,183,187,184,153A,181; ECE139,153A,180,181,186; ME107. These close13
previously unread code descriptions and replace historical/undated evidence for
three others. Current184now has substantive software-development content.
Current41states4units; the GEAR5unit inconsistency remains and curated unitsnull.
ME107is3units, requiresME17or instructor consent, and merely recommendsPSTAT120A.
The parser preserves full published eligibility, including concurrent math for25.

Both current181records expressly allow AI upper-division students and identify
each other as the same course. The required degree row plus reciprocal identity
proof establishes one fixed course, not two choices; both codes are retained.
Reciprocal153Astatements establish one option identity. Current42,139,153Aand180
still list narrower majors despite their AI degree membership; policy applicability
requires follow-up, not an inferred exemption. Counts are20fixed/61options/2context
identities and21/63/2raw observations. Total83identities from86sourcecodes.

The current program tree still refers scienceListsA/Bto the department, with8and12
units; no finite pool was published there. It explicitly requires at least9field
electives, retains the192/196combined4unit/GPA3.0restriction, and displays two opaque
course references where the older worksheet had a sequence. The observedCSdirectory
contains189A/Bbut not189C/D; do not substitute those identities without evidence.
Remaining exact-code description follow-ups:189C,189Dandlegacy109ES. Current versions
for datedEnglish records, other undated metadata, college GE pools and applicable
approval policies remain accessible work.

### Final named-code follow-up (2026-10-11)

The current catalog's exact WRIT109ESrecord was read in full: professional
communication about environmental topics,4units, WRIT2/2E/2LKandupper-division
standing, and no credit afterEnglish109I. It remains separate from107EP: the
Writing Program's "formerly109ES" label does not independently prove identical
current-version course identity. Both published code records remain in the source
pool, with the version relationship explicit.

The ordinary current course-search query `CMPSC189` returns only189Aand189B, both
Senior Computer Systems Project; the fullCSdirectory likewise has those codes.
No189C/Ddescription or explicit renumbering was observed. Combined with the current
degree's two opaque references, this is a precise unresolved identity/source issue,
not permission to substituteA/Bor claim C/Dneverexisted. Current descriptions now
cover84of86represented codes, with their historical/generic limitations retained.
