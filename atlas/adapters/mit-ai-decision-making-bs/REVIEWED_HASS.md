# MIT HASS subject evidence contribution — 2026-10-11

This contribution owns the **845 existing `mit-ai-hass-*` source records** only. It does not change the degree seed, requirement graph, shared audit ledger, EECS annotations, chart/reference records, GIR records, or source identity groups. The primary MIT researcher integrates approved observations. The full audit remains partial.

## Checkpoint coverage

- **70 records reviewed**, using actual department descriptions rather than membership in a HASS pool.
- **7 records held for identity/version review:** four observations of listed 4.614 *Building Islam* versus current *Introduction to Islamic Architecture*; one 21H.151 *Pre-Modern China* versus *Dynastic China*; two observations of Soviet/post-Soviet titles versus the current Ukraine/Russia subject.
- **2 records held for a source conflict:** Writing About Race appears in two concentration inventories. The WGS directory describes race-writing workshops, but its linked WGS.231 Fall 2026 page repeats WGS.230's girlhood description. Neither description silently replaces the other.
- **766 records remain pending.** Their descriptions and entry conditions have not been fully reviewed; they are not labeled blocked or audited. The manifest enumerates every concrete record without collapsing repeated list observations.

Sources inspected include all seven publicly linked Architecture directory pages (83 class panels), the Fall 2026 Literature page (33 panels), Music (63 displayed panels, including repeats across filters), Theater (31 panels), 20 WGS directory excerpts and the 11 matching full detail pages, and all 16 public History detail links from the current schedule. Only actually matched and read subject evidence has a manual disposition. Counts of displayed panels are not unique courses or reviewed-record counts.

The current History schedule links some detail pages with older term metadata: for example, the Colonialism page says Spring 2026, while the current schedule is Fall 2026. The observer retains the detail's own term; it does not assign Fall 2026 to every linked description. Some pages omit a term. Missing unit and prerequisite fields remain null.

## Material findings and interpretation

- 21L.017 explicitly describes literary/rhetorical study of probability, not a mathematics curriculum. It is human context.
- Studio photography/video/design and practical musicianship are domain studies, not computing foundations merely because digital tools appear. 21M.053 has substantial cultural comparison and musical practice and remains mixed (`other`).
- 4.603's prerequisite field addresses graduate **4.604** only. The undergraduate prerequisite is left unknown, with the exact graduate-qualified field retained separately. Graduate additional-work clauses never become identity merges.
- 21L.607/608 each have six MIT units and may combine after both are completed as **one HASS-H subject**. 21L.613/614, or two differing-content terms of 614, may combine by petition after completion. The records remain distinct; primary requirement mapping must retain these bundle rules.
- 21M.051 excludes students who have completed 21M.150/151/301/302 or can already read music. The Senegalese ensemble uses an audition limit and recommends earlier subjects; recommendations are not prerequisites.
- WGS.277's metadata says “same subject” across undergraduate and graduate entries, while its body says it meets with EC.718 and graduate work differs. No identity group is inferred. Current WGS.301 names 24.137; older HASS list labels include 24.237. Exact labels remain untouched for primary reconciliation.
- MIT's [official subject key](https://catalog.mit.edu/subjects/) expressly defines a numeric triplet's total as its sum. The helper checks that convention before calculating unit totals, preserves the triplet and cites the rule. Arranged or absent amounts stay null.

## Access and missingness

All 21 relevant central catalog department pages were inspected; their course sections were empty. Economics initially disconnected, then succeeded with the same empty section. Ordinary Chrome independently showed the empty Anthropology page. Its explicitly linked PDF likewise contained a heading only. These are **empty public responses, not publisher denials**.

The Economics department's linked `http://student.mit.edu/catalog/m14a.html` was explicitly robots-denied. No denied catalog endpoint was retrieved or bypassed. Public department sites independently supplied the observations above. Architecture syllabi explicitly labeled certificate-protected were not accessed. Catalog emptiness is not a blanket claim that every pending HASS description is unavailable; remaining department/course/version routes still need individual review.

## Reproducibility and guards

`reviewed_hass_subjects.py` contains source-specific observers for Architecture, Literature, History, WGS and performing-arts schedules. They extract observations only. `matched_review` reuses a saved manual decision only when the original listed ID/code/title/source ID, the observed source URL, and the **entire observed payload digest** agree. Changed descriptions, terms, prerequisites and other observed restrictions withdraw the decision. The helper neither rewrites titles nor classifies unseen text.

The JSON contains concise manual summaries, exact listed and observed identities, dates, source specifications, digests, prerequisites, unit evidence, restrictions and explicit pending/held states. Raw captures remain ignored in `/tmp/mit-hass-subjects/`; no raw catalog HTML is committed. Tests cover scope boundaries, changed-evidence rejection, half-term bundle semantics, graduate-only restrictions, source conflicts, unknown values and actual cached-source reruns. The primary adapter must register approved source specifications before integrating metadata.
