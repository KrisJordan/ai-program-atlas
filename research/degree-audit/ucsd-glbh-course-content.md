# UC San Diego GLBH course-content contribution

Reviewed 2026-10-11. Scope is exactly **26 existing represented targets** from `/tmp/ucsd-glbh-targets.json`. This contribution edits only its helper, manifest, tests and evidence note. No seed, shared observer, requirement, identity group or audit ledger changes are included.

## Evidence and bounded coverage

The observed [official course index](https://catalog.ucsd.edu/front/courses.html) supplies the actual link to the [Global Health chapter](https://catalog.ucsd.edu/courses/GLBH.html). The link’s stale tooltip is not used as identity evidence; the fetched page’s H1 is **Global Health Program**. The normal robots-aware Fetcher returned HTTP 200 at `2026-10-11T08:46:00+00:00`, and the chapter identifies **General Catalog 2026–27**. Raw HTML and provenance remain in `/tmp/ucsd-glbh.html`, `/tmp/ucsd-glbh-source-index.json` and the ignored Fetcher cache. The manifest retains exact source, heading, edition and normalized complete-body hashes, with original short summaries.

All **25 exact matching course blocks** were read in full. **24 are approved for metadata integration: 15 human-context and two applications reviews, six mixed reviews, and one unclassified review.** Seventeen therefore have a reviewed single category. All matched headings print four quarter units, including the held course; no range occurs.

- **GLBH 131:** no exact current Climate Resilience heading; no alternate identifier, cancellation or institution-wide absence is inferred.
- **GLBH 107:** current *Health of Refugees and Displaced Populations in Local and Global Contexts* expands the listed *Refugee Health in Local and Global Contexts*. The current body is reviewed, but this population/title expansion remains a conservative version hold. Its current human-context candidate must not certify the unresolved older record or transfer its metadata without primary identity review.

The GLBH 130 word-order variation, GLBH 146 article, GLBH 181 plural, GLBH 150B expanded program subtitle, punctuation and parenthetical cross-list labels remain documented rather than treated as substantive conflicts. No target uses a shared heading or a graduate-section eligibility rule.

## Actual-content decisions

- **Applications:** GLBH 111 explicitly involves clinic-based field experience and learning evidence-based care delivery. GLBH 141 takes clinicians’ perspectives and the translation of epidemiological knowledge into treatment. These specific objectives establish applied health content without classification from the GLBH prefix.
- **Human context:** GLBH 103/105/108/109/114/130 address institutions, inequality, colonialism, policy and cultural context. GLBH 104 is ethical/humanities inquiry; 129 religious/ritual healing; 139 historical and cultural institutions of Native American health; 147 culture and human values in environmental health; 148 medical anthropology; 150 cultural shaping of mental illness; 160 policy/law/governance. GLBH 113 expressly emphasizes social, economic, environmental, behavioral and political determinants of women’s health. These descriptions do not specify a coequal clinical-method curriculum.
- **GLBH 108S, human context:** the Indigenous Futures field school centers ethical research partnership and historical distrust. Genomic studies are the context; the actual text does not describe sequencing, laboratory or computational-genomics training.
- **Mixed:** GLBH 120 integrates health/environmental sciences, Indigenous knowledge and community building; 121 combines biosocial policy with diagnostic/treatment practices and health interventions; 106 combines water-safety testing and technologies with social/economic/policy planning; 146 combines a medical-student HIV learning format and observed care across cultural and socioeconomic settings; 171R introduces mental-health research/practice and advocacy against stigma through scholarly analysis; 181 joins disease/ecological frameworks with development and health policy. Application and human-context candidates are retained explicitly rather than splitting credits or forcing one subject.
- **GLBH 150B, unclassified:** preparing a thesis gives a format, not a concrete topic or method. The preceding 150A block was also read and leaves the student’s primary interest unspecified; it does not resolve the subject.

The GLBH cross-listed anthropology courses agree with the existing ANSC reviews at this bounded level: 105/129/139/147/148/150 human context and 146 mixed. No manual identity groups or updates to the ANSC evidence are emitted.

## Prerequisites, fieldwork and source limitations

Only **GLBH 160 and 150B** among the 24 emitted blocks print `Prerequisites:` clauses. The other **22 remain null**, not “none.” The parser does not import prerequisite text from a different source or silently treat the chapter’s silence as a repeal:

- The earlier approved-pool records for GLBH 120/130 list upper-division standing. Their current chapter blocks omit prerequisite clauses. Notes preserve that source difference and expressly avoid a waiver inference.
- GLBH 111’s prior experiential-pool record says “Application process”; the chapter does not describe one. It **does** require crossing the US–Mexico border to attend the Tijuana clinic, allows credit up to three times, and says program/materials fees may apply. Prior upper-division global-health coursework is recommended preparation rather than a stated prerequisite. The old application condition is retained as separate source context.
- GLBH 106 recommends GLBH 20 before enrollment. This is not converted into a mandatory prerequisite. A water-safety test is an explicit practical learning activity.
- GLBH 108 describes an educational setting for Latinx/Hispanic students but does not state an exclusive identity-based enrollment prohibition. GLBH 108S may have program/materials fees.
- GLBH 160 requires upper-division standing. GLBH 150B requires GLBH 150A and department approval. No additional major or grade restriction is inferred from the honors title.
- GLBH 171R’s exact suffix is retained. The block does not explicitly state online delivery, so an R suffix does not generate a delivery claim.

The chapter explicitly cross-lists GLBH 105/129/139/146/147/148/150 with their same-number ANSC records. Corresponding credit exclusions are preserved. GLBH 105’s four-code exclusion also names ANSC 105S and 105GS; it does not independently establish a four-way identity group. GLBH 139 may be coscheduled with ANTH 237/GLBH 245 and GLBH 141 with GLBH 241; coscheduling does not establish identity or import graduate eligibility.

## Guards and focused validation

`ucsd_glbh_reviews.py` provides `parse_observations(html)` and URL-keyed `SOURCE_PARSERS`. It validates chapter identity, edition, exact headings and complete course bodies, including nested and unwrapped text. Changed facts, units, conditions, duplicate headings, held-title evidence or a formerly missing identifier appearing requires renewed review. Password forms are rejected. Only program identity, course metadata and source dispositions are emitted. Manual category reviews remain in the manifest; held candidate analysis is not an old-record content certification.

**14 focused tests passed**, including exact cached replay of all 24 observations and two dispositions. Tests cover source/edition/body changes, null prerequisites versus recommended preparation, prior pool conditions, fieldwork, coscheduling, title holds, domain/mixed/ethical boundaries and no suffix-derived online claim. No full suite, site build, seed or ledger update was performed. Primary integration and resolution of the title/missing-source dispositions remain outstanding.
