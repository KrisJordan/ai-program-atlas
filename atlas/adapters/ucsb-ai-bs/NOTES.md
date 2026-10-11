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
